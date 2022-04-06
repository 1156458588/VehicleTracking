import time

import pandas as pd
import numpy as np
from tensorflow.keras.utils import timeseries_dataset_from_array
import train_data
from need import get_areas
from model_test import get_model

path_total = 'E:/高速相关数据/2022.3.23/gk3'
channel_list = ['ch1', 'ch2', 'ch3', 'ch4']
# channel_list = ['CH1', 'CH2', 'CH3', 'CH4']  # 处理 几个 通道 的 数据

# 需要 根据 瀑布图 选择 开始 和  结束  的 滑动区块    一分钟的数据 可以滑591次    所以  取值范围 为  [0, 590]
# 滑动窗 开始结束 的 索引  选取 slide_window_start_index*0.1    slide_window_end_index*0.1
slide_window_start_index, slide_window_end_index = 0, 400
bin_name_working_condition = '20220323133300.bin'  # 某个 工况 对应的 bin文件 时间名称     根据 名称  找索引

save_path = path_total + '/'  # 保存 csv 格式 数据 的 路径  每个工况数据保存一次

# (4, num_bin)  选取 最大 传感器数量  作为 基准    标准化  四个通道  数据形状
bin_files, sensor_num_max = train_data.get_bin_absolute_path(path_total, channel_list, mode='max')
bin_name_channel = [bin_file_path.split('/')[-1].split('_')[-1] for bin_file_path in bin_files[0]]
bin_index = bin_name_channel.index(bin_name_working_condition)
num_bin = bin_files.shape[1]  # 每个通道 的 bin 文件个数
print(f'每个通道有{num_bin}个bin文件')
print(f'当前选择索引为{bin_index}的bin文件')

if __name__ == '__main__':
    total_data = np.zeros(shape=(1, 7))

    bin_one_minute = bin_files[:, bin_index]  # 4个通道 某一分钟 的 bin 文件 （绝对路径）
    bin_name_minute = bin_one_minute[0].split('/')[-1].split('_')[-1]

    print('-' * 50)
    data_one_minute = train_data.get_one_minute_data(bin_one_minute, sensor_num_max, mode='max',
                                                     sample_fre=get_areas.sampleFre)
    print(f'{len(bin_one_minute)}个通道的{bin_name_minute}文件加载完毕！！')
    print(data_one_minute.shape)  # (4, sensor_num_max, 60000)

    slide_window_total_data = []  # 4 个通道 总的 滑窗 数据
    for channel_data in data_one_minute:
        channel_data = channel_data.T  # 转置  axis 0 变为 时间 维度  模拟滑窗   (60000, sensor_num_max)
        dataset = timeseries_dataset_from_array(channel_data, None, sequence_length=get_areas.length_frame,
                                                sequence_stride=get_areas.slide_length)
        channel_slide_window_total_data = []
        for batch in dataset:
            channel_slide_window_total_data.append(batch.numpy())  # (128, 1000, 257)  batch_size = 128

        # (total_slide_count, 1000, 257)
        channel_slide_window_total_data = np.concatenate(channel_slide_window_total_data, axis=0)
        slide_window_total_data.append(channel_slide_window_total_data)

    slide_window_total_data = np.array(slide_window_total_data)
    print(slide_window_total_data.shape)  # (4, total_slide_count, 1000, 257)

    model = get_model((None, get_areas.length_frame, 1), num_classes=4, dense_act='softmax',
                      model_path='multi_ep096-val_acc0.969-val_f10.960.h5')
    print(f'模型加载完毕！！！')

    print('*' * 50)
    print(f'开始进行滑窗数据处理！！！  当前最小阈值为{get_areas.min_threshold}')
    start = 0
    slide_second = get_areas.slide_length / get_areas.sampleFre  # 每次 滑动 的 秒数  0.1
    end = get_areas.length_frame / get_areas.sampleFre
    for slide_window in range(slide_window_total_data.shape[1]):
        if slide_window != 0:  # 第二次  才开始 滑动
            start = round(start + slide_second, 1)  # 保留一位小数  消除 不确定尾数带来的影响
            end = round(end + slide_second, 1)
        if slide_window_start_index <= slide_window <= slide_window_end_index:  # 选取11.0-12.0秒内的数据
            print(f'选取{start}-{end}秒内的数据')

            data_frame = slide_window_total_data[:, slide_window, :, :]  # 一帧 原始数据 (4, 1000, 257)
            areas = get_areas.get_areas(data_frame, model=None)  # 得到 4 个 通道 的 响应区 对象 的 array

            for index, area in enumerate(areas):
                print(f'\033[31m{area.channel}通道上的响应区为{area.area}, 最大响应区（索引）：'
                      f'{area.max_ind_area} 对应的车类别为{area.vehicle_type}\033[0m')

            #     if index == 0:
            #         area_data = np.array([area.channel, area.vehicle_type, area.max_ind_area, area.area[0], area.area[-1],
            #                               area.prob, time.time()+0.1*slide_window])
            #     else:
            #         area_data = np.hstack((area_data, np.array([area.channel, area.vehicle_type, area.max_ind_area, area.area[0], area.area[-1],
            #                                                     area.prob, time.time()+0.1*slide_window])))
            # if len(areas) != 0:
            #     pd.DataFrame(np.expand_dims(area_data, axis=0)).to_csv(
            #         save_path + '_' + bin_name_minute + '.csv', mode='a', header=False, index=False, encoding='utf_8_sig')


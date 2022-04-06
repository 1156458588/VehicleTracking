import pandas as pd
import numpy as np
from tensorflow.keras.utils import timeseries_dataset_from_array
import train_data
from need import get_areas

path_total = 'E:/高速相关数据/2022.1.13'
channel_list = ['CH1', 'CH2', 'CH3', 'CH4']  # 处理 几个 通道 的 数据

# 需要 根据 瀑布图 选择 开始 和  结束  的 滑动区块    一分钟的数据 可以滑591次    所以  取值范围 为  [0, 590]
# 滑动窗 开始结束 的 索引  选取 slide_window_start_index*0.1    slide_window_end_index*0.1
slide_window_start_index, slide_window_end_index = 174, 210
bin_name_working_condition = '20220113131100.bin'  # 某个 工况 对应的 bin文件 时间名称     根据 名称  找索引

save_path = path_total + '/dataset_raw_' + str(get_areas.length_frame)  # 保存 csv 格式 数据 的 路径  每个工况数据保存一次

# (4, num_bin)  选取 最大 传感器数量  作为 基准    标准化  四个通道  数据形状
bin_files, sensor_num_max = train_data.get_bin_absolute_path(path_total, channel_list, mode='max')
bin_name_channel = [bin_file_path.split('/')[-1].split('_')[-1] for bin_file_path in bin_files[0]]
bin_index = bin_name_channel.index(bin_name_working_condition)
num_bin = bin_files.shape[1]  # 每个通道 的 bin 文件个数
print(f'每个通道有{num_bin}个bin文件')
print(f'当前选择索引为{bin_index}的bin文件')

if __name__ == '__main__':
    total_data = np.zeros(shape=(1, get_areas.length_frame + 1))

    bin_one_minute = bin_files[:, bin_index]  # 4个通道 某一分钟 的 bin 文件 （绝对路径）
    bin_name_minute = bin_one_minute[0].split('/')[-1].split('_')[-1]

    print('-' * 50)
    data_one_minute = train_data.get_one_minute_data(bin_one_minute, sensor_num_max, mode='max',
                                                     sample_fre=get_areas.sampleFre)
    print(f'{len(bin_one_minute)}个通道的{bin_name_minute}文件加载完毕！！')
    print(data_one_minute.shape)  # (4, sensor_num_max, 60000)

    slide_window_total_data = []  # 4 个通道 总的 滑窗 数据  np.lib.stride_tricks.sliding_window_view
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

    print('*' * 50)
    print(f'开始进行滑窗数据处理！！！  当前最小阈值为{get_areas.min_threshold}')  # 最大值的 4.5% - 6.4%
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
            areas = get_areas.get_areas(data_frame)  # 得到 4 个 通道 的 响应区 对象 的 array

            for area in areas:

                label = input(f'\033[31m请输入，{area.channel}通道上的{area.area}的'
                              f'最大响应区（索引）：{area.max_ind_area} 对应的类别'
                              f'（0表示小车，1表示大车，2表示大车伴随，3其他干扰，-1即结束标注保存数据）：\033[0m')
                if label not in ['0', '1', '2', '3', '-1']:
                    label = input(f'\033[32m请重新输入该响应区对应的类别：\033[0m')
                if label == '-1':
                    break
                # 保存 的 键

                max_ind_area_data_frame = data_frame[area.channel][:, area.max_ind_area]
                max_ind_area_data_frame = np.hstack((max_ind_area_data_frame, np.array([int(label)])))  # 按列
                total_data = np.vstack((total_data, max_ind_area_data_frame))  # 按行
            if len(areas) != 0:
                if label == '-1':
                    break

    total_data = np.delete(total_data, 0, axis=0)
    pd.DataFrame(total_data).to_csv(save_path + '_' + bin_name_minute + '.csv', header=False, index=False, mode='a')
    print(f'{bin_name_minute}文件数据已保存完毕！！！！')

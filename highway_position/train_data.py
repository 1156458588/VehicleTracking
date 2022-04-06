import os
import re
import struct

import numpy as np


def get_bin_absolute_path(path_total, channel_list, mode=None):
    """
    获取 传入 通道列表路径下  所有 bin文件 绝对 路径
    :param mode: 'max'  返回 channel_list 中 最大 传感器数量    不传 默认为 None  则返回 最小
    :param path_total: 原始bin文件 所在的 总路径    如： 'E:/高速相关数据/2022.1.13'
    :param channel_list: 处理 几个 通道 的 数据   如 ['CH1', 'CH2', 'CH3', 'CH4']  
    :return:   shape为   (len(channel_list), num_bin) 
    """
    bin_file = []

    for channel in channel_list:
        bin_file.append(
            [path_total + '/' + channel + '/' + filename for filename in os.listdir(os.path.join(path_total, channel))])
    bin_file = np.array(bin_file)  # (4, num_bin)

    # num_bin = bin_file.shape[1]  # 每个通道 的 bin 文件个数
    sensor_num_list = sorted(
        [int(re.findall(r'P(\d+)_', bin_path)[0]) for bin_path in bin_file[:, 0]])  # 每个通道 传感器数量 且从小到大排序
    # 选取 最大 或 最小 传感器数量  作为 基准    用于 标准化  四个通道  数据形状

    return bin_file, sensor_num_list[-1 if mode == 'max' else 0]


def get_multi_minute_data(bin_multi_minute, sensor_num_m, sample_fre, mode=None):
    """
    获取 所选通道 多分钟 bin文件 数据   (4, 60000 * 3, sensor_num_m)

    :param bin_multi_minute: 四个通道  几分钟 bin 文件的 绝对路径 列表  (4, 3)  ['xxx/CH1/xxx.bin', 'xxx/CH2/xxx.bin', ...]
    :param sensor_num_m: 所选通道 中 传感器 数量 （最大 或 最小 ）
    :param sample_fre: 采样 频率
    :param mode: 不传 默认为 None  表示 sensor_num_m 取 最小值   为 'max' 时 表示  sensor_num_m 取 最大值 （配套使用）
    :return:
    """
    data_multi_minute = []
    for minute in range(bin_multi_minute.shape[1]):
        data_one_minute = []  # 4个通道 同一分钟的 数据  (4, 60000, sensor_num_m)
        bin_one_minute = bin_multi_minute[:, minute]  # 同一分钟的 bin 文件

        for bin_one_minute_ch in bin_one_minute:
            sensor_num = int(re.findall(r'P(\d+)_', bin_one_minute_ch)[0])  # 每个通道 传感器 个数 不一

            with open(bin_one_minute_ch, 'rb') as f:
                data_one_minute_ch = f.read()  # 读入 一个bin 文件 所有字节 数据

            # 将字节数据 解包成 一维元组  是 按 同一时刻所有传感器的值 顺序存储的
            # 一个float等于四个字节，所以是 len(fout) // 4 个float
            data_raw = struct.unpack('f' * (len(data_one_minute_ch) // 4), data_one_minute_ch)
            data = np.array(data_raw).reshape((-1, sensor_num))

            data_standard = np.zeros(shape=(60 * sample_fre, sensor_num_m))
            if mode == 'max':
                data_standard[:, :sensor_num] = data[:60 * sample_fre, :]
            else:
                # 取 前 sensor_num_min 个 传感器数据
                data_standard = data[:60 * sample_fre, :sensor_num_m]

            data_one_minute.append(data_standard)
        data_multi_minute.append(np.array(data_one_minute))

    return np.concatenate(data_multi_minute, axis=1, dtype=np.float32)

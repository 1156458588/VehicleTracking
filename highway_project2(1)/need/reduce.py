import copy

import numpy as np

from need import get_areas


def sigmoid(data):
    """
    :param data: ndarray类型的数据
    :return:
    """
    return 1 / (1 + np.exp(-data))


def get_clean_data(data_frame, response_weight=True):
    """
    得到 4 个 通道 的  消除干扰 后的 绝对值 数据   各通道测区 已对齐
    :param response_weight: 是否 关注  通道响应  权重 
    :param data_frame: 一帧 原始 数据  shape 为 (4, 200 / 1000 / 60 * 1000 , 257)     有干扰的数据
    :return:
    """
    data_frame_align = []  # 测区 对齐 数据
    # 得到 测区 索引 对齐的 数据
    for channel, channel_data in enumerate(data_frame):
        sta = get_areas.valid_sensor_range[channel][0]
        end = get_areas.valid_sensor_range[channel][1]
        data_frame_align.append(channel_data[:, sta:end])
    data_frame_align = np.array(data_frame_align)

    data_frame_abs = copy.deepcopy(np.abs(data_frame_align)) 
    data_frame_abs_clean = np.zeros(shape=data_frame_abs.shape)  # 存储 消除 干扰 后的 数据
    channel_ = np.arange(len(data_frame_abs))  # 通道 索引

    for channel, channel_data in enumerate(data_frame_abs):
        channel_data_copy = copy.deepcopy(channel_data)  # 深拷贝   防止 循环过程 会 修改原始数据

        channel_disturb_list = np.setdiff1d(channel_, channel)
        for disturb_channel in channel_disturb_list:

            if response_weight:
                ch = data_frame_abs[disturb_channel]  # 某干扰 通道 每个 时刻的最大值   反应 当前 时刻的 响应程度
                ch = sigmoid(ch)  # 得到  该干扰通道  每个时刻 响应 的权重   响应越大 权重越大
            else:
                ch = 1

            channel_data_copy -= (get_areas.channel_disturb_coefficient / np.abs(disturb_channel - channel)) * \
                                 data_frame_abs[disturb_channel] * ch

        channel_data_copy[channel_data_copy < 0] = 0  # 合理赋值

        data_frame_abs_clean[channel] = channel_data_copy

    return data_frame_abs_clean, data_frame_align

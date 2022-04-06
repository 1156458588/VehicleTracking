import numpy as np
from scipy.signal import find_peaks
from need.utils import findSubsequences, Area, get_config, getFFT

config_dict = get_config(config_file='need/config.yml')
valid_sensor_range = config_dict['valid_sensor_range']
min_threshold = config_dict['min_threshold']
max_zero_num = config_dict['max_zero_num']
min_continuous_one_num = config_dict['min_continuous_one_num']
min_area_len = config_dict['min_area_len']
fft_index_threshold = config_dict['fft_index_threshold']
min_threshold_trough, max_threshold_trough = config_dict['min_threshold_trough'], config_dict['max_threshold_trough']
vehicle_type_threshold = config_dict['vehicle_type_threshold']
channel_num = config_dict['channel_num']
channel_disturb_coefficient = config_dict['channel_disturb_coefficient']
sensor_num_max = config_dict['sensor_num_max']
length_frame = config_dict['length_frame']
slide_length = config_dict['slide_length']
length_package = config_dict['length_package']
sampleFre = config_dict['sampleFre']
send_ip = config_dict['send_ip']


def predict_by_model(model, batch_data, areas):
    """
    返回 经过 二分类模型 筛选 后 是 车的响应区
    :param model:
    :param batch_data:
    :param areas:
    :return:
    """
    if model:
        if len(batch_data) != 0:  # 至少存在 一个 响应区
            batch_data = np.expand_dims(np.array(batch_data), axis=2)
            pred = model(batch_data).numpy()  # (b, 2)
            ind = np.nonzero(pred.argmax(axis=1))[0]  # (b) -> 标签为1对应的索引 array
            areas = np.array(areas)[ind]

    return np.array(areas)


def get_areas_channel(channel_data_frame, channel, model=None):
    """
    单个  通道 的 响应区 对象列表
    :param channel: 通道号
    :param model: 加载最优权重后的 模型     默认为None  返回 未经过 模型判断的 响应区 对象 列表
    :param channel_data_frame: 单通道 一帧 原始 数据  shape 为 (1000, sensor_num)  不同 通道 sensor_num  不一样
    :return:
    """
    channel_data_frame_abs = np.abs(channel_data_frame)  # 一帧数据（绝对值）

    # 每个传感器 在 这一帧长(1000个点) 中的  最大值
    channel_max_data_frame_abs = channel_data_frame_abs.max(axis=0)  # (sensor_num, )

    # 判断 最大值     其 大于 阈值的 位置   置为 1  否则为0
    channel_mask = np.where(channel_max_data_frame_abs > min_threshold, 1, 0)

    areas = []
    batch_data = []

    # 得到 当前通道  所有 1   的 索引    也即 响应 传感器  有响应 的 位置    可能有 0 个 或 1 个 或 多个 响应区
    indices_one = np.asarray(np.nonzero(channel_mask)[0], dtype=np.short)

    channel_area_indices = _get_initial_channel_area_indices(indices_one)
    # print('')
    # print('#' * 60)
    # print(f'{channel}通道，初步筛选后的响应区（索引）\n{channel_area_indices}')

    if len(channel_area_indices) != 0:  # 初步 的响应区 不为 空

        if min_area_len < 100:
            channel_area_indices = _get_finally_channel_area_indices_v2(channel_area_indices,
                                                                        channel_data_frame_abs)
            # print(f'{channel}通道，划分 多辆车 后的  最终 响应区（索引）\n{channel_area_indices}')

        for channel_area in channel_area_indices:  # 对 每个 响应区
            # 当前 响应区 最大值 对应  测区/索引
            max_ind_area = channel_area[channel_max_data_frame_abs[channel_area].argmax()]
            # 先满足  频域 特征
            if getFFT(channel_data_frame[:, max_ind_area]).argmax() <= fft_index_threshold:
                max_ind_area_val = channel_max_data_frame_abs[max_ind_area]
                if max_ind_area_val < vehicle_type_threshold:
                    vehicle_type = 0  # 小车
                else:
                    vehicle_type = 1  # 大车
                if len(valid_sensor_range) == 0:  # 为空 则为全部测区范围
                    batch_data.append(channel_data_frame[:, max_ind_area])
                    max_ind_area = ((channel_area[0] + channel_area[-1]) // 2 + max_ind_area) // 2
                    areas.append(Area(channel, channel_area, max_ind_area, max_ind_area_val, vehicle_type=vehicle_type))
                else:
                    if valid_sensor_range[channel][0] <= max_ind_area <= valid_sensor_range[channel][1]:
                        batch_data.append(channel_data_frame[:, max_ind_area])
                        max_ind_area = ((channel_area[0] + channel_area[-1]) // 2 + max_ind_area) // 2
                        areas.append(Area(channel, channel_area, max_ind_area, max_ind_area_val, vehicle_type=vehicle_type))

    return predict_by_model(model, batch_data, areas=areas)


def predict_by_multi_model(model, batch_data, areas):
    """
    返回 经过  多分类模型 筛选 后 是  车的响应区
    0表示小车，1表示大车， 2表示大车伴随， 3其他干扰
    :param model:
    :param batch_data:
    :param areas:
    :return:
    """
    if model:
        if len(batch_data) != 0:  # 至少存在 一个 响应区
            batch_data = np.expand_dims(np.array(batch_data), axis=2)
            pred = model(batch_data).numpy()  # (b, 4)
            prob = pred.max(axis=1)  #
            cls = pred.argmax(axis=1)  # (b)  b个数据 对应的 标签类别

            mask = np.logical_or(cls == 0, cls == 1)

            # 筛选后的响应区  和 对应 车类别 及其 可信度
            areas = np.array(areas)[mask]
            cls = cls[mask]
            prob = prob[mask]

            for i in range(len(areas)):
                areas[i].vehicle_type = cls[i]
                areas[i].set_prob(prob[i])

    return np.array(areas)


def get_areas(data_frame, model=None):
    """
    得到 4 个 通道 的 响应区对象列表      用于 离线跑数据
    :param model: 加载最优权重后的 模型     默认为None  返回 未经过 模型判断的 响应区 对象 列表
    :param data_frame: 一帧 原始 数据  shape 为 (4, 1000, 257)
    :return: 
    """
    data_frame_abs = np.abs(data_frame)  # 一帧数据（绝对值）

    # 找出 每个传感器 在 这一帧长(1000个点) 中的  最大值 及其 对应 索引(可选)
    max_data_frame_abs = data_frame_abs.max(axis=1)  # (4, 257)
    print(f'当前这一帧数据中，最大值为{max_data_frame_abs.max()}')
    # 判断 最大值     其 大于 阈值的 位置   置为 1  否则为0
    mask_one = np.where(max_data_frame_abs > min_threshold, 1, 0)

    areas = []  # 存储 4 个 通道 响应区 对象 列表
    batch_data = []  # 批次 数据  (b, 1000)  要一一对应

    # 遍历 每个 通道  得到  连1 响应测区(1 ... 1)
    for channel, channel_mask in enumerate(mask_one):

        # 得到 当前通道  所有 1   的 索引    也即 响应 传感器  有响应 的 位置    可能有 0 个 或 1 个 或 多个 响应区
        indices_one = np.asarray(np.nonzero(channel_mask)[0], dtype=np.short)

        # 初步的 响应区
        channel_area_indices = _get_initial_channel_area_indices(indices_one)
        print('')
        print('#' * 60)
        print(f'{channel}通道，初步筛选后的响应区（索引）\n{channel_area_indices}')

        if len(channel_area_indices) != 0:  # 初步 的响应区 不为 空

            if min_area_len < 100:
                # 一片 连1中 划分 车 后的  最终 响应区 列表
                channel_area_indices = _get_finally_channel_area_indices_v2(channel_area_indices,
                                                                            data_frame_abs[channel])
                print(f'{channel}通道，划分 多辆车 后的  最终 响应区（索引）\n{channel_area_indices}')

            for channel_area in channel_area_indices:  # 对 每个 响应区
                # 当前 响应区 最大值 对应 测区/索引
                max_ind_area = channel_area[max_data_frame_abs[channel][channel_area].argmax()]
                max_ind_area_val = max_data_frame_abs[channel][max_ind_area]
                if len(valid_sensor_range) == 0:  # 为空 则为全部测区范围
                    batch_data.append(data_frame[channel][:, max_ind_area])
                    areas.append(Area(channel, channel_area, max_ind_area, max_ind_area_val))
                else:
                    if valid_sensor_range[channel][0] <= max_ind_area <= valid_sensor_range[channel][1]:
                        batch_data.append(data_frame[channel][:, max_ind_area])
                        areas.append(Area(channel, channel_area, max_ind_area, max_ind_area_val))

    return predict_by_multi_model(model, batch_data, areas=areas)


def _get_initial_channel_area_indices(indices_one):
    """
    得到单通道 上  初步 的 响应区 索引
    :param indices_one: 该通道上 所有 1  的 索引    也即 传感器 有响应 的 位置
    :return: a list of arrays
    """
    # 存储 当前 通道  所有 连1 区域  索引
    channel_area_indices = []
    # 向前 差分  得到  相邻 1 之间  0 的 个数  [2, 1, 0, 0, 0, 0, ]
    zero_num = np.diff(indices_one) - 1  # indices_one 没有元素 或 只有 一个元素时  差分 出来 都是 空的 array   []
    # 找出  大于 max_zero_num 元素 的 索引     也即  响应传感器 出现 断点  的 索引/位置
    indices_more_than = list(np.nonzero(zero_num > max_zero_num)[0] + 1)  # 加一  补上 差分 的 一个    对齐索引

    if len(indices_more_than) == 0:
        channel_area_indices.append(indices_one)
    else:  # 至少 存在一个 断点
        for i, j in zip([0] + indices_more_than, indices_more_than + [None]):
            channel_area_indices.append(indices_one[i:j])

    # 初步 排除 只有单（min_continuous_one_num - 1）个测区 或 为空 的 响应区
    channel_area_indices = [i for i in channel_area_indices if len(i) >= min_continuous_one_num]
    return channel_area_indices


def _get_finally_channel_area_indices_v2(channel_area_indices: list, channel_data_frame_abs):
    """
    得到单通道 上  最终 的 响应区 索引
    :param channel_area_indices:  单通道 上  初步 的 响应区 索引
        [array([44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55], dtype=int64)]
    :param channel_data_frame_abs: 单通道  一帧 绝对值数据     (1000, 257)
    :return: 划分之后 的 响应区 索引
        [array([44, 45, 46, 47, 48, 49, 50], dtype=int64), array([51, 52, 53, 54, 55], dtype=int64)]
    """
    channel_area_indices_ = []  # 存储 未划分 和 划分后 的响应区 索引
    # 进一步 细分 响应区
    for channel_area in channel_area_indices:

        # 当前 响应区 长度 大于 指定的阈值 长度  即 一个区中  可能有几辆车 需要将其响应区 分开
        if len(channel_area) > min_area_len:
            # shape 为 (12, )  得到 归一化 [0, 1] 之间 的 数 据
            sum_area_frame = channel_data_frame_abs[:, channel_area].sum(axis=0) / \
                             channel_data_frame_abs[:, channel_area].sum(axis=0).max()
            # print(f'当前 大于响应区长度阈值 的响应区 {channel_area} 对 {channel_data_frame_abs.shape[0]} 个点求和 归一化后\n{sum_area_frame}')

            # 寻找 满足条件 的 波谷   得到  波谷的 索引 列表
            indices, _ = find_peaks(sum_area_frame * -1)
            if len(indices) == 0:  # 未找到 波谷 不用划分
                channel_area_indices_.append(channel_area)
            else:
                # 去除 无效 波谷 索引
                indices = np.array(
                    [i for i in indices if min_threshold_trough < sum_area_frame[i] < max_threshold_trough])
                if len(indices) == 0:  # 去除后 无波谷 不用划分
                    channel_area_indices_.append(channel_area)
                else:  # 至少 存在 一个 波谷 索引
                    # 需要保留 结尾的元素  先让 索引加1
                    indices = list(indices + 1)
                    for i, j in zip([0] + indices, indices + [None]):
                        # 排除 划分后 只有单（min_continuous_one_num - 1）个测区 或 为空 的 响应区
                        if len(channel_area[i:j]) >= min_continuous_one_num:
                            channel_area_indices_.append(channel_area[i: j])
        else:
            channel_area_indices_.append(channel_area)

    return channel_area_indices_


def _get_finally_channel_area_indices_v1(channel_area_indices: list, channel_indices_max_data_frame):
    """
    通过寻找子序列的方法  得到单通道 上  最终 的 响应区 索引
    :param channel_area_indices:  单通道 上  初步 的 响应区 索引
        [array([45, 46, 47], dtype=int64), array([56, 57, 58, 60, 61, 62], dtype=int64)]
    :param channel_indices_max_data_frame: 该通道 所有测区 最大值  在  这一帧长 中 的 索引
    :return: 划分之后 的 响应区 索引
        [array([45, 46, 47], dtype=int64), array([56, 57, 58], dtype=int64), array([60, 61, 62], dtype=int64)]
    """
    channel_area_indices_ = []  # 存储 未划分 和 划分后 的响应区 索引
    # 进一步 细分 响应区
    for i, channel_area in enumerate(channel_area_indices):

        # 当前 响应区 长度 大于 指定的阈值 长度  即 一个区中  可能有几辆车 需要将其响应区 分开
        if len(channel_area) > min_area_len:
            # channel_area  [90,   91,  93,  94,  95,  97,  98, 100]
            #               [100, 300, 450, 600, 800, 200, 400, 600]
            channel_area_max_inds = list(channel_indices_max_data_frame[channel_area])
            print(f'当前 大于响应区长度阈值 的第{i}个响应区 在这一帧长中对应的最大值索引为\n{channel_area_max_inds}')
            # 根据最大值索引  寻找 最长  递增 或 递减 的 子集  有多少个子集 就有多少辆车
            # [[100, 300, 450, 600, 800], [200, 400, 600]]
            areas_max_inds = findSubsequences(channel_area_max_inds, [])
            print(areas_max_inds)

            if len(areas_max_inds) > 1:  # 确实 有多辆车   将其 都 加入 响应区列表中  并 删除 原来大的响应区
                area_len = 0
                for index, area in enumerate(areas_max_inds):
                    if index == 0:
                        channel_area_indices_.append(channel_area[:len(area)])
                        area_len = len(area)
                    else:
                        channel_area_indices_.append(channel_area[area_len: area_len + len(area)])
                        area_len += len(area)
            else:
                channel_area_indices_.append(channel_area)
        else:
            channel_area_indices_.append(channel_area)

    return channel_area_indices_

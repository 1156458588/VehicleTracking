import numpy as np
from scipy.fft import fft
import yaml


class Area:

    def __init__(self, channel, area, max_ind_area, max_ind_area_val, vehicle_type=None):
        """
        :param channel: 所在通道
        :param area: 响应区 范围 索引
        :param max_ind_area: 最大响应区 索引
        :param max_ind_area_val: 定位点的最大值（绝对值）
        :param vehicle_type: 当前响应区对应车辆类型     0 表示小车   1 表示大车
        """
        self.channel = channel
        self.area = area
        self.max_ind_area = max_ind_area
        self.max_ind_area_val = max_ind_area_val
        self.vehicle_type = vehicle_type

    def set_prob(self, prob):
        self.prob = prob  # 该响应区 的 可信度


def get_config(config_file=None):

    with open(config_file, 'r', encoding='utf-8') as fo:
        dict_yaml = yaml.load(fo.read(), yaml.Loader)

    return dict_yaml


def findSubsequences(channel_area_max_inds: list, res):
    """
    双重 递归  寻找   最长 递增 或 递减  子序列
    :param res: 返回 划分后的 响应区  每个传感器最大值  对应的索引  [[100, 300, 450, 600, 800], [200, 400, 600]]
    :param channel_area_max_inds: 在 1500个点（一帧）中   单通道某个响应区  每个传感器最大值 对应的索引
    如  [100, 300, 450, 600, 800, 200, 400, 600]
    :return:
    """
    ans = []

    def find1(now, last):
        base = now[-1]
        ans.append(base)
        if len(last) != 0:  # 递归 为空时 返回
            if last[0] >= base:  # 当 不满足该条件时  递归 回调
                find1(now + last[:1], last[1:])  # 递归 调用

    def find2(now, last):
        base = now[-1]
        ans.append(base)
        if len(last) != 0:
            if last[0] <= base:
                find2(now + last[:1], last[1:])

    if channel_area_max_inds[1] >= channel_area_max_inds[0]:  # 递增子序列    正向行驶
        find1(channel_area_max_inds[:1], channel_area_max_inds[1:])
    else:  # 若不管  递减子序列    返回 行驶
        first_el = channel_area_max_inds.pop(0)  # 将 首元素 删除 继续判断
        res.append([first_el])
        # find2(channel_area_max_inds[:1], channel_area_max_inds[1:])

    channel_area_max_inds = channel_area_max_inds[len(ans):]
    print(f'子序列为：{ans}')
    if len(ans) != 0:
        res.append(ans)
    print(f'剩下的每个响应区最大值索引为 {channel_area_max_inds}')

    if len(channel_area_max_inds) > 1:  # 至少 有 两个 测区的最大值 索引
        findSubsequences(channel_area_max_inds, res)

    return res


def getFFT(data):
    """
    得到 FFT 后的 单边 归一化 振幅谱
    :param data:某个传感器 原始1500个点的数据   (1500, )
    :return:
    """
    pointNum = len(data)
    fft_y = fft(data)  # 快速傅里叶变换    变换之后的结果数据(复数形式)长度和原始采样信号是一样的
    abs_y = np.abs(fft_y)  # 取复数的绝对值，即复数的模(双边频谱)

    # FFT具有对称性，一般只需要用pointNum的一半， 取前半部分即可
    normalization_y = abs_y / pointNum  # 归一化处理（双边频谱）
    normalization_half_y = normalization_y[range(int(pointNum / 2))]  # 由于对称性，只取一半区间（单边频谱）
    return normalization_half_y


def ZeroCrossingRate(signal):
    """计算短时过零率"""
    wlen = len(signal)
    t = 0
    for i in range(wlen - 1):
        if signal[i] * signal[i + 1] < 0:
            t = t + 1
    rate = t / wlen
    return rate


if __name__ == '__main__':
    # a = [1070, 935, 976, 224, 138, 721, 418, 112, 98]
    #
    # print(findSubsequences(a, []))
    print(get_config(config_file='config.yml'))

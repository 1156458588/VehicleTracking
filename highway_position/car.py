import numpy as np
import scipy
from scipy.signal import peak_widths, peak_prominences


class car:
    scopes = []
    position = 0
    carType = 0
    peakValue = 0
    channel = 0
    length = 0

    def __init__(self, scopes, position, carType, peakValue, channel, length):
        self.carType = carType
        self.scopes = scopes
        self.position = position
        self.peakValue = peakValue
        self.channel = channel
        self.length = length

def getCars(data, threshold, distance, relHeight, channel):
    retCars = []
    data = np.array(data)
    peaks, _ = scipy.signal.find_peaks(data, height=threshold, distance=distance)
    print('peaks = ', peaks)
    # file = open('E:\\'+str(channel)+'通道数据.txt', "a+", 'uft-8')
    # file.write(str(peaks)+'\n')
    # file.close()
    results_half = peak_widths(data, peaks, rel_height=relHeight)
    for i in range(len(peaks)):
        start = int(round(results_half[2][i]))
        end = int(round(results_half[3][i]))
        prominence = peak_prominences(data, peaks)[0][i]
        length = abs(end - start) + 1
        # 车型默认为小车
        carType = 0
        # 小车
        if 10 < prominence < 120 and length < 4:
            carType = 0
        # 大车
        if (prominence > 100 and length > 3) or prominence > 200 or (length > 5 and 80 < prominence < 100):
            carType = 1
        # 底噪
        if (prominence < 20 and length > 3) or prominence < 8 or length > 6:
            continue
        if channel == 1:
            print('asd定位点：', peaks[i], ", 突起度=", prominence, '通道：', channel, '范围:', (end - start + 1))
        retCars.append(car(scopes=[start, end], carType=carType,
                           position=peaks[i],
                           peakValue=data[peaks[i]], channel=channel, length=length))
    return retCars

def is_average_threshold(y):
    average_interval = 40
    predict_value = []
    for i in range(y.shape[0] // average_interval):
        tmp = y[i * average_interval:(i + 1) * average_interval]
        x = np.arange(0, tmp.shape[0], 1)
        # try:
        # 指数拟合
        #     predict_value = []
        #     n = scipy.optimize.curve_fit(lambda t, a, b: a * np.exp(b * t) + np.log(b * t), x, y, p0=(1, 0.1))
        #     for i in x:
        #         predict_value.extend([abs(n[0][0] * np.exp(n[0][1] * i) + np.log(n[0][1] * i))] * 10)
        #     print(n[0][0])
        # except:
        n = scipy.optimize.curve_fit(lambda t, a, b: a + b * t, x, tmp)
        for i in x:
            predict_value.extend([abs(n[0][0] + n[0][1] * i)])
    if y.shape[0] % average_interval != 0:
        tmp = y[(y.shape[0] // average_interval) * average_interval:]
        x = np.arange(0, tmp.shape[0], 1)
        n = scipy.optimize.curve_fit(lambda t, a, b: a + b * t, x, tmp)
        for i in x:
            predict_value.extend([abs(n[0][0] + n[0][1] * i)])
    _threshold = np.average(np.array(predict_value))
    if max(y) / _threshold < 3:  # 全是底噪的时候，每一个底噪之间差距很小
        _threshold = max(y)
    else:
        if max(y) - _threshold < 10:  # 整体很低的时候，防止阈值设置过低引起多点起振
            _threshold = (max(y) + _threshold) / 2
        else:
            _threshold = np.maximum(max(y) / 15, _threshold)
    return _threshold







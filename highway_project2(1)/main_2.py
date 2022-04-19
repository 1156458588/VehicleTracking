import threading
import time

import numpy as np

from car import getCars, is_average_threshold
from need.reduce import get_clean_data
from need import get_areas
from need.ZMQClient import MessageClient
from need.ZMQServer import MessageServer

# from need.model_best import get_model


if __name__ == '__main__':

    # model = get_model((None, get_areas.length_frame, 1), model_path='ep1759-val_acc0.986-val_f10.979.h5')
    # print(f'模型加载完毕！！！')
    package_num = get_areas.length_frame // get_areas.length_package  # 程序开始分析  需要 攒够 的 包 数量

    msg = MessageServer()
    msg_send = MessageClient(ip=get_areas.send_ip)
    t = threading.Thread(target=msg.ReceiveThread, daemon=True)
    t1 = threading.Thread(target=msg_send.SendThread, daemon=True)
    t.start()
    t1.start()

    data_frame = np.zeros(shape=(get_areas.channel_num, get_areas.length_frame, get_areas.sensor_num_max))
    data_frame_ = [[] for _ in range(get_areas.channel_num)]
    mask = [False for _ in range(get_areas.channel_num)]  # 数据 是否 装满 标志

    while 1:
        #  四个通道 均满足条件
        for i in range(get_areas.channel_num):

            if not mask[i] and msg.q[i].qsize() >= package_num:
                print(f'程序 正常运行  {i}通道队列大小：{msg.q[i].qsize()}')
                for _ in range(package_num):
                    # 一个包的数据
                    channel_package_data = msg.q[i].get()
                    dev_ID = channel_package_data[0]
                    timestamp = channel_package_data[2]
                    data_frame_[i].append(channel_package_data[-1])
                data_frame_[i] = np.concatenate(data_frame_[i], axis=0)  # 一帧数据   (length_frame, sensor_num)
                data_frame[i, :, :data_frame_[i].shape[1]] = data_frame_[i]
                mask[i] = True
                data_frame_[i] = []

        if np.all(mask):  # 四个通道数据 都有了 才 开始分析
            data_frame_clean = get_clean_data(data_frame, response_weight=True)  # (4, 200, 230)
            # 单通道 一帧 原始数据 (1000, sensor_num)
            for channel, channel_data_frame in enumerate(data_frame_clean):
                shift = get_areas.valid_sensor_range[channel][0]  # 当前通道 测区索引 偏移量
                # areas = get_areas.get_areas_channel(channel_data_frame, channel, model=None)
                channel_data_frame_sum = channel_data_frame.sum(axis=0)
                tmp = []
                channel_threshold = is_average_threshold(channel_data_frame_sum)
                for i in channel_data_frame_sum:
                    if i >= channel_threshold:
                        tmp.append(i)
                    else:
                        tmp.append(0)
                channel_data_frame_sum = np.array(tmp)
                cars = getCars(channel_data_frame_sum, threshold=channel_threshold,
                               distance=3, relHeight=0.8, channel=channel)
                # if len(cars) > 0 and channel == 3:
                    # file = open('E:\\'+'channel3.txt', "a+", encoding='utf-8')
                    # file.write("***************"+'\n')
                    # for i in range(len(cars)):
                    #     file.write("通道："+str(channel)+",定位："+str(cars[i].position)+",范围："+str(cars[i].scopes)+",峰值："+str(cars[i].peakValue)+'\n')
                    # file.write("***************" +'\n')
                    # file.close()
                if len(cars) == 0:
                    print(f'\033[32m在{timestamp}时间，{channel}通道上无响应区\033[0m')
                    msg_send.PackBag(dev_ID, channel, 0, 0, 0, 0, 0, 0, timestamp)
                else:
                    for car in cars:
                        if channel == 1:
                            print(f'\033[4;31m{car.channel}通道上的响应区为{np.array(car.scopes)+shift}, 最大响应区（索引）：'
                                  f'{car.position+shift} 对应的车类别为{car.carType}\033[0m')
                        msg_send.PackBag(dev_ID, channel, car.position+shift, car.peakValue, car.scopes[0]+shift,
                                         car.scopes[1]+shift, car.carType, len(cars), timestamp)
            mask = [False for _ in range(get_areas.channel_num)]  # 数据分析完成  重新 装配 数据
        else:
            time.sleep(0.005)

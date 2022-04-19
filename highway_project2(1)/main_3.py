import threading
import time

import numpy as np

from car import getCars, is_average_threshold
from need import get_areas
from need.ZMQClient import MessageClient
from need.ZMQServer import MessageServer
from need.reduce import get_clean_data


def is_continuous():
    if not msg.con:
        print(f'当前数据不连续，清空队列中所有数据')
        # 清空 所有队列
        for channel_q in msg.q:
            channel_q.queue.clear()
    msg.con = False
    threading.Timer(60 * 60 * 2, is_continuous).start()


if __name__ == '__main__':

    package_num = get_areas.length_frame // get_areas.length_package  # 程序开始分析  需要 攒够 的 包 数量

    msg = MessageServer()
    msg_send = MessageClient(ip=get_areas.send_ip)
    t = threading.Thread(target=msg.ReceiveThread, daemon=True)
    t1 = threading.Thread(target=msg_send.SendThread, daemon=True)
    t.start()
    t1.start()
    is_continuous()

    data_frame = np.zeros(shape=(get_areas.channel_num, get_areas.length_frame, get_areas.sensor_num_max))
    data_frame_ = [[] for _ in range(get_areas.channel_num)]
    mask = [False for _ in range(get_areas.channel_num)]  # 数据 是否 装满 标志

    while 1:

        if not msg.con:

            while 1:
                # 首先 数据对齐 再开始
                first_package_data = []
                for channel_q in msg.q:  # 取出 每个队列 第一包 数据的时间戳  用于数据对齐
                    first_package_data.append(channel_q.get()[2])

                # print(f'四个通道时间戳为{first_package_data}')
                # 两个通道 以上才需要 考虑 时间 对齐
                if len(first_package_data) > 1:

                    if np.all(np.abs(np.diff(first_package_data)) < get_areas.length_package):
                        print(f'数据已对齐，跳出对齐操作！！！')
                        break
                    print(f'开始对齐数据')
                    base_timestamp = first_package_data[0]  # 以 通道0 时间戳为基线

                    for channel, channel_timestamp in enumerate(first_package_data[1:]):
                        if base_timestamp - channel_timestamp > get_areas.length_package:
                            print(f'{channel + 1}通道 是上一帧的数据 ， 丢弃')
                            msg.q[channel + 1].get()
                        elif base_timestamp - channel_timestamp < -get_areas.length_package:
                            base_package_data = msg.q[0].get()
                            base_timestamp = base_package_data[2]  # 更新基线
                else:
                    break

        # print(f'*'*50)
        #  四个通道 均满足条件
        for i in range(get_areas.channel_num):

            if not mask[i] and msg.q[i].qsize() >= package_num:
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
            # print(f'开始分析数据')
            data_frame_clean = get_clean_data(data_frame, response_weight=True)  # (4, 200, 230)

            for channel, channel_data_frame in enumerate(data_frame_clean):
                shift = get_areas.valid_sensor_range[channel][0]  # 当前通道 测区索引 偏移量

                channel_data_frame_sum = channel_data_frame.sum(axis=0)
                channel_threshold = is_average_threshold(channel_data_frame_sum)
                channel_data_frame_sum[channel_data_frame_sum < channel_threshold] = 0

                cars = getCars(channel_data_frame_sum, threshold=channel_threshold,
                               distance=3, relHeight=0.8, channel=channel)

                if len(cars) == 0:
                    print(f'\033[32m在{timestamp}时间，{channel}通道上无响应区\033[0m')
                    msg_send.PackBag(dev_ID, channel, 0, 0, 0, 0, 0, 0, timestamp)
                else:
                    for car in cars:
                        if car.channel == 1:
                            print(f'\033[4;31m{car.channel}通道上的响应区范围为{np.array(car.scopes) + shift}, '
                                  f'定位点为：{car.position + shift}，车类型为{car.carType}\033[0m')

                        msg_send.PackBag(dev_ID, channel, car.position + shift, car.peakValue, car.scopes[0] + shift,
                                         car.scopes[1] + shift, car.carType, len(cars), timestamp)

            mask = [False for _ in range(get_areas.channel_num)]  # 数据分析完成  重新 装配 数据
        else:
            time.sleep(0.005)

import threading
import time

import numpy as np

from car import getCars, is_average_threshold
from need import get_areas
from need.ZMQClient import MessageClient
from need.ZMQServer import MessageServer
from need.reduce import get_clean_data


def is_continuous():
    global align_again
    if not msg.con:
        print(f'当前数据不连续，清空队列中所有数据')
        # 清空 所有队列
        for channel_q in msg.q:
            channel_q.queue.clear()
        align_again = True
    msg.con = False
    threading.Timer(2, is_continuous).start()  # 2s之内 未收到数据  则判定为不连续  之后重新 收到数据 需要 重新对齐


if __name__ == '__main__':

    process_start = [True for _ in range(get_areas.channel_num)]  # 4个 通道程序启动 标志
    package_num_start = get_areas.length_frame // get_areas.length_package  # 程序启动   需要 攒够 的 包 数量  10
    package_num = get_areas.slide_length // get_areas.length_package  # 滑窗   需要攒够 的 包 数量  2

    align_again = True  # 是否需要重新对齐

    msg = MessageServer()
    msg_send = MessageClient(ip=get_areas.send_ip)
    t = threading.Thread(target=msg.ReceiveThread, daemon=True)
    t1 = threading.Thread(target=msg_send.SendThread, daemon=True)
    t.start()
    t1.start()
    # is_continuous()

    # 一帧数据 容器
    data_frame = np.zeros(shape=(get_areas.channel_num, get_areas.length_frame, get_areas.sensor_num_max))
    data_frame_ = [[] for _ in range(get_areas.channel_num)]
    mask = [False for _ in range(get_areas.channel_num)]  # 数据 是否 装满 标志

    # 滑窗 版本
    while 1:

        # if align_again:
        #
        #     while 1:
        #         # 首先 数据对齐 再开始
        #         first_package_data = []
        #         for channel_q in msg.q:  # 取出 每个队列 第一包 数据的时间戳  用于数据对齐
        #             first_package_data.append(channel_q.get()[2])
        #
        #         print(f'四个通道时间戳为{first_package_data}')
        #         # 两个通道 以上才需要 考虑 时间 对齐
        #         if len(first_package_data) > 1:
        #
        #             if np.all(np.abs(np.diff(first_package_data)) < get_areas.length_package):
        #                 print(f'数据已对齐，跳出对齐操作！！！')
        #                 align_again = False
        #                 break
        #             print(f'开始对齐数据')
        #             base_timestamp = first_package_data[0]  # 以 通道0 时间戳为基线
        #
        #             for channel, channel_timestamp in enumerate(first_package_data[1:]):
        #                 if base_timestamp - channel_timestamp > get_areas.length_package:
        #                     print(f'{channel + 1}通道 是上一帧的数据 ， 丢弃')
        #                     msg.q[channel + 1].get()
        #                 elif base_timestamp - channel_timestamp < -get_areas.length_package:
        #                     base_package_data = msg.q[0].get()
        #                     base_timestamp = base_package_data[2]  # 更新基线
        #         else:
        #             align_again = False
        #             break

        # 对四个通道 进行数据装配
        for i in range(get_areas.channel_num):

            if process_start[i]:  # 程序 启动
                if not mask[i] and msg.q[i].qsize() >= package_num_start:

                    for _ in range(package_num_start):
                        # 一个包的数据
                        channel_package_data = msg.q[i].get()
                        dev_ID = channel_package_data[0]
                        timestamp = channel_package_data[2]
                        data_frame_[i].append(channel_package_data[-1])
                    data_frame_[i] = np.concatenate(data_frame_[i], axis=0)  # 程序启动 第一帧数据   (length_frame, sensor_num)

                    data_frame[i, :, :data_frame_[i].shape[1]] = data_frame_[i]
                    process_start[i] = False
                    mask[i] = True
                    # data_frame_ = []
            else:  # 正常运行

                if not mask[i] and msg.q[i].qsize() >= package_num:
                    data_frame_[i] = data_frame_[i][get_areas.slide_length:]
                    for _ in range(package_num):
                        channel_package_data = msg.q[i].get()
                        dev_ID = channel_package_data[0]
                        timestamp = channel_package_data[2]
                        data_frame_[i] = np.concatenate([data_frame_[i], channel_package_data[-1]], axis=0)

                    data_frame[i, :, :data_frame_[i].shape[1]] = data_frame_[i]
                    mask[i] = True

        if np.all(mask):  # 四个通道数据 都装配完成  才 开始分析
            # 测区对齐后  干净的数据(abs)  及 原始数据
            data_frame_clean, data_frame_align = get_clean_data(data_frame, response_weight=True)  # (4, 200, 230)
            print('shape = ', data_frame.shape)
            for channel, channel_data_frame in enumerate(data_frame_clean):
                shift = get_areas.valid_sensor_range[channel][0]  # 当前通道 测区索引 偏移量
                channel_data_frame_sum = channel_data_frame.sum(axis=0)
                channel_threshold = is_average_threshold(channel_data_frame_sum)
                channel_data_frame_sum[channel_data_frame_sum < channel_threshold] = 0
                channel_data_frame_align = data_frame_align[channel]  # 某通道 对齐 原始 数据 (200, 230)
                # 把这个直接传进去 就行
                cars = getCars(channel_data_frame_sum, threshold=channel_threshold,
                               distance=3, relHeight=0.8, channel=channel, originalData=channel_data_frame_align)

                if len(cars) == 0:
                    print(f'\033[32m在{timestamp}时间，{channel}通道上无响应区\033[0m')
                    msg_send.PackBag(dev_ID, channel, 0, 0, 0, 0, 0, 0, timestamp)
                else:

                    # file = open('E:\\定位信息2.txt', 'a+', encoding='utf-8')
                    # file.writelines('\n')
                    # file.writelines('*************' + '\n')
                    for car in cars:
                        if car.channel == 3 or car.channel == 1 or car.channel == 2:

                            # file.writelines(
                            #     '通道：'+str(car.channel)+'，时间：' + str(timestamp) + ',定位：' + str(car.position + shift) + ',平均值：'+str(car.peakValue)+',车型：'+str(car.carType)+'\n')

                            print(f'\033[4;31m{car.channel}通道上的响应区范围为{np.array(car.scopes) + shift}, '
                                  f'定位点为：{car.position + shift}，车类型为{car.carType}, 平均值为{car.peakValue}\033[0m')

                        msg_send.PackBag(dev_ID, channel, car.position + shift, car.peakValue, car.scopes[0] + shift,
                                         car.scopes[1] + shift, car.carType, len(cars), timestamp)
                    # file.writelines('*************' + '\n')
                    # file.writelines('\n')
                    # file.close()

            mask = [False for _ in range(get_areas.channel_num)]  # 数据分析完成  需要 重新 装配 数据
        else:
            time.sleep(0.005)

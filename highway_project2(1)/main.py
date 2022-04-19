
import threading
import time
import numpy as np
from queue import Queue

from need import get_areas
from need.model_best import get_model
from need.ZMQServer import MessageServer
from need.ZMQClient import MessageClient


process_start = [True for _ in range(get_areas.channel_num)]  # 4个 通道程序启动 标志
queue_list = [Queue(maxsize=1000) for _ in range(get_areas.channel_num)]  # 4个通道 攒包 队列
package_num_start = get_areas.length_frame // get_areas.length_package  # 程序初始化 需要 攒够 的 包 数量  20
package_num = get_areas.slide_length // get_areas.length_package  # 需要攒够 的 包 数量  2    10

# 在一个函数中，对全局变量进行修改的时候，到底是否需要使用 global 进行说明，要看是否对全局变量的执行指向进行了修改。
# 如果修改了执行指向，即让全局变量指向了一个新的地方，那么必须使用 global。
# 如果仅仅是修改了指向的空间中的数据，此时不是必须要使用 global。


def main(channel, channel_data_frame=None):
    if channel_data_frame is None:
        channel_data_frame = []

    print(f'{channel}通道线程 启动！！！')

    while 1:
        if process_start[channel]:  # 程序 启动
            if queue_list[channel].qsize() >= package_num_start:
                print(f'程序 启动  当前通道队列大小：{queue_list[channel].qsize()}')
                for _ in range(package_num_start):
                    channel_package_data = queue_list[channel].get()
                    dev_ID = channel_package_data[0]
                    timestamp = channel_package_data[2]
                    channel_data_frame.append(channel_package_data[-1])
                channel_data_frame = np.concatenate(channel_data_frame, axis=0)  # 初始化 一帧数据
                process_start[channel] = False

                # 单通道 一帧 原始数据 (1000, sensor_num)
                tt2 = time.time()
                areas = get_areas.get_areas_channel(channel_data_frame, channel, model=None)
                print(f'程序启动后第一次得到结果耗时：{time.time() - tt2}')

                if len(areas) == 0:
                    print(f'\033[32m在{timestamp}时间，{channel}通道上无响应区\033[0m')
                    msg_send.PackBag(dev_ID, channel, 0, 0, 0, 0, 0, 0, timestamp)
                else:
                    for area in areas:
                        print(f'\033[4;31m{area.channel}通道上的响应区为{area.area}, 最大响应区（索引）：'
                              f'{area.max_ind_area} 对应的车类别为{area.vehicle_type}\033[0m')
                        msg_send.PackBag(dev_ID, channel, area.max_ind_area, area.max_ind_area_val, area.area[0],
                                         area.area[-1], area.vehicle_type, len(areas), timestamp)


        else:  # 正常运行
            if queue_list[channel].qsize() >= package_num:  # 开始滑窗
                print(f'{threading.current_thread()}线程正常运行 当前通道队列大小：{queue_list[channel].qsize()}')
                channel_data_frame = channel_data_frame[get_areas.slide_length:]
                for _ in range(package_num):
                    channel_package_data = queue_list[channel].get()
                    dev_ID = channel_package_data[0]
                    timestamp = channel_package_data[2]
                    channel_data_frame = np.concatenate([channel_data_frame, channel_package_data[-1]], axis=0)

                tt2 = time.time()  # time.time()得到的是1970年到当前的秒数,单位是秒，不是毫秒
                areas = get_areas.get_areas_channel(channel_data_frame, channel, model=None)
                print(f'{threading.current_thread()}线程 正常运行后得到结果耗时：{time.time() - tt2}')

                if len(areas) == 0:
                    print(f'\033[32m在{timestamp}时间，{channel}通道上无响应区\033[0m')
                    msg_send.PackBag(dev_ID, channel, 0, 0, 0, 0, 0, 0, timestamp)
                else:
                    for area in areas:
                        print(f'\033[4;31m{area.channel}通道上的响应区为{area.area}, 最大响应区（索引）：'
                              f'{area.max_ind_area} 对应的车类别为{area.vehicle_type}\033[0m')
                        msg_send.PackBag(dev_ID, channel, area.max_ind_area, area.max_ind_area_val, area.area[0],
                                         area.area[-1], area.vehicle_type, len(areas), timestamp)


if __name__ == '__main__':

    model = get_model((None, get_areas.length_frame, 1), model_path='ep1759-val_acc0.986-val_f10.979.h5')
    print(f'模型加载完毕！！！')

    msg = MessageServer()
    msg_send = MessageClient(ip=get_areas.send_ip)
    t = threading.Thread(target=msg.ReceiveThread, daemon=True)
    t1 = threading.Thread(target=msg_send.SendThread, daemon=True)
    t.start()
    t1.start()

    # 有 几个 通道 开启 几个进程 监听  对应的 攒包队列      进程 适用 cpu计算密集型任务
    for i in range(get_areas.channel_num):
        t = threading.Thread(target=main, args=(i,), daemon=True)
        t.start()

    while 1:

        time.sleep(0.005)
        data = msg.Dequeue()  # [仪表ID, 通道号, 时间戳, data]    data形状为 (50, sensor_num)
        if data is not None:
            queue_list[data[1]].put(data)  # 将 每包 数据  放至  对应  通道 队列中


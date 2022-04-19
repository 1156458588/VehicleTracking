import threading
import time
import numpy as np
from car import getCars, is_average_threshold
from need import get_areas
from need.ZMQClient import MessageClient
from need.ZMQServer import MessageServer

process_start = [True for _ in range(get_areas.channel_num)]  # 4个 通道程序启动 标志
package_num_start = get_areas.length_frame // get_areas.length_package  # 程序初始化 需要 攒够 的 包 数量  20
package_num = get_areas.slide_length // get_areas.length_package  # 需要攒够 的 包 数量  2    10

# 在一个函数中，对全局变量进行修改的时候，到底是否需要使用 global 进行说明，要看是否对全局变量的执行指向进行了修改。
# 如果修改了执行指向，即让全局变量指向了一个新的地方，那么必须使用 global。
# 如果仅仅是修改了指向的空间中的数据，此时不是必须要使用 global。


if __name__ == '__main__':
    msg = MessageServer()
    msg_send = MessageClient(ip=get_areas.send_ip)
    t = threading.Thread(target=msg.ReceiveThread, daemon=True)
    t1 = threading.Thread(target=msg_send.SendThread, daemon=True)
    t.start()
    t1.start()
    data_frame = [[] for _ in range(get_areas.channel_num)]
    print("frame size = ", len(data_frame[0]))
    writFlag= False
    while 1:
        # 遍历各个通道

        for i in range(get_areas.channel_num):
            if msg.q[i].qsize() >= package_num_start:
                print(f'程序 启动  {i}通道队列大小：{msg.q[i].qsize()}')
                for _ in range(package_num_start):
                    # 一个包的数据
                    channel_package_data = msg.q[i].get()
                    dev_ID = channel_package_data[0]
                    timestamp = channel_package_data[2]
                    data_frame[i].append(channel_package_data[-1])
                data_frame[i] = np.concatenate(data_frame[i], axis=0)  #一帧数据
                # print('第', i, '通道的数据是：', data_frame[i])
                # 单通道 一帧 原始数据 (1000, sensor_num)
                tt2 = time.time()
                print('数据形状：', data_frame[i].shape)
                cars = getCars(np.abs(data_frame[i]).sum(axis=0), threshold=is_average_threshold(np.abs(data_frame[i]).sum(axis=0)), distance=3, relHeight=0.8, channel=i)
                # file = open('E:\\' + '循环跑12.txt', "a+", encoding='utf-8')
                # file.write("" + '\n')
                # file.write("***************" + '\n')
                # if len(cars) > 0:
                #     for j in range(len(cars)):
                #         file.write("通道："+str(i)+",定位："+str(cars[j].position)+",范围："+str(cars[j].scopes)+",峰值："+str(cars[j].peakValue)+'\n')
                # file.write("***************" + '\n')
                # file.write("" + '\n')
                # file.close()
                if len(cars) == 0:
                    print(f'\033[32m在{timestamp}时间，{i}通道上无响应区\033[0m')
                    msg_send.PackBag(dev_ID, i, 0, 0, 0, 0, 0, 0, timestamp)
                else:
                    for car in cars:
                        print(f'\033[4;31m{car.channel}通道上的响应区为{car.scopes}, 最大响应区（索引）：'
                              f'{car.position} 对应的车类别为{car.carType}\033[0m')
                        msg_send.PackBag(dev_ID, i, car.position, car.peakValue, car.scopes[0],
                                         car.scopes[1], car.carType, len(cars), timestamp)
                        print(dev_ID, i, car.position, car.peakValue, car.scopes[0],
                                         car.scopes[1], car.carType, len(cars), timestamp)
                data_frame[i] = []
            else:
                time.sleep(0.005)
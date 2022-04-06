import struct
import threading
import time

import zmq
from queue import Queue


class MessagePublisher(object):
    def __init__(self, port='8030'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:{}".format(port))
        self.q = Queue(maxsize=1000)
        self.sn = 0  # 自增包序号
        self.mile_range = None

    def SendThread(self):
        while True:
            time.sleep(0.05)
            msg = self.Dequeue()
            if msg is not None:
                try:
                    self.socket.send(msg)
                except Exception as e:
                    print(e)

    def ShowState(self):
        print('发送缓冲区大小:' + str(self.q.qsize()))
        threading.Timer(1.5, self.ShowState).start()

    # def PackNoCarBag(self):
    #     num = 0
    #     device_ip = [192, 168, 1, 100]

    def PackBag(self, timestamp, k, v):
        num = len(k)
        device_ip = [192, 168, 1, 100]
        c_time = timestamp
        device_b = struct.pack('BBBB', device_ip[j][0], device_ip[j][1], device_ip[j][2], device_ip[j][3])
        data_pack = struct.pack('i', self.sn) + device_b + struct.pack('qi', c_time, num)
        self.sn = self.sn + 1
        car_num = '鄂A1V21A       '  # 空格凑够16字节
        for i in range(num):
            speed = v[i][6]
            position = v[i][1]
            lane = v[i][0]
            if speed >= 0:
                direction = 0
            else:
                direction = 1
            if position < self.mile_range[lane][0] + 10 or position > self.mile_range[lane][1] - 10:
                edge = 1
            else:
                edge = 0
            single_data = struct.pack('Q', k[i]) + bytes(car_num, encoding='utf8') + struct.pack('b', v[i][4]) + \
                          struct.pack('IIf', v[i][3][0], (v[i][3][1]), abs(v[i][6])) + \
                          struct.pack('b', v[i][0]) + struct.pack('I', v[i][1]) + \
                          struct.pack('bb', edge, direction)
            data_pack = data_pack + single_data
        self.Enqueue(data_pack)

    def Enqueue(self, block):
        # threadLock.acquire()
        if self.q.full():
            self.q.get()
        self.q.put(block)
        # threadLock.release()

    def Dequeue(self):
        # threadLock.acquire()
        if self.q.empty():
            return None
        else:
            return self.q.get()
        # threadLock.release()

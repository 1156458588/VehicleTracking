import struct
import threading
import time

import zmq
from queue import Queue


class MessageClient(object):
    def __init__(self, ip='localhost', port='8030'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.address = "tcp://{}:{}".format(ip, port)
        self.socket.connect(self.address)
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.q = Queue(maxsize=1000)
        self.is_re_build = True
        self.send_state = False
        self.Rebuild()
        self.sn = 0  # 自增包序号

    def SendThread(self):
        while True:
            time.sleep(0.05)
            msg = self.Dequeue()
            if msg is not None:
                try:
                    rec = self.SendMsg(msg)
                    print(rec)
                except Exception as e:
                    print(e)

    def Rebuild(self):
        print('当前发送状态:' + str(self.send_state))
        print('发送缓冲区大小:' + str(self.q.qsize()))
        if self.is_re_build is False:
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.close()
            self.poller.unregister(self.socket)
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(self.address)
            self.poller.register(self.socket, zmq.POLLIN)
            self.is_re_build = True
        threading.Timer(1.5, self.Rebuild).start()

    def SendMsg(self, msg):
        if self.is_re_build:
            print("发送轨迹数据")
            self.socket.send(msg)
            if self.poller.poll(1000):
                resp = self.socket.recv()
                self.send_state = True
            else:
                self.is_re_build = False
                self.send_state = False
                # raise Exception('Server no response.')
            return resp
        else:
            return None

    def PackBag(self, timestamp, k, v):
        num = len(k)
        device_ip = '192.168.1.100   '  # 空格凑够16字节
        c_time = timestamp
        size = 64 * num  # 单个Data尺寸为44
        device_b = bytes(device_ip, encoding="utf8")
        data_pack = struct.pack('i', self.sn) + device_b + struct.pack('qi', c_time, size)
        self.sn = self.sn + 1
        car_num = '鄂A1V21A       '  # 空格凑够16字节
        for i in range(num):
            single_data = bytes(k[i], encoding='utf8') + bytes(car_num, encoding='utf8') + \
                          struct.pack('h', v[i][-3]) + struct.pack('f', abs(v[0][-1])) + struct.pack('h', v[i][0]) + struct.pack('i', v[i][1])
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

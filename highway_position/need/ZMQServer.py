import struct
import threading
from queue import Queue

import numpy as np
import zmq

from need import get_areas


class MessageServer(object):
    def __init__(self, port='8010'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:" + port)
        # 程序启动初始化 四个队列
        self.q = [Queue(maxsize=1000) for _ in range(get_areas.channel_num)]
        self.StateTimer()

    def ReceiveThread(self):
        while 1:
            #  Wait for next request from client
            message = self.socket.recv()
            #  Send reply back to client
            self.socket.send(b"ok")
            # print("Received request: %s" % message)
            shell = message[0:20]
            head_length = struct.calcsize('hhii')
            head = struct.unpack_from('hhii', shell, 0)
            datatime = struct.unpack_from("Q", shell, head_length)[0]
            data = np.frombuffer(message[20:], dtype=np.float32)
            sample = head[3] // head[2]
            data = data.reshape(sample, head[2])
            # timeStamp = datetime.datetime.fromtimestamp(datatime / 1000)
            # time_string = timeStamp.strftime("%Y-%m-%d %H:%M:%S.%f")
            t_data = [head[0], head[1], datatime, data]
            self.Enqueue(t_data)

    def StateTimer(self):
        print('接收缓冲区大小:' + str(self.q[0].qsize()), str(self.q[1].qsize()), str(self.q[2].qsize()), str(self.q[3].qsize()))
        threading.Timer(1.5, self.StateTimer).start()

    def Enqueue(self, item):
        # threadLock.acquire()
        index = item[1]
        if self.q[index].full():
            self.q[index].get()
        self.q[index].put(item)
        # threadLock.release()

    def Dequeue(self, index):
        # threadLock.acquire()
        if self.q[index].empty():
            return None
        else:
            return self.q[index].get()
    # threadLock.release()


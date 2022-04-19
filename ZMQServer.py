import zmq
import struct
from queue import Queue
import threading


class MessageServer(object):
    def __init__(self, port='8020'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:" + port)
        self.q = Queue(maxsize=1000)
        self.StateTimer()

    def ReceiveThread(self):
        while True:
            #  Wait for next request from client
            message = self.socket.recv()
            self.socket.send(b"ok")
            # print("收到定位数据")
            data = struct.unpack('iiifiiiiQ', message)
            # timeStamp = datetime.datetime.fromtimestamp(datatime / 1000)
            # time_string = timeStamp.strftime("%Y-%m-%d %H:%M:%S.%f"
            # if data[1] == 3:
            #     print('datta = ', data)
            self.Enqueue(data)

    def StateTimer(self):
        # print('接收缓冲区大小:' + str(self.q.qsize()))
        threading.Timer(1.5, self.StateTimer).start()

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


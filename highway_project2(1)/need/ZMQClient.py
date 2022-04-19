import struct
import threading
import time

import zmq
from queue import Queue


class MessageClient(object):
    def __init__(self, ip='localhost', port='8020'):
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

    def SendThread(self):
        while 1:
            time.sleep(0.001)
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
            self.socket.send(msg)
            if self.poller.poll(1000):
                resp = self.socket.recv()
                self.send_state = True
            else:
                self.is_re_build = False
                self.send_state = False
                raise Exception('Server no response.')
            return resp
        else:
            return None

    def PackBag(self, dev_id, channel, sensor, value, min_s, max_s, c_type, count, timestamp):
        byte = struct.pack('iiifiiiiQ', dev_id, channel, sensor, value, min_s, max_s, c_type, count, timestamp)
        self.Enqueue(byte)

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

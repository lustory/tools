
import sys

import socket
import traceback
import cv2
from imutils.video import VideoStream
import imagezmq
import threading
import numpy as np
from time import sleep
import simplejpeg

# Helper class implementing an IO deamon thread
class VideoStreamSubscriber:
    """
    订阅视频流地址
    hostname:   视频流的地址，当视频流来自本机时，hostname=localhsot 或127.0.0.1
                当视频流来自局域网其他机器时，hostname=本机内网ip地址。
    port：      传输端口
    is_req_rep: 是否采用request_reply模式，若为是，则接收到消息后须给返回值，否则
                不用返回值。
    dtype:      传输的数据类型是否为buffer，若为是则采用rec_jpg，否则为rec_image
    """


    def __init__(self, hostname, port, is_req_rep=False, dtype="buffer"):
        self.hostname = hostname
        self.port = port
        self.dtype=dtype
        # self.with_msg= with_msg
        self._stop = False
        self._data_ready = threading.Event()
        self._thread = threading.Thread(target=self._run, args=(is_req_rep,))
        self._thread.daemon = True
        self._thread.start()

    def receive(self, timeout=60.0):
        flag = self._data_ready.wait(timeout=timeout)
        if not flag:
            raise TimeoutError(
                "Timeout while reading from subscriber tcp://{}:{}".format(self.hostname, self.port))
        self._data_ready.clear()
        return self._data

    def _run(self, is_req_rep):
        receiver = imagezmq.ImageHub("tcp://{}:{}".format(self.hostname, self.port), REQ_REP=is_req_rep)
        while not self._stop:
            if self.dtype == "buffer":
                self._data = receiver.recv_jpg()
            else:
                self._data = receiver.recv_image()
   
            self._data_ready.set()
            
            if is_req_rep:
                receiver.send_reply(b"ok")

        receiver.close()

    def close(self):
        self._stop = True

# Simulating heavy processing load
def limit_to_2_fps():
    sleep(0.5)
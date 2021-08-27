
#coding:utf-8
import os
import cv2
import time
import numpy as np
import paddlex as pdx
from imutils import resize as im_resize
# from configParser import Config as config
import simplejpeg
import imagezmq
import socket
import itertools
from multiprocessing import Queue
from comm.ImageZMQ.VideoStreamSubscriber import VideoStreamSubscriber
import functools
from threading import Thread, Event
import orjson
from comm.ImageZMQ.utils import send_msg
from .image_utils import *

class POST_PROCESS:
    def __init__(self, maxqsize=1000):
        self.msgqueue = Queue() if maxqsize==0 else Queue(maxsize=maxqsize) 
    
    def _receive_msg(self, hostname, port, is_req_rep=True, timeout=10**5):
        
        receiver = VideoStreamSubscriber(hostname, port, is_req_rep=is_req_rep) 
        print(f"[INFO] start receiving msgs in {'REQ_REP' if is_req_rep else 'pub_sub'} mode ...")

        while True:
            msg, jpg_buffer = receiver.receive(timeout=timeout)
            image = simplejpeg.decode_jpeg(jpg_buffer, colorspace='BGR', fastdct=False, fastupsample=False)
            self.msgqueue.put({"msg":msg, "image":image})
            
    def start_receive(self, hostname, port, is_req_rep=True):
        receive_msg = functools.partial(self._receive_msg, hostname=hostname, port=port, is_req_rep=is_req_rep)
        Thread(target=receive_msg, args=()).start()
    
    def imshow_with_box(self, show_type="jupyter"):
        JS = jimage_show(width=800)
        while True:
            info = self.msgqueue.get()
            boxes, labels, image = info["msg"]["boxes"], info["msg"]["labels"], info["image"]
            image = plot_boxes_on_image(image, boxes, labels)
            if show_type == "jupyter":
                JS.show(image)
    
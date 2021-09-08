
#coding:utf-8
import os
import cv2
import time
import numpy as np
from imutils import resize as im_resize
import simplejpeg
import imagezmq
import socket
import itertools
from multiprocessing import Queue
from comm.ImageZMQ.VideoStreamSubscriber import VideoStreamSubscriber
import functools
from threading import Thread, Event
import orjson
from .image_utils import *
from collections import Counter, deque
from .push_stream import PUSH_STREAM


LABELS = ["RY_RY", "PD_DKM"]
class POST_PROCESS:
    def __init__(self, maxqsize=100, roi_points=[], token=None):
        self.msgqueue = Queue() if maxqsize==0 else Queue(maxsize=maxqsize) 
        self.im_w = None
        self.im_h = None
        self.roi = roi_points # [ [x,y], [x,y]]
        self.has_image_info = False    
        self.token=token
    
    def _receive_msg(self, hostname, port, req_rep=True, token="", timeout=10**5):
        
        receiver = VideoStreamSubscriber(hostname, port, req_rep=req_rep) 
        print(f"[INFO] using {'REQ_REP' if req_rep else 'pub_sub'} mode ...")
        
        while True:
            msg, jpg_buffer = receiver.receive(timeout=timeout)
            if msg["msg"] != token:
                continue
            image = simplejpeg.decode_jpeg(jpg_buffer, colorspace='BGR', fastdct=False, fastupsample=False)

            self.msgqueue.put({"msg":msg, "image":image})
            
            if not self.has_image_info:
                self.im_h, self.im_w = image.shape[:2]
                self.has_image_info = True
            
    def start_receive(self, hostname, port, req_rep=True, token="token"):
        receive_msg = functools.partial(self._receive_msg, hostname=hostname, port=port, req_rep=req_rep, token=token)
        Thread(target=receive_msg, args=()).start()
        
    def imshow_with_logic_decision(self, show_type="jupyter", poolsize=5):
        JS = jimage_show(width=800)
        ry_list, dkm_list = deque(maxlen=poolsize), deque(maxlen=poolsize)
        while True:
            info = self.msgqueue.get()
            boxes, labels, image = info["msg"]["boxes"], info["msg"]["labels"], info["image"]
            
            # main logic
            ry_list.appendleft(1) if "RY" in "".join(labels) else ry_list.appendleft(0) 
            dkm_list.appendleft(1) if "DKM" in "".join(labels) else dkm_list.appendleft(0) 
            
            # when reached the maxlen, the do the rest logic.
            if len(ry_list) >= ry_list.maxlen:
                if (sum(ry_list)/ry_list.maxlen) >= 0.6:
                    textSize = int(image.shape[0]/20)
                    org = (textSize*1, image.shape[0] - 1*textSize)
                    image = put_text(image, "人员进入", org=org, textSize=textSize, color="white", fillColor=(241,147,156))

#             print(labels)
            image = plot_boxes_on_image(image, boxes, labels)
            if show_type == "jupyter":
                JS.show(image)
    
    def imshow_with_box(self, show_type="jupyter"):
        JS = jimage_show(width=800)
        while True:
            info = self.msgqueue.get()
            boxes, labels, image = info["msg"]["boxes"], info["msg"]["labels"], info["image"]
            image = plot_boxes_on_image(image, boxes, labels)
            if show_type == "jupyter":
                JS.show(image)
    

    
    def push_stream(self, ip="localhost", port=1935, stream_name="test1", decision_poolsize=5):
        
        temp = 0
        ry_list, dkm_list = deque(maxlen=decision_poolsize), deque(maxlen=decision_poolsize)
        jinru_list = deque(maxlen=decision_poolsize)
        while True:
            
            info = self.msgqueue.get()
            if temp == 0:
                PS = PUSH_STREAM(ip=ip, port=port, stream_name=stream_name, \
                                     image_width=self.im_w, image_height=self.im_h, fps=4)
                PS.start_prush_rtmp_stream()
                temp = -1
                
                
                
            
            boxes, labels, image = info["msg"]["boxes"], info["msg"]["labels"], info["image"]
            boxes_centers = centerpoint_of_boxes(boxes)
            
            if self.token !="jjj":
                is_in = points_in_polygons(boxes_centers, self.roi)



                # main logic
                ry_list.appendleft(1) if "RY" in "".join(labels) else ry_list.appendleft(0) 
                dkm_list.appendleft(1) if "DKM" in "".join(labels) else dkm_list.appendleft(0) 
                jinru_list.appendleft(1) if is_in == "in" else jinru_list.appendleft(0)
            
            # when reached the maxlen, the do the rest logic.
#             if len(ry_list) >= ry_list.maxlen:
#                 if (sum(ry_list)/ry_list.maxlen) >= 0.6:
#                     textSize = int(image.shape[0]/20)
#                     org = (textSize*1, image.shape[0] - 1*textSize)
#                     image = put_text(image, "人员进入", org=org, textSize=textSize, color="white", fillColor=(241,147,156))
                if len(jinru_list) >= jinru_list.maxlen:
                    if (sum(jinru_list)/jinru_list.maxlen)>=0.6:
                        textSize = int(image.shape[0]/20)
                        org = (textSize*1, image.shape[0] - 1*textSize)
                        image = put_text(image, "禁区闯入", org=org, textSize=textSize, color="white", fillColor=(241,147,156))
            image = plot_roi_on_image(image, self.roi, fill=None, outline="red")
        
            image = plot_boxes_on_image(image, boxes, labels)
            

            PS.image_write(image)

#coding:utf-8
import os
import cv2
import time
import numpy as np
import paddlex as pdx
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
from comm.ImageZMQ.utils import send_msg
from .pinfer_utils import *


class DETECT():
    def __init__(self, model_path="./inference_model", \
                 use_gpu=False, \
                 gpu_mem=100, \
                 gpu_id=0, \
                 confThre=0.5, \
                 label_dict={1:"cat", 2:"dog"},\
                 maxqsize=0):
        
        self.confThre = confThre
        self.label_dict=label_dict
        self.net = pinfer_init_predictor(model_dir=model_path, \
                                              gpu_mem=gpu_mem, \
                                              gpu_id=gpu_id, \
                                              use_gpu=use_gpu)
        
        self.msgqueue = Queue() if maxqsize ==0 else Queue(maxsize=maxqsize) 
            
    def _receive_msgs(self, hostname="192.168.31.100", port=6500, is_req_rep=True, timeout=10**5):

        # dtype=image 表示接受numpy格式的image, buffer表示接收jpeg buffer
        receiver = VideoStreamSubscriber(hostname, port, is_req_rep=is_req_rep) 
        print(f"[INFO] start receiving msgs in {'REQ_REP' if is_req_rep else 'pub_sub'} mode ...")

        while True:
            _, jpg_buffer = receiver.receive(timeout=timeout)
            image = simplejpeg.decode_jpeg(jpg_buffer, colorspace='BGR', fastdct=False, fastupsample=False)

            # input_queue.put({"msg":msg, "image":image})
            self.msgqueue.put(image)
            
    def start_receive(self, hostname, port, is_req_rep=True):
        receive_msg = functools.partial(self._receive_msgs,\
                                        hostname=hostname, \
                                        port=port, \
                                        is_req_rep=is_req_rep)
        Thread(target=receive_msg, args=()).start()
    
    def filter_bboxes(self, det_results, label_dict):
        # cat_id, score, bbox
        boxes_and_labels = [[res[0], res[2:]] for res in det_results if res[1] >= self.confThre]

        boxes, labels = [], []
        for box, label in boxes_and_labels:
            label = self.label_dict[int(label)]
            boxes.append(box), labels.append(label)
        return boxes, labels
    
    def detect(self, image):
        det_results = pinfer_run(self.net, image)
        
        boxes, labels = self.filter_bboxes(det_results)
        return boxes, labels
    
    def acquire_msgs(self, maxsize=50):
    
        if 1 <= self.msgqueue.qsize() <= maxsize:
            images =  [self.msgqueue.get() for i in range(self.msgqueue.qsize())]
        elif self.msgqueue.qsize() > maxsize:
            images =  [self.msgqueue.get() for i in range(maxsize)]
        else:
            images =  [self.msgqueue.get()]
        
        return images
    
    def batch_detect_and_send(self, remote_addr, port, is_req_rep=True, maxsize=50):

        sender = imagezmq.ImageSender(f"tcp://{remote_addr}:{port}")
        
        send_count = 0
        while True:
            t1 = time.time()
            image_list = self.acquire_msgs(maxsize=maxsize)
            t2 = time.time()
            image_results = self.net.predict(map(lambda x:x.copy().astype("float32"), image_list)) 
            os.system("clear")
#             print(f"inference {len(image_list)}: {time.time() - t2:,.2f}", end="  ")
        
            for image, result in zip(image_list, image_results):
                boxes, labels = self.filter_bboxes(result)
                new_msg = {"boxes":boxes, "labels":labels}
                send_msg(sender, image, msg=new_msg, image_quality=90, image_type="buffer", is_req_rep=is_req_rep)

                send_count += 1
                
                print(f"prev step image cached: {self.msgqueue.qsize():,} | image sent: {send_count:,}")
            
#             print(f"all: {time.time() - t1:,.2f}")


    
    def get_roi(self, image, box):
        x, y, w, h = box
        return image[y:y+h, x:x+w]
    
    def round_list(self, input_list):
        return [round(i) for i in input_list]
    
    
    def image_compress(self,image):
        jpg_buffer = simplejpeg.encode_jpeg(image, quality=90, colorspace='BGR', fastdct=False)
        image = simplejpeg.decode_jpeg(jpg_buffer, colorspace='BGR', fastdct=False, fastupsample=False)
        return image
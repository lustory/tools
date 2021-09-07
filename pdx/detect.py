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
from comm.ImageZMQ import VideoStreamSubscriber
import functools
from threading import Thread, Event
import orjson
from comm.ImageZMQ import msgSender


NONE_DETECTED = -1

class DETECT():
    def __init__(self, model_path="./inference_model", use_gpu=False, confThre=0.5, msgCachedSize=0):
        self.confThre = confThre
        self.model_path = model_path
        self.use_gpu = use_gpu
        self.net = pdx.load_model(self.model_path)
        self.msgqueue = Queue() if msgCachedSize ==0 else Queue(maxsize=msgCachedSize) 
            
    def _receive_msgs(self, hostname="192.168.31.100", port=6500, req_rep=True, timeout=10**5):

        # dtype=image 表示接受numpy格式的image, buffer表示接收jpeg buffer
        receiver = VideoStreamSubscriber(hostname, port, req_rep=req_rep) 
        print(f"[INFO] using {'REQ_REP' if req_rep else 'pub_sub'} mode ...")

        while True:
            msg, jpg_buffer = receiver.receive(timeout=timeout)
            image = simplejpeg.decode_jpeg(jpg_buffer, colorspace='BGR', fastdct=False, fastupsample=False)
            self.msgqueue.put({"msg":msg, "image":image})
            
    def start_receive(self, hostname, port, req_rep=True):
        if isinstance(port,list):
            for i in port:
                Thread(target=self._receive_msgs, args=(hostname, i, req_rep)).start()
        else:
            Thread(target=self._receive_msgs, args=(hostname, port, req_rep)).start()
    
    def filter_bboxes(self, det_results):
        boxes_and_labels = [ [self.round_list(res['bbox']), res['category']]  \
                             for res in det_results if res['score'] >= self.confThre ]
        boxes, labels = [], []
        for box, label in boxes_and_labels:
            boxes.append(box), labels.append(label)
        return boxes, labels
    
    def detect(self, image):
        det_results = self.net.predict(image.copy().astype('float32')) 
        boxes, labels = self.filter_bboxes(det_results)
        return boxes, labels
    
    def acquire_msgs(self, maxBatchSize=50):
    
        if 1 <= self.msgqueue.qsize() <= maxBatchSize:
            msgs =  [self.msgqueue.get() for i in range(self.msgqueue.qsize())]
        elif self.msgqueue.qsize() > maxBatchSize:
            msgs =  [self.msgqueue.get() for i in range(maxBatchSize)]
        else:
            msgs =  [self.msgqueue.get()]
        
        msg_list, image_list = [], []
        for msg in msgs:
            msg_list.append(msg["msg"])
            image_list.append(msg["image"])
        return msg_list, image_list
    
    def batch_detect_and_send(self, remote_addr, port, req_rep=True, maxBatchSize=50):
        
        Sender = msgSender(remote_addr, port, image_type="buffer", req_rep=req_rep)
        
        send_count = 0
        while True:
#             t1 = time.time()
            msg_list, image_list = self.acquire_msgs(maxBatchSize=maxBatchSize)
            
            image_results = self.net.predict(map(lambda x:x.copy().astype("float32"), image_list)) 
            
            os.system("clear")
            for msg, image, result in zip(msg_list, image_list, image_results):
#                 t2 = time.time()
                boxes, labels = self.filter_bboxes(result)
                new_msg = {"msg":msg, "boxes":boxes, "labels":labels}
                Sender.send(image, msg=new_msg, image_quality=90)

                send_count += 1
                
                print(f"pending: {self.msgqueue.qsize():,} | sent: {send_count:,}")
#                 print(time.time() -t2)
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
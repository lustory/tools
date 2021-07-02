
#coding:utf-8

import cv2
import time
import numpy as np
import paddlex as pdx
from imutils import resize as im_resize
from configParser import Config as config
import simplejpeg
import imagezmq
import socket

NONE_DETECTED = -1

class BH_detector():
    def __init__(self, model_path="./inference_model", use_gpu=False, inputWdith=512, inputHeight=512, confThre=0.5):
        self.confThre = confThre
        self.model_path = model_path
        self.use_gpu = use_gpu
        self.net = None
        

    def net_init(self):
        if self.net is None:
            self.net = pdx.deploy.Predictor(self.model_path, use_gpu=self.use_gpu)

    def detect(self, image, idx=0):
        self.net_init()

        image = self.image_compress(image)
        
        det_results = self.net.predict(image.copy().astype('float32'))
        
        boxes_and_labels = [ [self.round_list(res['bbox']), res['category_id']]  for res in det_results if res['score'] >= self.confThre ]
        
        if len(boxes_and_labels) == 0:
            return config.NO_P_DETECTED, [0,0,0,0], config.NO_P_DETECTED

        # 对box按照x坐标升序排列
        boxes_and_labels = sorted(boxes_and_labels, key=lambda x:x[0][0])

        box, label = boxes_and_labels[idx]
        ROI = self.get_roi(image, box)
        
#         print(f"Meter type : {METER_LABELS[int(label)]}")
        return ROI, box, label # config.METER_LABELS[label]   
    
    def acquire_msgs(self, input_queue, max_size = 5):
    
        if 1 <= input_queue.qsize() <= max_size:
            images =  [input_queue.get() for i in range(input_queue.qsize())]
        elif input_queue.qsize() > max_size:
            images =  [input_queue.get() for i in range(max_size)]
        else:
            images =  [input_queue.get()]
        
        return images
    
    def batch_detect_and_send(self, input_queue, remote_addr="192.168.31.104", port=6501, is_req_rep=True, max_size=10):
        
        # 模型初始化
        self.net_init()

        ## 消息发送初始化
        pub_host_name = socket.gethostname()
        sender = imagezmq.ImageSender(f"tcp://{remote_addr}:{port}", REQ_REP=is_req_rep)

        while True:
            msg_list = self.acquire_msgs(input_queue, max_size=max_size)
            image_list = [i["image"] for i in msg_list]
            
            image_boxes, image_labels = self.batch_detect(image_list)
            for image, single_image_boxes, single_image_labels in zip(image_list, image_boxes, image_labels):
                if single_image_labels != config.NONE_DETECTED:
                    labels = [ config.LABELS[int(label)] for label in single_image_labels]
                new_msg = [single_image_boxes, labels]
    #             # new_msg = orjson.dumps(new_msg) 

                # # 方式1，传送numpy image
                # sender.send_image_reqrep(new_msg, image)

                # 方式2，传送jpg buffer
                jpg_buffer = simplejpeg.encode_jpeg(image, quality=90, colorspace='BGR', fastdct=False)
                sender.send_jpg_reqrep(new_msg, jpg_buffer)
                

    def batch_detect(self, image_list):
                
        results = self.net.batch_predict(image_list=image_list)

        image_boxes, image_labels = [], []
        # 遍历每张图片的预测结果
        for single_image_results in results:
            
            # temp_boxes, temp_labels记录每张图片的预测结果
            temp_boxes, temp_labels = [], []
            # 单张图片的预测结果
            for result in single_image_results:
                if result["score"] >= self.confThre:
                    temp_boxes.append(self.round_list(result["bbox"]))
                    temp_labels.append(result["category_id"])
                    
            # 若当前图片没有发现目标
            if len(temp_boxes) == 0:
                image_boxes.append(config.NONE_DETECTED)
                image_labels.append(config.NONE_DETECTED)
            else:
                image_boxes.append(temp_boxes)
                image_labels.append(temp_labels)
   
        return image_boxes, image_labels



    
    def get_roi(self, image, box):
        x, y, w, h = box
        return image[y:y+h, x:x+w]
    
    def round_list(self, input_list):
        return [round(i) for i in input_list]
    
    
    def image_compress(self,image):
        jpg_buffer = simplejpeg.encode_jpeg(image, quality=90, colorspace='BGR', fastdct=False)
        image = simplejpeg.decode_jpeg(jpg_buffer, colorspace='BGR', fastdct=False, fastupsample=False)
        return image
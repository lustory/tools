import os
import cv2
import sys
import time
import numpy as np
from itertools import cycle
from threading import Thread, Event
import simplejpeg
from multiprocessing import Queue
import copy
import imutils

 
class webCamVideoStream:
    def __init__(self, video_addr, skip_num=3, retry=10, maxqsize=30, im_w=None, quality=None,  name="webCamera"):
        '''
            video_addr: 输入视频流地址
            skip_num: 跳帧数量
            retry=10: 视频流无法连接时，最大的重连次数
            maxqsize: 最大的缓存帧数量，0表示无限大。maxqsize所起作用是
                      在源头防止因下游处理阻塞导致的帧积压问题，帧积压又会进一步
                      造成下游的图片流延迟。建议该参数设定后保持默认即可。
                      但当下游读帧受其他程序阻塞时，
            im_w: 图像宽度，保持长宽比缩放
            quality: 图片质量。
            name: 进程名
        '''
        
        self.video_addr = video_addr
        self.stream = cv2.VideoCapture(self.video_addr)
        self.retry = retry
        self.stream_init()
        self.readin_cycle_loop = cycle(list(range(skip_num+1)))
        self.name = name
        self.stopped = False
        self.imagedeque = Queue() if maxqsize ==0 else Queue(maxsize=maxqsize) 
        self.im_w = im_w
        self.quality = quality
 
    def start(self):
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self
    
    def update(self):
        while True:
            if self.stopped:
                return 
            self.grabbed, self.frame = self.stream.read()
            if not self.grabbed: 
                self.stream_init()     
                
            if self.quality != None:
                self.frame = self.image_compress(self.frame, self.quality)
                
            if (self.im_w != None) and (self.im_w < self.frame.shape[1]):
                self.frame = imutils.resize(self.frame, width = self.im_w)
                
            self.imagedeque.put(self.frame)
            
            self.skip_frame()
                         
    def skip_frame(self):
        while True:
            if next(self.readin_cycle_loop) != 0:
                self.stream.grab()
            else:
                break
            
    def stream_init(self):
        self.grabbed, self.frame = self.stream.read()
        retry = self.retry
        
        if not self.grabbed:
            print(f"[INFO] webcam reconnectinig ")
            while True:
                self.stream = cv2.VideoCapture(self.video_addr)
                self.grabbed, self.frame = self.stream.read()
                if not self.grabbed:
                    time.sleep(1)
                    retry -= 1
                    assert retry >= 0, print("The input video stream is not available...")
                else:
                    break     
                    
    def image_compress(self, image, quality):
        jpg_buffer = simplejpeg.encode_jpeg(image, quality, colorspace='BGR', fastdct=False)
        image = simplejpeg.decode_jpeg(jpg_buffer, colorspace='BGR', fastdct=False, fastupsample=False)
        return image
    
    def stop(self):
        self.stopped = True
        
    def read(self):
        return self.imagedeque.get()

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#     def frame_cmp(self):
#         if next(self.cmp_cycle_loop) == 0:
#             self.cur_frame = self.frame.copy()
#             if isinstance(self.prev_frame, np.ndarray):
#                 score = self.frame_simi(self.cur_frame[:,:,0], self.prev_frame[:,:,0])
#                 if score <= 0.95:
#                     self.no_motion = False
#                 else:
#                     self.no_motion = True
                
                
#             self.prev_frame = self.cur_frame
     
            
#     def frame_simi(self, img1, img2, hash_type='phash'):
            
#         def hash_score(hash1, hash2):
#             hash_dist = sum([ham_dist(v1, v2) for v1, v2 in zip(hash1[0], hash2[0])])
#             score = 1 - hash_dist / 64
#             return score
        
#         def ham_dist(x, y):
#             """
#             :type x: int
#             :type y: int
#             :rtype: int
#             """
#             return bin(x ^ y).count('1')
        
#         try:
#             h1, h2 = map(cv2.img_hash.pHash, (img1, img2,))
# #             h1, h2 = map(cv2.img_hash.averageHash, (img1, img2,))
#             score = hash_score(h1, h2)
#             return score
#         except Exception as e:
#             print(e)
#             return 0
        
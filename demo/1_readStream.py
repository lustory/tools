import sys
sys.path.append("/home/xjtu/.research/tools")

import os
import socket
import traceback
from time import sleep
import cv2
from imutils.video import VideoStream
import imagezmq
import simplejpeg
from itertools import count
from video.filevideostream import FileVideoStream
from comm.ImageZMQ.utils import send_msg
import imutils
import time
from video.webCameraVideoStream import webCamVideoStream


## 消息发送初始化
port = 6500
is_req_rep = True
remote_addr = "127.0.0.1" 
input_stream = "/home/xjtu/.research/test.mp4"
sender = imagezmq.ImageSender(f"tcp://{remote_addr}:{port}")
print(f"[INFO] starting sending msgs using {'req_rep' if is_req_rep else 'pub_sub'} mode")


webcam = webCamVideoStream(input_stream, skip_num=3, maxqsize=0, im_w=None)
webcam.start()

count = 0
while True:
    image = webcam.read()
    send_msg(sender, image, image_quality=70)
    time.sleep(0.05)
    os.system("clear")
    count += 1
    print(f"{socket.gethostname()} sent frames: {count:,}")
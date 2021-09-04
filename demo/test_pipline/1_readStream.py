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

# 测试视频
# input_stream = "/home/xjtu/.research/test.mp4"

# 测试视频
# input_stream = "/home/xjtu/.research/data/zhongyangbiandiansuo-05.mp4"

# 中央变电所1
input_stream = "rtsp://180.213.214.75:554/rtp/gb_play_34020000001320000021_34020000001320000021" 

# # 中央变电所
# input_stream = "rtsp://180.213.214.75:554/rtp/gb_play_34020000001320000060_34020000001320000060"


sender = imagezmq.ImageSender(f"tcp://{remote_addr}:{port}")
print(f"[INFO] starting sending msgs using {'req_rep' if is_req_rep else 'pub_sub'} mode")

webcam = webCamVideoStream(input_stream, skip_num=3, retry=100000, maxqsize=50, im_w=640, quality=70)
webcam.start()

count = 0
while True:
    image = webcam.read()
    send_msg(sender, image, image_quality=90)
#     time.sleep(0.05)
    os.system("clear")
    count += 1
    print(f"{socket.gethostname()} sent frames: {count:,.2f}")
print(f"{count:,} sent, finished")
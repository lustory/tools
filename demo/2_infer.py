import sys
sys.path.append("/home/xjtu/.research/tools")

import os
import socket
import traceback
from time import sleep
import cv2
import functools
from imutils.video import VideoStream
import imagezmq
import simplejpeg
from itertools import count
from comm.ImageZMQ.utils import receive_msg2queue
from video.filevideostream import FileVideoStream
from comm.ImageZMQ.utils import send_msg
import imutils
import time
from video.webCameraVideoStream import webCamVideoStream
from pdx.detect import DETECT
import warnings
warnings.filterwarnings("ignore")


import multiprocessing as mp
from multiprocessing import Process, Manager,Queue
from video.image_utils import *


# 当消息来自本机时，hostname="localhost" 或 127.0.0.1
# 当消息来自局域网时，hostname=本机的局域网ip
receive_port = 6500
send_port = 6501
REQ_REP = True
hostname = "localhost" 
model_path = "/home/xjtu/.research/models/test_model"


detector = DETECT(model_path=model_path, inputWdith=544, inputHeight=544, confThre=0.5)

detector.start_receive(hostname=hostname, port=receive_port, is_req_rep=REQ_REP)

detector.batch_detect_and_send(remote_addr=hostname, port=send_port)
import sys
sys.path.append("/home/xjtu/.research/tools")

import os
import socket
import traceback
from time import sleep
import cv2
import functools
from imutils.video import VideoStream
from pdx.detect import DETECT
import warnings
warnings.filterwarnings("ignore")


# 当消息来自本机时，hostname="localhost" 或 127.0.0.1
# 当消息来自局域网时，hostname=本机的局域网ip
receive_port = 6000
send_port = 6001
REQ_REP = True
hostname = "127.0.0.1" 
model_path = "/home/xjtu/.research/models/zybds_general_20210830"


detector = DETECT(model_path=model_path, confThre=0.6, maxqsize=0)

detector.start_receive(hostname=hostname, port=receive_port, is_req_rep=REQ_REP)

detector.batch_detect_and_send(remote_addr=hostname, port=send_port, maxsize=20)
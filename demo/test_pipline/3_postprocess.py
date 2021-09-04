import sys
sys.path.append("/home/xjtu/.research/tools")

# import socket
# # import traceback
# import cv2
# from imutils.video import VideoStream
# import imagezmq
# import threading
# import numpy as np
# from time import sleep
# import simplejpeg
# import orjson
# from comm.ImageZMQ.VideoStreamSubscriber import VideoStreamSubscriber
# from multiprocessing import Process,Queue

# from video.filevideostream import FileVideoStream
# import multiprocessing as mp
# from multiprocessing import Process, Manager,Queue
# import time
# from comm.ImageZMQ.utils import receive_msg2queue
# import functools
# from video.image_utils import *

# import multiprocessing as mp
# from multiprocessing import Process, Manager,Queue
# from utils import *
from video.post_process import POST_PROCESS




hostname="127.0.0.1"
port=6501

PP = POST_PROCESS()
PP.start_receive(hostname, port)

PP.push_stream(ip="localhost", port=1935, stream_name="zhongyangbiandiansuo_1", poolsize=5)
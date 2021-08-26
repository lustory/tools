import os
import PIL
from PIL import Image
from io import BytesIO
import simplejpeg
from IPython import display
import ipywidgets as widgets
import cv2
import datetime
from PIL import Image, ImageDraw, ImageFont
import imutils
import numpy as np
import itertools 
import pathlib2 as pathlib
import time



def jcam_show(cam, height=300, width=400):
    imgbox = widgets.Image(format='jpg', height=height, width=width)
    display.display(imgbox)
    cam.start()
    while True:
        image = cam.read()
        imgbox.value = cv2.imencode(".jpg", image)[1].tobytes()
        
class jimage_show:
    def __init__(self, height=300, width=400):
        self.imgbox = widgets.Image(format='jpg', height=height, width=width)
        display.display(self.imgbox)
    

    def show(self, image):
        self.imgbox.value = cv2.imencode(".jpg", image)[1].tobytes()
    

def buffer2image(image_buffer, colorspace="BGR"):
    return simplejpeg.decode_jpeg(image_buffer, colorspace=colorspace, fastdct=False, fastupsample=False)


def stream_info(input_url, max_retry=10):
    
    '''
        input_url: 输入的视频流地址，rtsp或rtmp
        max_retry: 最大尝试获取视频流的次数。
        return: [height, width] 视频流帧的高度和宽度
    '''
    
    cap = cv2.VideoCapture(input_url)
    
    retry_count = 0
    while True:
        ret, frame = cap.read()
        if isinstance(frame, np.ndarray):
            return frame.shape[:2]
        else:
            retry_count += 1
            time.sleep(1)
            if retry_count == max_retry:
                assert retry_count < max_retry, print("The input stream is not available... ")
                return 
            

def camera_shot(prefix="mac",save_image=False):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        if save_image:
            cv2.imwrite(f"./{prefix}_{now()}.jpg", frame)
    return ret, frame


def now():
    return datetime.datetime.now().strftime('%Y%m%d-%H%M%S')


def screen_shot(save_dir="./", prefix="454-desktop", save_image=False):
    try:
        frame = PIL.ImageGrab.grab(all_screens=True)
        frame = cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2BGR)
        if save_image:
            print(f"{os.path.join(save_dir, '_'.join([prefix, now()+'.jpg']) )}")
            cv2.imwrite(f"{os.path.join(save_dir, '_'.join([prefix, now()+'.jpg']) )}", frame)
        return True, frame
    except Exception as e:
        print(e)
        return False, False

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
import functools


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


def plot_boxes_on_image(image, boxes, labels=None, line_width=3, box_color="red", text_color="white", line_ratio=0.3):
    
    if boxes == []:
        return image
    
    image_copy = image.copy()
    boxes = [xywh2xyxy(i) for i in boxes]
        
    plot = functools.partial(plot_one_box, line_width=line_width, box_color=box_color, text_color=text_color, line_ratio=line_ratio)
    
    labels = [labels]*len(boxes) if labels==None else labels
    for box, label in zip(boxes, labels):
        image_copy = plot(image_copy, box, label)

    return image_copy
            

def plot_one_box(image, box, label=None, line_width=3, box_color="lime", text_color="white", line_ratio=0.3):
    '''
        # 使用opencv在image上画出一个box, box=[x,y,x,y]
    '''
    image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    ######### 画矩形框 #########
    draw = ImageDraw.ImageDraw(image)
    # 矩形框参数计算
    [x1,y1,x2,y2] = box
    box_width, box_height = y2-y1, x2-x1
    
    
    # 画矩形框方式1
#     draw.rectangle(((x1, y1),(x2, y2)), fill=None, outline=box_color, width=line_width)  

    # 画矩形框方式2
    plot_hollow_box(draw, box, line_ratio=line_ratio, color=box_color, line_width=line_width)
    
    ######### 画label #########
    if label != None:
        # 将int类型的label转化为字符串
        label = str(label) if isinstance(label, int) else label
        # 单个字的大小 = box宽度的3/4除以字的个数，同时不小于20
        textSize = max(10, int(box_width*3/4/len(label)))
        fontStyle = ImageFont.truetype("/home/xjtu/.research/tools/SimHei.ttf", textSize, encoding="utf-8")
        (text_w, text_h) = draw.textsize(label, fontStyle)
        ## first consider put text on the box, then under the box.
        new_y1 = y1-text_h-line_width if y1-text_h-line_width >=0 else y1 + line_width
        draw.rectangle(((x1, new_y1),(x1+text_w, new_y1+text_h)), fill="blue", outline=None, width=line_width)  
        draw.text((x1,new_y1), label, text_color, font=fontStyle)
        
    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)



def xywh2xyxy(box):
    if isinstance(box[0], int):
        x,y,w,h = box
        return [x,y,x+w,y+h]
    else:
        temp = []
        for [x,y,w,h] in box:
            temp.append([x,y,x+w,y+h])
        return temp
    
def plot_hollow_box(draw, box, line_ratio=0.3, color="springgreen", line_width=3):
    '''
        基于PIL.draw，画出空心box,
        draw: ImageDraw.ImageDraw
        box: [x1,y1,x2,y2]
        line_ratio：实际画出box的长和宽占原本长和宽的比例。
        color: box颜色
        line_width: 线段宽度（像素）        
    '''
    # 矩形框参数计算
    [x1,y1,x2,y2] = box
    box_height, box_width = y2-y1, x2-x1
    x_extend, y_extend = int(box_width*line_ratio), int(box_height*line_ratio)
    
    draw.line((x1,y1, x1+x_extend, y1), color, width=line_width) 
    draw.line((x1,y1, x1, y1+y_extend), color, width=line_width) 
    draw.line((x1,y2, x1+x_extend, y2), color, width=line_width) 
    draw.line((x1,y2, x1, y2-y_extend), color, width=line_width) 
    draw.line((x2,y1, x2-x_extend, y1), color, width=line_width) 
    draw.line((x2,y1, x2, y1+y_extend), color, width=line_width) 
    draw.line((x2,y2, x2-x_extend, y2), color, width=line_width) 
    draw.line((x2,y2, x2, y2-y_extend), color, width=line_width)      
    

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



# 苋菜红  (166,27,41)
# 春梅红 （241,147,156)
# 大鹅紫 （51,20,30)
# COLORS = [(166,27,41),\
#           (241,147,156),\
#           (51,20,30)]

# BGR
COLORS = {"body":"lime", "head":"red"}

def jcam_show(cam, height=300, width=400):
    imgbox = widgets.Image(format='jpg', height=height, width=width)
    display.display(imgbox)
    
    while True:
        image = cam.read()
        imgbox.value = cv2.imencode(".jpg", image)[1].tobytes()
        
        
class Jimage_show:
    def __init__(self, height=300, width=400):
        self.imgbox = widgets.Image(format='jpg', height=height, width=width)
        display.display(self.imgbox)
    

    def show(self, image):
        self.imgbox.value = cv2.imencode(".jpg", image)[1].tobytes()
    

def buffer2image(image_buffer, colorspace="BGR"):
    return simplejpeg.decode_jpeg(image_buffer, colorspace=colorspace, fastdct=False, fastupsample=False)



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


def plot_boxes_on_image(image, boxes, labels=None, box_type="xyxy", line_width=3, box_color="red", textColor="white", line_ratio=0.3):
    image_copy = image.copy()
    if box_type == "xywh":
        boxes = [xywh2xyxy(i) for i in boxes]
        
    if labels != None:
#         # 设定label和box的对应关系
#         labels = labels if labels != None else [None]*len(boxes)
        for index, (box, label) in enumerate(zip(boxes, labels)):
            image_copy = plot_one_box(image_copy, box, label, line_width=line_width, box_color=box_color if box_color !=None else COLORS[label], textColor=textColor, line_ratio=line_ratio)
    else:
        for index, box in enumerate(boxes):
            image_copy = plot_one_box(image_copy, box, None, line_width=line_width, box_color=box_color if box_color !=None else COLORS[label], textColor=textColor, line_ratio=line_ratio)
        
    return image_copy
            

def plot_one_box(image, box, label=None, line_width=3, box_color="lime", textColor="white", line_ratio=0.3):
    '''
        # 使用opencv在image上画出一个box, box=[x,y,x,y]
    '''
    # 图像格式转化
    img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    

    ######### 画矩形框 #########
    draw = ImageDraw.ImageDraw(img)
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
        # 单个字体大小（字体为正方形，这里的大小指的是其宽或高的像素值）。
        # 同时限定单个字尺寸最大为20
        textSize = min(20, int(box_width*3/4/len(label)))
        fontStyle = ImageFont.truetype("SimHei.ttf", textSize, encoding="utf-8")
        (text_w, text_h) = draw.textsize(label, fontStyle)
        new_y1 = y1-text_h - line_width if y1-text_h >=0 else y1 + line_width
        draw.rectangle(((x1, new_y1),(x1+text_w, new_y1+text_h)), fill="blue", outline=None, width=line_width)  
        draw.text((x1,new_y1), label, textColor, font=fontStyle)
        
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
#     # 线条和字体的宽度
#     lt = line_thickness or round(0.002 * (image.shape[0] + image.shape[1]) / 2) + 1  # line/font thickness
    
#     # 画出box
#     [x1,y1,x2,y2] = box
#     cv2.rectangle(image, (x1,y1), (x2,y2), COLORS[box_color], thickness=lt, lineType=cv2.LINE_AA)
    
#     # 将int类型的label转化为字符串
#     label = str(label) if isinstance(label, int) else label
    
#     # 画出label
#     if label:
#         # label字体粗细
#         ft = max(lt - 1, 1)  # font thickness
#         # 文字的尺寸
#         [text_width, text_height] = cv2.getTextSize(label, 0, fontScale=lt/3, thickness=ft)[0]
#         ## 将文字画在框的左上角外侧，若上边沿空间不足，则画在框左上角内侧
#         # 文字框的右上角坐标
#         x2 = x1 + text_width
        
#         if (y1 - text_height) <= 0:
#             y2 = y1 + text_height
#             cv2.rectangle(image, (x1,y1), (x2,y2), COLORS[box_color], -1, cv2.LINE_AA)  # filled
#             putText(image, label,  (x1, y2 - 2), int(lt/3), (225, 255, 255))
# #             cv2.putText(image, label, (x1, y2 - 2), 0, lt / 3, [225, 255, 255], thickness=ft, lineType=cv2.LINE_AA)
#         else:
#             y2 = y1 - text_height
#             cv2.rectangle(image, (x1,y1), (x2,y2), COLORS[box_color], -1, cv2.LINE_AA)  # filled
#             putText(image, label,  (x1, y2 - 2), int(lt/3), (225, 255, 255))
# #             cv2.putText(image, label, (x1, y1), 0, lt / 3, [225, 255, 255], thickness=ft, lineType=cv2.LINE_AA)
        
    
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
    

def xywh2xyxy(box):
    if isinstance(box[0], int):
        x,y,w,h = box
        return [x,y,x+w,y+h]
    else:
        temp = []
        for [x,y,w,h] in box:
            temp.append([x,y,x+w,y+h])
        return temp


def putText(img,text,org,textSize,color):
    '''
        org: (x,y)
    '''
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    draw = ImageDraw.Draw(img)

    # 字体的格式
    fontStyle = ImageFont.truetype("SimHei.ttf", textSize, encoding="utf-8")
    # 绘制文本
    draw.text(org, text, color, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)



from PIL import Image, ImageDraw, ImageFont
import cv2

def text_bar(width=500, height=500, people_num=10, people_name="不知道", input_image=None, text_size=45):

    
    image = Image.new('RGB', (width, height), (255, 255, 255))

    # img_PIL = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))# 图像从OpenCV格式转换成PIL格式
    font = ImageFont.truetype("SimHei.ttf", text_size, encoding="utf-8")#40为字体大小，根据需要调整
    textColor = (0,0,0)
    
    renshu = f"累计人数:{people_num}"
    xingming = f"姓名:{people_name}"
    print(font.getsize(xingming))
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), renshu, font=font, fill=textColor)   # position  #第一个数值是距左，第二个数值是距上
    draw.text((110,100), xingming, font=font, fill=textColor)
    draw.rounded_rectangle(((100, 150),(400, 450)), radius=10, fill=None, outline='#e0c8d1', width=3)  

    if isinstance(input_image, np.ndarray):
        input_image = Image.fromarray(cv2.cvtColor(pad_image(input_image, target_size=280), cv2.COLOR_BGR2RGB))
        image.paste(input_image,(110,160))  #,390,440

    # frame = cv2.cvtColor(np.asarray(img_PIL),cv2.COLOR_RGB2BGR)#转换回OpenCV格式
    image.show()


def pad_image(image, target_size, bg_color=(255,255,255)):
    '''
        将输入图片保持长宽比，缩放到target_size大小
    '''
    ih, iw = image.shape[:2] # 
    if isinstance(target_size, tuple):
        w, h = target_size # 
    else:
        w, h = (target_size, target_size)
    scale = min(w / iw, h / ih) # 
   
    nw = int(iw * scale)
    nh = int(ih * scale)
    
    image = imutils.resize(image, width=nw, height=nh)    
    new_image = cv2.copyMakeBorder(image,  top=(h-nh)//2, bottom=(h-nh)//2, \
                                   left=(w-nw)//2, right=(w-nw)//2, borderType=cv2.BORDER_CONSTANT, value=bg_color)
    
    return new_image

def is_valid_head_box(head_box):
    '''
        检测头部矩形框的合理性
        规则为：1<=高度/宽度<=1.8
    
    '''
    x,y,w,h = head_box
    if 1<= h/w <=1.5:
        return True
    else:
        return False


class image_saver:
    def __init__(self, save_dir="./"):
        self.count = itertools.count(0)
        self.save_dir = save_dir
    
    def image_roi_save(self, image, boxes, prefix=""):
        '''
            保存输入图片中的ROI区域，其中image为输入图片，
            boxes为图片中的ROI区域。默认box为xywh格式。
        '''
        # 检查存储目录，若不存在，则创建之。
        pathlib.Path(self.save_dir).mkdir(parents=True, exist_ok=True) 
        
        # 若boxes中包含了单个矩形区域
        if isinstance(boxes[0], int):
            boxes = [boxes]
        for index, [x,y,w,h] in enumerate(boxes):
            ROI = image[y:y+h,x:x+w]
            image_count = next(self.count)
            image_name = f"{image_count}_{index}.jpg" if prefix=="" else f"{prefix}_{image_count}_{index}.jpg"
            save_dir = os.path.join(self.save_dir,image_name)
            cv2.imwrite(save_dir, ROI)
        


if __name__ == '__main__':
    image = cv2.imread("./test.jpg")
    text_bar(width=500, height=500, input_image=image)
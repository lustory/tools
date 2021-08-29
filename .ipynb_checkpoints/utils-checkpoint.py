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



# 苋菜红  (166,27,41)
# 春梅红 （241,147,156)
# 大鹅紫 （51,20,30)
# COLORS = [(166,27,41),\
#           (241,147,156),\
#           (51,20,30)]

# BGR
COLORS = {"body":"lime", "head":"red"}


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
        
    




def put_text(img, text, org, textSize, color):
    '''
        org: (x,y)
    '''
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    draw = ImageDraw.Draw(img)

    # 字体的格式
    fontStyle = ImageFont.truetype("/home/xjtu/.research/tools/SimHei.ttf", textSize, encoding="utf-8")
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

import imagezmq
from threading import Thread
import simplejpeg
import imutils

'''
    sender: imagezmq.ImageSender。
    msg: 待发送的消息。
    image: 待发送的图片。
    image_quality: 对输入图片进行jpg压缩后的图片质量，仅当image_type="buffer"时有效
    image_type: 传输的图片类型，包含"buffer"和"image"两类。buffer表示传输jpgbuffer，
                image表示直接传输cv2图片。默认为buffer。
    is_req_rep: 是否为req_rep消息传输模式，消息传输模式包含req_rep和pub_sub两种模式，
                默认为req_rep。
'''
    
    
class msgSender:
    def __init__(self, remote_addr, port, image_type="buffer", req_rep=False):
        self.req_rep = req_rep
        self.image_type= image_type
        self.sender = imagezmq.ImageSender(f"tcp://{remote_addr}:{port}", REQ_REP=self.req_rep)
    
    def _send(self, image, msg, im_w=None, image_quality=90):
        if (im_w != None) and (im_w < image.shape[1]):
            image = imutils.resize(image, width=im_w)
                 
        if self.image_type=="buffer":
            jpg_buffer = simplejpeg.encode_jpeg(image, quality=image_quality, colorspace='BGR', fastdct=False)
            if self.req_rep:
                self.sender.send_jpg_reqrep(msg, jpg_buffer)
            else:
                self.sender.send_jpg(msg, jpg_buffer)
        else:
            if self.req_rep:
                self.sender.send_image_reqrep(msg, image)
            else:
                self.sender.send_image(msg, image)
                
    def send(self, image, msg, im_w=None, image_quality=90):
        Thread(target=self._send, args=(image, msg, im_w, image_quality)).start()

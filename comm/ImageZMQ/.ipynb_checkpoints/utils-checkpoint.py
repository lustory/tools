import simplejpeg
from itertools import count
from .VideoStreamSubscriber import VideoStreamSubscriber



def receive_msg2queue(input_queue, hostname="192.168.31.100", port=6500, \
                      is_req_rep=True, timeout=360, dtype="buffer"):

    # dtype=image 表示接受numpy格式的image, buffer表示接收jpeg buffer
    receiver = VideoStreamSubscriber(hostname, port, is_req_rep=is_req_rep, dtype=dtype) 
    print(f"[INFO] start receiving msgs in {'REQ_REP' if is_req_rep else 'pub_sub'} mode ...")

    msg_count = count(0)
    while True:

        msg, image = receiver.receive(timeout=timeout)
        if dtype == "buffer":
            image = simplejpeg.decode_jpeg(image, colorspace='BGR', fastdct=False, fastupsample=False)

        input_queue.put({"msg":msg, "image":image})
#         print(f"[INFO] msgs received: {next(msg_count):,}, cached in queue: {input_queue.qsize():,}")
        

def send_msg(sender, image, msg="", image_quality=90, image_type="buffer", is_req_rep=True):
    '''
        发送消息。
        sender: imagezmq.ImageSender。
        msg: 待发送的消息。
        image: 待发送的图片。
        image_quality: 对输入图片进行jpg压缩后的图片质量，仅当image_type="buffer"时有效
        image_type: 传输的图片类型，包含"buffer"和"image"两类。buffer表示传输jpgbuffer，
                    image表示直接传输cv2图片。默认为buffer。
        is_req_rep: 是否为req_rep消息传输模式，消息传输模式包含req_rep和pub_sub两种模式，
                    默认为req_rep。
    '''
    
    # 方式1：直接发送图片
    if image_type != "buffer":
        if is_req_rep:
            sender.send_image_reqrep(msg, image)
        else:
            sender.send_image(msg, image)
    # 方式2：发送图片jpg buffer
    else: 
        jpg_buffer = simplejpeg.encode_jpeg(image, quality=image_quality, \
                                            colorspace='BGR', fastdct=False)
        if is_req_rep:
            sender.send_jpg_reqrep(msg, jpg_buffer)
        else:
            sender.send_jpg(msg, jpg_buffer)
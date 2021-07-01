import simplejpeg
from .VideoStreamSubscriber import VideoStreamSubscriber



def receive_msg2queue(input_queue, hostname="192.168.31.100", port=6500, timeout=360, dtype="buffer"):

    # dtype=image 表示接受numpy格式的image, buffer表示接收jpeg buffer
    receiver = VideoStreamSubscriber(hostname, port, is_req_rep=True, dtype=dtype) 

    while True:

        msg, image = receiver.receive(timeout=timeout)
        if dtype == "buffer":
            image = simplejpeg.decode_jpeg(image, colorspace='BGR', fastdct=False, fastupsample=False)

        input_queue.put({"msg":msg, "image":image})
        print(f"[INFO] msgs cached : {input_queue.qsize()}")
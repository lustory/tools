import simplejpeg
from itertools import count
from .VideoStreamSubscriber import VideoStreamSubscriber



def receive_msg2queue(input_queue, hostname="192.168.31.100", port=6500, \
                      is_req_rep=True, timeout=10*5, dtype="buffer"):

    # dtype=image 表示接受numpy格式的image, buffer表示接收jpeg buffer
    receiver = VideoStreamSubscriber(hostname, port, is_req_rep=is_req_rep, dtype=dtype) 
    print(f"[INFO] start receiving msgs in {'REQ_REP' if is_req_rep else 'pub_sub'} mode ...")

    msg_count = count(0)
    while True:

        _, image = receiver.receive(timeout=timeout)
        image = simplejpeg.decode_jpeg(image, colorspace='BGR', fastdct=False, fastupsample=False)
        input_queue.put(image)
#         print(f"[INFO] msgs received: {next(msg_count):,}, cached in queue: {input_queue.qsize():,}")
        

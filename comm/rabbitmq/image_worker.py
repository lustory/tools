#!/usr/bin/env python
import pika, sys, os
import simplejpeg
import cv2
import json
import numpy as np
import base64
import matplotlib.pyplot as plt



# 和server建立连接
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# 声明exchange及名称，这样worker才能连接到某个具体的exchange
channel.exchange_declare(exchange='shot', exchange_type='topic')

# 建立queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

binding_key = "454_desktop"

# 从系统输入中获取binding_key，若binding_key与publisher一致，则接收publisher的消息
channel.queue_bind(exchange='shot', queue=queue_name, routing_key=binding_key)


def callback(ch, method, properties, body):
    print(f" [x] {method.routing_key}")
    msg = json.loads(body)
    msg["image"] = np.asarray(msg["image"],dtype=np.uint8)

    print(msg['idx'], msg["time_stamp"])
    
    

    # # image = simplejpeg.decode_jpeg(bytes(message["image"], encoding = "utf8" , errors='ignore'), colorspace='BGR', fastdct=False, fastupsample=False)
    # print("fdsafsdfsdf", image.shape)
    # cv2.imshow(f"{method.routing_key}", msg["image"])
    plt.imshow(msg["image"])
    plt.show()
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()



channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)


channel.start_consuming()



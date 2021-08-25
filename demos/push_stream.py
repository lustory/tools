import cv2
import sys
import ffmpeg
sys.path.append("/home/lulei/research/tools/")

from tools.video.push_stream import PUSH_STREAM


filename = "test.mp4"
push_url = "rtmp://localhost:1935/stream/test"

cap = cv2.VideoCapture(filename)

# 读取视频属性
cap = cv2.VideoCapture(filename)
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))



PS = PUSH_STREAM("localhost", 1935, "test1", image_width=width, image_height=height, fps=fps)
PS.start_prush_rtmp_stream()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    PS.image_write(frame)
    
    

    
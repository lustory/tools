import sys
sys.path.append("/home/xjtu/.research/tools")

from video.post_process import POST_PROCESS




hostname="127.0.0.1"
port=6001

PP = POST_PROCESS()
PP.start_receive(hostname, port)

PP.push_stream(ip="localhost", port=1935, stream_name="zhongyangbiandiansuo_1", decision_poolsize=5)
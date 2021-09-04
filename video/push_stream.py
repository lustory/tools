import subprocess

class PUSH_STREAM:
    def __init__(self, ip, port, stream_name, image_width, image_height, fps):
        self.ip = ip
        self.port = port
        self.stream_name = stream_name
        self.width = image_width
        self.height = image_height
        self.fps = fps 
        self.push_process = None
        
    def start_prush_rtmp_stream(self):
        '''
            ip: 推流ip
            port: 推流端口
            stream_name: 推流名称
            image_width: 视频宽度
            image_height: 视频高度
            fps: 视频帧率
        '''
        # rtmp 推流地址
        rtmp_url = f"rtmp://{self.ip}:{self.port}/live/{self.stream_name}"
            
        # ffmpeg命令
        command = ['ffmpeg',
                   '-y',
                   '-f', 'rawvideo',
                   '-vcodec', 'rawvideo',
                   '-pix_fmt', 'bgr24',
                   '-s', "{}x{}".format(self.width, self.height),
                   '-r', str(self.fps),
                   '-i', '-',
                   '-c:v', 'libx264',
                   '-pix_fmt', 'yuv420p',
                   '-preset', 'ultrafast',
                   '-f', 'flv',
                   rtmp_url]
        
        # 开启子进程
        self.push_process = subprocess.Popen(command, stdin=subprocess.PIPE)
        
    def image_write(self, image):
        self.push_process.stdin.write(image.tobytes())
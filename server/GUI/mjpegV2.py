# -*- coding: UTF-8 -*-
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
import cv2
import asyncio
import time
import logging
import queue
import threading

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
frame_queue=queue.Queue()
class VideoStreamer:
    def __init__(self,video_path):
        self._cap = None
        self._frame_cache = None
        self._running = False
        self._lock = asyncio.Lock()
        self.video_path=video_path
        self.frame_queue = asyncio.Queue(maxsize=10)
        self.mainloop = asyncio.get_event_loop()
    async def initialize(self):
        async with self._lock:
            if self._cap is None:
                # rtsp与正常的分开处理
                if self.video_path.startswith('rtsp:'):
                    self._cap = cv2.VideoCapture(self.video_path, cv2.CAP_FFMPEG)
                    # while True:
                    #     ret, frame = self._cap.read()
                    #     if not ret:
                    #         print("帧读取失败，重试或退出")
                    #         break
                    #
                    #     cv2.imshow('RTSP Stream', frame)
                    #     if cv2.waitKey(1) & 0xFF == ord('q'):
                    #         break


                else:
                    self._cap = cv2.VideoCapture(self.video_path)
                if not self._cap.isOpened():
                    logger.error("无法打开视频文件")
                    raise RuntimeError("视频文件打开失败")
                logger.info("视频初始化完成")





    async def safe_read_frame(self):
        try:
            success, frame = self._cap.read()
            if not success:
                logger.info("检测到视频结束，准备重播")
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, frame = self._cap.read()
                if not success:
                    logger.error("视频重播失败，重新初始化")
                    await self.restart()
                    return None
            return frame
        except Exception as e:
            logger.error(f"帧读取异常: {str(e)}")
            await self.restart()
            return None



    async def restart(self):
        async with self._lock:
            if self._cap:
                self._cap.release()
                self._cap = cv2.VideoCapture("test1.mp4")
                logger.info("视频流重新初始化")

    async def get_frame(self):
        await self.initialize()
        fps = self._cap.get(cv2.CAP_PROP_FPS) or 25
        interval = 1 / fps
        while True:
            start_time = time.monotonic()
            frame = await self.safe_read_frame()
            if  frame is None:
                break
            _,buffer = cv2.imencode(".jpg",frame,[int(cv2.IMWRITE_JPEG_QUALITY), 75])
            self._frame_cache = buffer.tobytes()

            cv2.imshow("test",frame)
            cv2.waitKey(1)
            # 保证稳定帧间隔
            elapsed = time.monotonic() - start_time
            print(elapsed)
            await asyncio.sleep(max(0, (interval - elapsed)/3))

            if self._frame_cache:
                yield (
                        b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' +
                        self._frame_cache + b'\r\n'
                )

    async def frame_generator(self):
        await self.initialize()
        fps = self._cap.get(cv2.CAP_PROP_FPS) or 25
        interval = 1 / fps

        while True:
            start_time = time.monotonic()
            frame = await self.safe_read_frame()

            if frame is not None:
                # 帧处理
              #  frame = cv2.resize(frame, (640, 480))
                _, buffer = cv2.imencode('.jpg', frame, [
                    int(cv2.IMWRITE_JPEG_QUALITY), 75
                ])
                self._frame_cache = buffer.tobytes()

            # 保证稳定帧间隔
            elapsed = time.monotonic() - start_time
            print(elapsed)
            await asyncio.sleep(max(0, (interval - elapsed)/3))

            if self._frame_cache:
                yield (
                        b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' +
                        self._frame_cache + b'\r\n'
                )


    def start(self):
        """启动视频流线程"""
        self.running = True
        self.thread = threading.Thread(target=self.generator)
        self.thread.daemon = True
        self.thread.start()


    def generator(self):
        video_path="rtsp://localhost:5558/live"
        cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
        while True:
            ret,frame = cap.read()
            # cv2.imshow("test", frame)
            # cv2.waitKey(1)
           # print(ret)
            if not ret:
               break

            asyncio.run_coroutine_threadsafe(self.frame_queue.put(frame),self.mainloop)
        cap.release()


    async def consume_frame(self):

         while True:

             frame = await self.frame_queue.get()
             # print('.2.')
             # cv2.imshow("test",frame)
             # cv2.waitKey(1)
             _,buffer=cv2.imencode('.jpg',frame)
             _frame_cache = buffer.tobytes()

             yield (
                     b'--frame\r\n'
                     b'Content-Type: image/jpeg\r\n\r\n' +
                     _frame_cache + b'\r\n'
             )




streamer1 = VideoStreamer('rtsp://localhost:5558/live')
@app.get('/video_feed1')
async def video_feed1():
    return StreamingResponse(
        streamer1.get_frame(),
        media_type='multipart/x-mixed-replace; boundary=frame'
)
streamer11 = VideoStreamer('rtsp://localhost:5558/live')
streamer11.start()
@app.get('/video_feed11')
async def video_feed11():
    return StreamingResponse(
        streamer11.consume_frame(),
        media_type='multipart/x-mixed-replace; boundary=frame'
)


streamer2 = VideoStreamer('datas/test2.mp4')
@app.get('/video_feed2')
async def video_feed2():
    return StreamingResponse(
        streamer2.frame_generator(),
        media_type='multipart/x-mixed-replace; boundary=frame'
)


streamer3 = VideoStreamer('datas/test3.mp4')
@app.get('/video_feed3')
async def video_feed3():
    return StreamingResponse(
        streamer3.frame_generator(),
        media_type='multipart/x-mixed-replace; boundary=frame'
)
# http://127.0.0.1:8003/video_feed4
streamer4 = VideoStreamer('datas/test4.mkv')
@app.get('/video_feed4')
async def video_feed4():
    return StreamingResponse(
        streamer4.frame_generator(),
        media_type='multipart/x-mixed-replace; boundary=frame'
)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>稳定视频流</title>
    <style>
        #loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            display: none;
        }
        .container {
            position: relative;
            width: 640px;
            height: 480px;
            background: #000;
        }
    </style>
</head>

<body>
    <div class="container">
        <img id="video" src="" style="width:100%;height:100%">
         <div id="loading"></div>
    </div>

    <script>
        let retryCount = 0;
        const maxRetry = 5;
        const video = document.getElementById('video');
        const loading = document.getElementById('loading');

        function showLoading() {
            loading.style.display = 'block';
        }

        function hideLoading() {
            loading.style.display = 'none';
        }

        function connectStream() {
            showLoading();
            video.src = 'http://127.0.0.1:3009/customer-flow/video-stream/8db5e66d-9b5b-4dde-a016-e6a08b42bceb';
          

            video.onloadstart = () => {
                retryCount = 0;
                hideLoading();
            }

            video.onerror = () => {
                if(retryCount < maxRetry) {
                    retryCount++;
                    setTimeout(() => {
                        showLoading();
                        video.src += '&retry=' + retryCount;
                    }, 1000 * Math.pow(2, retryCount));
                } else {
                    video.src = '';
                    alert('视频连接失败');
                }
            }
        }

        // 初始连接
        connectStream();

        // 网络状态检测
        window.addEventListener('online', connectStream);
    </script>
</body>
</html>
"""

@app.get("/web")
async def get(video_id):

    return HTMLResponse(HTML_PAGE.replace("{video_id}",video_id))
    #return HTMLResponse(HTML_PAGE)
if __name__ == "__main__":
    import uvicorn

    powertime=1
    # 启动FastAPI
    main_loop = asyncio.get_event_loop()
    config = uvicorn.Config('mjpegV2:app',
        host="0.0.0.0",
        port=8008,
        http="h11",
        timeout_keep_alive=65,
        limit_concurrency=100)
    # config = uvicorn.Config(app, host="127.0.0.1", port=8765, loop=main_loop)
    server = uvicorn.Server(config)



    main_loop.run_until_complete(server.serve())




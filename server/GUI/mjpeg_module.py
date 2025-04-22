# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/18 2:00 
@Describe:
'''
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
frame_queue = queue.Queue()


class VideoStreamer:
    def __init__(self, video_path):
        self._cap = None
        self._frame_cache = None
        self._running = False
        self._lock = asyncio.Lock()
        self.video_path = video_path
        self.frame_queue = asyncio.Queue(maxsize=10)
        self.mainloop = asyncio.get_event_loop()

    async def initialize(self):
        async with self._lock:
            if self._cap is None:
                # rtsp与正常的分开处理
                if self.video_path.startswith('rtsp:'):
                    self._cap = cv2.VideoCapture(self.video_path, cv2.CAP_FFMPEG)
                # elif self.video_path.startswith('noframe'):
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

            if frame is None:
                break
            _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            self._frame_cache = buffer.tobytes()

            cv2.imshow("test", frame)
            cv2.waitKey(1)
            # 保证稳定帧间隔
            elapsed = time.monotonic() - start_time
            print(elapsed)
            await asyncio.sleep(max(0, (interval - elapsed) / 3))

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
            await asyncio.sleep(max(0, (interval - elapsed) / 3))

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
        video_path = "rtsp://localhost:5558/live"
        cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            asyncio.run_coroutine_threadsafe(self.frame_queue.put(frame), self.mainloop)
        cap.release()


    async def add_frame(self,frame):
        asyncio.run_coroutine_threadsafe(self.frame_queue.put(frame), self.mainloop)


    async def consume_frame(self):
        while True:
            frame = await self.frame_queue.get()
            # print('.2.')
            # cv2.imshow("test",frame)
            # cv2.waitKey(1)
            _, buffer = cv2.imencode('.jpg', frame)
            _frame_cache = buffer.tobytes()

            yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    _frame_cache + b'\r\n'
            )



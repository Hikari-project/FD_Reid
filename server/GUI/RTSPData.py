# -*- coding: UTF-8 -*-
'''
@Project :FD_Reid_Web 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/05/07 22:41 
@Describe:
'''
import asyncio
import queue
import threading
import uuid
import cv2

from libs.rtsp_check import is_img_not_valid

class RTSPData:
    """
    RTSPData RTSP流数据实例化
    """
    def __init__(self ,rtsp_url,max_num=3):
        # 创建链接
        self.cap=cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # 设置缓冲区大小

        self.rtsp_url=rtsp_url
        self.stream_id=str(uuid.uuid4()) # rtsp流的指代ip

        self.screen_img = self._get_screen_frame()
        self.height,self.width=self.screen_img.shape[:2]

        self.stop_event = threading.Event()
        # 启动rtsp自动解码线程
        self.mainloop = asyncio.get_event_loop()
        self._rtsp_2_frames_thread()


        self.origin_frame_queue=queue.Queue(maxsize=max_num)
        # self.process_frame_queue=queue.Queue(maxsize=max_num)
        self.process_frame_queue=asyncio.Queue(maxsize=max_num)




    def _get_screen_frame(self):
        """ 获取有效帧 """
        # 增加重连次数和超时处理
        valid_frame = None
        # 捕获首帧
        max_attempts = 100
        for i in range(max_attempts):
            ret, frame = self.cap.read()
            if ret and frame is not None and frame.size != 0:
                if is_img_not_valid(frame):
                    continue
                else:
                    print('发现未损坏图片', str(i))
                    valid_frame = frame
                    break
            cv2.waitKey(1)
        return valid_frame

    def _rtsp_2_frames_thread(self):

        def  _rtsp_2_frames():
            while not self.stop_event.is_set():
                ret, frame = self.cap.read()
                if ret:
                    try:
                        # print('frame2',str(self.origin_frame_queue.qsize()))
                        # cv2.imshow('frame2', frame)
                        # cv2.waitKey(1)
                        # 跨线程异步写入队列

                        #asyncio.run_coroutine_threadsafe(self.origin_frame_queue.put(frame),self.mainloop)
                       # await self.origin_frame_queue.put(frame, block=False)
                        self.origin_frame_queue.put(frame, block=False)

                    except queue.Full:

                        # _= asyncio.run_coroutine_threadsafe(self.origin_frame_queue.get(),self.mainloop)
                        _=self.origin_frame_queue.get()
                        pass  # 忽略队列满的情况

                else:
                    print("RTSP读取失败，尝试重连...")
                    break
            self.cap.release()
        # 启动同步采集线程
        threading.Thread(target=_rtsp_2_frames,daemon=True).start()
        #asyncio.run_coroutine_threadsafe(_rtsp_2_frames(), self.mainloop)
        # thread=threading.Thread(target=_rtsp_2_frames)
        # thread.start()

    async def _async_put_frame(self, frame):
        """异步队列写入方法"""
        try:
            await self.origin_frame_queue.put(frame)
            print(f"成功写入队列，当前大小: {self.origin_frame_queue.qsize()}")
        except asyncio.QueueFull:
            print("队列已满，丢弃最旧帧")
            _ = await self.origin_frame_queue.get()
            await self.origin_frame_queue.put(frame)
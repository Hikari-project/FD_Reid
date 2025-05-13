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
import time
import uuid
import cv2

from libs.rtsp_check import is_img_not_valid

class RTSPData:
    """
    RTSPData RTSP流数据实例化
    """
    def __init__(self ,rtsp_url,max_num=10,name=''):

        # 创建链接
        self.cap=cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 5)  # 设置缓冲区大小
        self.rtsp_url=rtsp_url
        self.stream_id=str(uuid.uuid4()) # rtsp流的指代ip

        # 是否需要图片
        self.is_need_screen_img = False  # 是否需要图片，后面分析的时候会为True,然后拿取分析的时候的第一帧
        self.screen_img = self._get_screen_frame()
        self.screen_img_path = f'static/frames/{self.stream_id}.jpg'
        self.height,self.width=self.screen_img.shape[:2]




        self.stop_event = threading.Event()
        # 启动rtsp自动解码线程
        self.mainloop = asyncio.get_event_loop()
        # 绑定到该事件循环
        asyncio.set_event_loop(self.mainloop)

        self._rtsp_2_frames_thread()
        self.name=name

        self.origin_frame_queue=queue.Queue(maxsize=max_num)
        # self.process_frame_queue=queue.Queue(maxsize=max_num)
        self.process_frame_queue=asyncio.Queue(maxsize=max_num)

        # 是否更新resize
        self.is_resize = False
        # 如果画面大于1920则进行resize
        self.min_width_px = 1280
        if self.width > self.min_width_px:
            new_h = self.height * self.min_width_px // self.width
            self.screen_img = cv2.resize(self.screen_img, (self.min_width_px, new_h))
            self.width, self.height = self.min_width_px, new_h
            print(self.height, self.width)
            print(self.min_width_px, new_h)
            self.is_resize = True


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
                       # print(f'rtsp:{self.rtsp_url} 压入一个frame，当前大小：{self.origin_frame_queue.qsize()}')
                        if self.is_resize:
                            frame = cv2.resize(frame, (self.width, self.height))
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
            if self.is_resize:
                frame = cv2.resize(frame, (self.width, self.height))
            await self.origin_frame_queue.put(frame)
            print(f"成功写入队列，当前大小: {self.origin_frame_queue.qsize()}")
        except asyncio.QueueFull:
            print("队列已满，丢弃最旧帧")
            _ = await self.origin_frame_queue.get()
            await self.origin_frame_queue.put(frame)

class HandleRTSPData:
    """已处理的RTSP流信息"""
    def __init__(self,rtsp_url='',frame_url='',mjpeg_stream='',mjpeg_url='',name='hello'):
        self.rtsp_url=rtsp_url
        self.frame_url=frame_url
        self.mjpeg_stream=mjpeg_stream  # 原始的mjpeg
        self.mjpeg_url=mjpeg_url  # 已处理的mjpeg
        self.name=name
        self.create_time=time.ctime()

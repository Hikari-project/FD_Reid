import queue
from datetime import datetime
import re
import gc
import os
import cv2
import sys

from pydantic import BaseModel

# 确保能找到项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
import torch

sys.path.append('../')

from log.log import LogSystem, GlobalCounter

import Algorithm.libs.config.model_cfgs as cfgs

from libs.reid_sqlV2 import init_db, add_feature, update_feature, delete_feature, load_features_from_sqlite, \
    get_max_person_id, clear_all_features

import threading
import json
import os
import tempfile
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
import time
import cv2
import asyncio
class FixedSizeAsyncQueue(asyncio.Queue):
    def __init__(self, maxsize=5):
        super().__init__(maxsize)

    async def put(self, item):
        if self.full():
            # 队列已满时，先丢弃最旧元素
            _ = await self.get()
        await super().put(item)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
# 是否渲染窗口
show = False
# -*- coding:utf-8 -*-
"""
@Author: self-798
@Contact: 123090233@link.cuhk.edu.cn
@Version: 4.0
@Date: 2025/4/5 
@Describe:
加入log系统，加入数据库，重构为类结构，改进进出店检测逻辑
"""

import os
import cv2
import numpy as np
import json
import time
from typing import Union, List
from Reid_module import ReIDTracker
from libs.rtsp_check import is_img_not_validV2
# 获取主事件循环
mainloop = asyncio.get_event_loop()
asyncio.set_event_loop(mainloop)

from concurrent.futures import ThreadPoolExecutor

# 创建编码线程池（根据CPU核心数调整）
encode_executor = ThreadPoolExecutor(max_workers=4)
# 添加自定义JSON编码器
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

from concurrent.futures import ThreadPoolExecutor

# 创建全局线程池
executor = ThreadPoolExecutor(max_workers=4)
@dataclass
class StreamInfo:
    """Stream information dataclass"""
    url: str  # 原始URL (RTSP或视频文件路径)
    mjpeg_url: str  # 转换后的MJPEG URL
    is_rtsp: bool  # 是否为RTSP流
    config: Dict[str, Any]  # 原始配置
    config_path: str  # 配置文件路径
    active: bool = True  # 流状态
    last_update: float = 0.0  # 最后更新时间戳
    reconnect_count: int = 0  # 重连计数
    show_window: bool = True  # 是否显示窗口


class StreamManager:
    """
    管理视频流和文件的类，支持RTSP和视频文件，提供配置管理和线程安全操作
    """

    def __init__(self, temp_dir=None, max_reconnect=10, mjpeg_server_port=8554,
                 frame_queue=[asyncio.Queue(maxsize=10)],rtsp_datas={}):
        """
        初始化流管理器

        Args:
            temp_dir: 临时文件目录，如果为None则使用系统临时目录
            max_reconnect: RTSP流最大重连次数，超过此数值将停止重连
            mjpeg_server_port: MJPEG服务器端口
        """
        self.streams: List[StreamInfo] = []
        self.lock = threading.RLock()  # 使用可重入锁保证线程安全
        self.temp_dir = temp_dir or tempfile.gettempdir()
        os.makedirs(self.temp_dir, exist_ok=True)
        self.processing_thread = None
        self.stop_event = threading.Event()
        self.max_reconnect = max_reconnect
        self.mjpeg_server_port = mjpeg_server_port
        self.mjpeg_server_running = False


        # 存储的数据
        # 存储处理线程的信息,用于后端管理线程资源
        video_thread_info = {}
        # 记录从rtsp到队列序号的映射

        self.video_thread_info = {}
        self.video_rtsp_dict= {}
        # 已处理的队列
        self.handle_frame = frame_queue
        # 已处理队列的状态管理,是否可用
        self.handle_queue_status = {
            0: True,
            1: True,
            2: True,
            3: True,
        }

        self.origin_frame_queue=[queue.Queue(maxsize=10),queue.Queue(maxsize=10),queue.Queue(maxsize=10),queue.Queue(maxsize=10)]
        # 已处理队列的状态管理,是否可用
        self.origin_frame_queue_status = {
            0: True,
            1: True,
            2: True,
            3: True,
        }
        self.origin_video_rtsp_dict = {}

        self.rtsp_datas=rtsp_datas


    def load_model(self):
        pass

    def is_rtsp_url(self, url: str) -> bool:
        """
        检查URL是否为RTSP流
        Args:
            url: 要检查的URL
        Returns:
            bool: 是否为RTSP流

        """
        return url.lower().startswith('rtsp://')

    def is_video_file(self, path: str) -> bool:
        """
        检查文件是否为视频文件

        Args:
            path: 文件路径

        Returns:
            bool: 是否为视频文件
        """
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']
        _, ext = os.path.splitext(path)
        return ext.lower() in video_extensions

    def setup_streams(self, config_list: List[Dict[str, Any]], queue_index=0, show_windows=True,stream_id=0) -> List[
        Dict[str, str]]:
        """
        设置流列表
        Args:
            config_list: 配置列表，每个元素包含URL和区域配置
            queue_index: 这个流输出的队列下标
            show_windows: 是否显示视频窗口
        Returns:
            List[Dict[str, str]]: 原始URL和对应MJPEG URL列表
        """
        with self.lock:
            # 清空现有流
           # self._clear_streams()

            # 处理新的配置列表
            mjpeg_list = []
            config = config_list[0]  # 后续要处理成只识别单个的

            # 验证必要的配置项

            # 获取路由
            url = config["rtsp_url"]

            # 检查是否为RTSP流或视频文件

            is_rtsp = self.is_rtsp_url(url)
            is_video = self.is_video_file(url) if not is_rtsp else False

            if not (is_rtsp or is_video):
                print(f"警告: URL '{url}' 既不是RTSP流也不是视频文件，将尝试作为视频文件处理")
                is_video = True

            # 检查区域配置
            if "points" not in config or not config["points"]:
                # 创建默认区域配置
                config["points"] = [[100, 400], [500, 400], [500, 200], [100, 200]]

            # if "b1" not in config or not config["b1"]:
            #     # 创建默认b1配置
            #     config["b1"] = [config["points"][0], config["points"][1]]
            #

            if "passway" not in config or not config["passway"]:
                # 创建默认b1配置
                config["b1"] = [config["points"][0], config["points"][1]]

            # 取第一个config
            config["b1"] = config["passway"][0]

            if "b2" not in config:
                # 创建默认b2配置 (中间线)
                x1 = (config["points"][0][0] + config["points"][3][0]) // 2
                y1 = (config["points"][0][1] + config["points"][3][1]) // 2
                x2 = (config["points"][1][0] + config["points"][2][0]) // 2
                y2 = (config["points"][1][1] + config["points"][2][1]) // 2
                config["b2"] = [[x1, y1], [x2, y2]]

            if "g2" not in config:
                # 创建默认g2配置 (顶线)
                config["g2"] = [config["points"][3], config["points"][2]]

            # 生成配置文件路径
            config_path = os.path.join(self.temp_dir, f"stream_config_{queue_index}.json")

            # 保存配置到JSON文件
            with open(config_path, 'w') as f:
                json.dump(config, f, cls=NumpyEncoder)

            # 生成MJPEG URL
            # mjpeg_url = self.generate_mjpeg_url(url, i)
            mjpeg_url = ''
            # 创建流信息
            stream_info = StreamInfo(
                url=url,
                mjpeg_url=mjpeg_url,
                is_rtsp=is_rtsp,
                config=config,
                config_path=config_path,
                active=True,
                last_update=time.time(),
                reconnect_count=0,
                show_window=show_windows
            )

            # 添加到流列表
            self.streams.append(stream_info)

            # 添加到返回列表
            mjpeg_list.append({
                "source_url": url,
                "mjpeg_url": f"/customer-flow/video_feed?stream_id={stream_id}",
                "is_rtsp": is_rtsp,
                "stream_index": queue_index
            })

            return mjpeg_list


    def update_stream_status(self, index: int, active: bool, reconnect_increment=False) -> bool:
        """
        更新流状态

        Args:
            index: 流索引
            active: 是否活跃
            reconnect_increment: 是否增加重连计数

        Returns:
            bool: 更新是否成功
        """
        with self.lock:
            if 0 <= index < len(self.streams):
                self.streams[index].active = active
                self.streams[index].last_update = time.time()

                if reconnect_increment:
                    self.streams[index].reconnect_count += 1

                return True
            return False


    def reset_reconnect_count(self, index: int) -> bool:
        """
        重置流的重连计数

        Args:
            index: 流索引

        Returns:
            bool: 重置是否成功
        """
        with self.lock:
            if 0 <= index < len(self.streams):
                self.streams[index].reconnect_count = 0
                return True
            return False





    def should_reconnect(self, index: int) -> bool:
        """
        检查是否应该继续尝试重连

        Args:
            index: 流索引

        Returns:
            bool: 是否应该继续尝试重连
        """
        with self.lock:
            if 0 <= index < len(self.streams):
                return (self.streams[index].reconnect_count < self.max_reconnect and
                        self.streams[index].active and
                        self.streams[index].is_rtsp)
            return False



    def process_video_in_thread(self, video_source, temp_data={},
                                skip_frames=2, match_thresh=0.15, is_track=True, save_video=False,
                                stream_manager=None, show_window=True, window_name=None, queue_index=0):
        """
        在单独的线程中处理视频源（可以是OpenCV的VideoCapture对象或RTSP URL）

        Args:
            video_source: 视频源，可以是OpenCV的VideoCapture对象或RTSP URL字符串
            temp_data: 临时数据
            skip_frames: 跳帧数
            match_thresh: 匹配阈值
            is_track: 是否启用跟踪
            save_video: 是否保存结果视频
            stream_manager: 流管理器实例，用于更新状态
            show_window: 是否显示窗口
            window_name: 窗口名称，如果为None，则自动生成
            queue_index: 处理后的帧放入哪个队列的索引

        Returns:
            thread_info: 包含线程对象、停止事件等信息的字典
        """
        import threading
        import cv2
        print("process_video_in_thread")
        # 创建停止事件
        print(len(self.rtsp_datas))
        print(self.rtsp_datas)
        current_rtsp_data=self.rtsp_datas[video_source]

        asyncio.set_event_loop(current_rtsp_data.mainloop)
        print('...11')
        async def _process_video_task(current_rtsp_data):
            """线程内运行的任务函数"""

            # 创建日志系统
            log_system = LogSystem()

            # 创建跟踪器
            tracker = ReIDTracker(log_system=log_system)
            print("temp_data:", str(temp_data))
            if not tracker.setup_processing(None, temp_data):
                print(f"无法设置视频处理环境")
                return
            frame_count=0
            #current_rtsp_data.origin_frame_queue=asyncio.Queue(maxsize=1)

            while not current_rtsp_data.stop_event.is_set():
                try:
                    # 尝试读取帧
                    # 同步队列获取，（使用线程池避免阻塞）
                   # print(current_rtsp_data.origin_frame_queue.qsize())
                    print('origin:', str(current_rtsp_data.origin_frame_queue.qsize()))
                    frame = current_rtsp_data.origin_frame_queue.get()
                    # frame= await mainloop.run_in_executor(
                    #     None,
                    #     lambda: current_rtsp_data.origin_frame_queue.get()
                    # )

                   # frame = current_rtsp_data.origin_frame_queue.get()
                    # ret,frame=cap.read()

                    # 增加帧计数
                    # frame_count += 1
                    # cv2.imshow("frame4", frame)

                    # # 使用跟踪器处理帧

                    # processed_frame, info = await loop.run_in_executor(
                    #     None,  # 使用默认的线程池执行器
                    #     lambda: tracker.process_frame(frame, 0, match_thresh, is_track)
                    # )
                    #processed_frame, info=tracker.process_frame(frame, 0, match_thresh, is_track)
                    # 2. 在主线程序线程池运行同步函数（关键修复）
                    # processed_frame, info = await asyncio.wrap_future(
                    #     asyncio.run_coroutine_threadsafe(
                    #         # 将同步函数包装为协程调用
                    #
                    #             tracker.process_frame(frame, 1, 0.15, True)
                    #         ,
                    #         current_rtsp_data.mainloop  # 确保在主循环中调度
                    #     )
                    # )

                    # 处理帧（使用线程池）
                    main_loop=asyncio.get_event_loop()
                    processed_frame, info = await main_loop.run_in_executor(
                        None,
                        lambda: tracker.process_frame(frame, 0, match_thresh, is_track)
                    )

                   #processed_frame, info = tracker.process_frame(frame, 0, match_thresh, is_track)
                    # processed_frame, info =  asyncio.run_coroutine_threadsafe(tracker.process_frame(frame, 0, match_thresh, is_track),asyncio.get_event_loop())
                    # 在线程池中执行同步函数
                    # processed_frame, info = await loop.run_in_executor(
                    #     None,  # 使用默认线程池
                    #     lambda: tracker.process_frame(frame, 0, match_thresh, is_track)
                    # )

                    #processed_frame=frame

                    # 将处理后的帧放入队列
                    if processed_frame is not None:
                        try:
                            print('process:',str(current_rtsp_data.process_frame_queue.qsize()))
                            # await current_rtsp_data.process_frame_queue.put(processed_frame)

                            await asyncio.wrap_future(
                                asyncio.run_coroutine_threadsafe(
                                    current_rtsp_data.process_frame_queue.put(processed_frame),
                                    current_rtsp_data.mainloop
                                )
                            )
                            # asyncio.run_coroutine_threadsafe(current_rtsp_data.process_frame_queue.put(processed_frame),mainloop)
                           # current_rtsp_data.process_frame_queue.put(processed_frame)


                        except asyncio.QueueFull:
                        #    print(queue_index,type(queue_index))
                            print(f"无法将帧放入队列: {e}")
                            # _ =   await current_rtsp_data.process_frame_queue.get()
                            _ = await asyncio.wrap_future(
                                asyncio.run_coroutine_threadsafe(
                                    current_rtsp_data.process_frame_queue.get(),
                                    current_rtsp_data.mainloop
                                )
                            )
                            #await current_rtsp_data.process_frame_queue.put(processed_frame)

                    #
                    #processed_frame=frame
                    # cv2.imshow("processed_frame", processed_frame)
                    #
                    #
                    # cv2.waitKey(1)


                except Exception as e:
                    print(f"处理{window_name}时出错: {str(e)}")
                    import traceback
                    traceback.print_exc()



            try:
                tracker.release()
            except Exception as e:
                print(f"释放{window_name}资源时出错: {str(e)}")

            # 关闭窗口
            if show_window and show:
                try:
                    cv2.destroyWindow(window_name)
                except Exception as e:
                    pass


            # 打印统计结果
            try:
                counts = log_system.get_counts()
                print(f"{window_name}统计结果:")
                print(f"Enter Count: {counts['enter']}")
                print(f"Exit Count: {counts['exit']}")
                print(f"Pass Count: {counts['pass']}")
                print(f"Re-enter Count: {counts['re_enter']}")
            except Exception as e:
                print(f"无法获取{window_name}的统计结果: {e}")

        # ---------- 启动线程 ----------
        # mainloop=current_rtsp_data
        # def start_thread():
        #     thread = threading.Thread(
        #         target=main_loop.run_until_complete,
        #         args=(_process_video_task(current_rtsp_data, main_loop),)
        #     )
        #     thread.start()
        #
        # # 启动主循环
        # start_thread()
        # main_loop.run_forever()

        def _thread_target():
            """线程入口：创建新事件循环"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(_process_video_task(current_rtsp_data))
            finally:
                loop.close()




        # 创建并启动线程
        thread = threading.Thread(target=_thread_target, daemon=True)
        thread.start()
        threading_dict={}

        # threading_dict={
        #     "thread": thread,
        #     "stop_event": stop_event,
        #     "window_name": window_name,
        #     "stream_id": stream_id
        # }

        #self.video_thread_info[queue_index] =threading_dict
       # self.video_rtsp_dict[video_source]=queue_index
        # 返回包含线程信息的字典
        return threading_dict

    def clear_queue(self, queue_index):

        if queue_index in self.video_thread_info:
            queue = self.video_thread_info[queue_index]
            while not queue.empty():
                try:
                    # 使用 get_nowait 避免阻塞
                    queue.get_nowait()
                    # 需要显式标记任务完成（如果队列是用 task_done 跟踪的）
                    queue.task_done()
                except asyncio.QueueEmpty:
                    break

    def get_valid_origin_queue_index(self):
        """
        查询目前哪个队列可以用
        :return:
        """
        print(self.origin_frame_queue_status.items())
        for key, value in self.origin_frame_queue_status.items():
            if value:
                self.origin_frame_queue[key] = queue.Queue(maxsize=10) # 清空这个队列
                self.origin_frame_queue_status[key] = False  # 这个队列已使用
                return key


    def stop_process_video_in_thread(self,rtsp_url):
        try:
            current_rtsp_data=self.rtsp_datas[rtsp_url]
            current_rtsp_data.stop_event.set()


            # # 停止线程
            # self.video_thread_info[queue_index]['stop_event'].set()
            # # 清除队列
            # self.clear_queue(queue_index)

        except Exception as e:
            print('stop error :', str(e))
        #self.stop_event.set()



    def get_valid_queue_index(self):
        """
        查询目前哪个队列可以用
        :return:
        """
        print(self.handle_queue_status.items())
        for key, value in self.handle_queue_status.items():
            if value:
                self.handle_frame[key] = FixedSizeAsyncQueue(maxsize=10)  # 清空这个队列
                self.handle_queue_status[key] = False  # 这个队列已使用
                return key


    def format_data(self, video_datas):
        config_list = [
            {
                "rtsp_video": 'rtsp://localhost:5555/live',
                "points": [[500, 600], [750, 600], [750, 400], [500, 400]]
            }
        ]

        # 设置流并获取MJPEG URL列表
        mjpeg_list = self.setup_streams(config_list, show_windows=True)
        # 打印MJPEG URL列表 (这些URL可以提供给前端显示)
        print("MJPEG流列表:")
        for stream in mjpeg_list:
            print(f"原始URL: {stream['source_url']}")
            print(f"MJPEG URL: {stream['mjpeg_url']}")
            print(f"是否RTSP: {stream['is_rtsp']}")
            print(f"流索引: {stream['stream_index']}")
            print()

    def _encode_frame(self, frame):
        """独立编码函数"""
        # 可在此处添加硬件加速逻辑
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        return buffer.tobytes()


    async def consume_frame(self, rtsp_url):
        # print(threading.current_thread())
        # video_id=0
        print("视频流：{}".format(rtsp_url))

        loop = asyncio.get_event_loop()

        current_rtsp_data=self.rtsp_datas[rtsp_url]
        while not current_rtsp_data.stop_event.is_set():
            print('..1.')
            print('process',str(current_rtsp_data.process_frame_queue.qsize()))
            frame = await current_rtsp_data.process_frame_queue.get()


            # cv2.imshow('process_frame', frame)
            # cv2.waitKey(1)
            # 检查是否支持CUDA
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                gpu_frame = cv2.cuda_GpuMat()
                gpu_frame.upload(frame)
                # 使用GPU编码
                _, buffer = cv2.imencode('.jpg', gpu_frame.download())
            else:
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])

            # 将编码任务提交到线程池
            _frame_cache = await loop.run_in_executor(
                encode_executor,
                self._encode_frame,  # 独立编码函数
                frame
            )



            yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    _frame_cache + b'\r\n'
            )



def clear_database():
    """清空特征数据库"""
    try:
        clear_all_features(cfgs.DB_PATH)
        init_db(cfgs.DB_PATH)
        print("数据库已清空并重新初始化")
        return True
    except Exception as e:
        print(f"清空数据库失败: {e}")
        return False



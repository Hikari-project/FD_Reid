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

from libs.reid_sqlV2 import init_db, add_feature, update_feature, delete_feature, load_features_from_sqlite, get_max_person_id, clear_all_features

import threading
import json
import os
import tempfile
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
import time
import cv2
import asyncio

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
# 是否渲染窗口
show=False
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
import sys
import cv2
import numpy as np
import json
import argparse
import time
from datetime import datetime
from typing import Union, List
from Reid_module import ReIDTracker


# 获取主事件循环
mainloop = asyncio.get_event_loop()
asyncio.set_event_loop(mainloop)


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

    def __init__(self, temp_dir=None, max_reconnect=10, mjpeg_server_port=8554,frame_queue=[asyncio.Queue(maxsize=10)]):
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

        # 已处理的队列
        self.handle_frame = frame_queue

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

    def generate_mjpeg_url(self, url: str, index: int) -> str:
        """
        为流生成MJPEG URL

        Args:
            url: 原始URL
            index: 流索引

        Returns:
            str: MJPEG URL
        """
        # 如果是RTSP URL，尝试转换为MJPEG URL
        if self.is_rtsp_url(url):
            # 简单转换RTSP到HTTP
            mjpeg_url = url.replace("rtsp://", "http://")

            # 尝试提取IP和端口
            match = re.match(r'rtsp://([^:/]+)(?::(\d+))?', url)
            if match:
                ip = match.group(1)
                # 默认使用配置的MJPEG服务器端口
                mjpeg_url = f"http://{ip}:{self.mjpeg_server_port}/live/stream{index}"
            else:
                # 如果无法解析，使用本地MJPEG服务器
                mjpeg_url = f"http://localhost:{self.mjpeg_server_port}/live/stream{index}"
        else:
            # 对于视频文件，使用本地MJPEG服务器
            mjpeg_url = f"http://localhost:{self.mjpeg_server_port}/video/stream{index}"

        return mjpeg_url


    def setup_streams(self, config_list: List[Dict[str, Any]], show_windows=True) -> List[Dict[str, str]]:
        """
        设置流列表

        Args:
            config_list: 配置列表，每个元素包含URL和区域配置
            show_windows: 是否显示视频窗口

        Returns:
            List[Dict[str, str]]: 原始URL和对应MJPEG URL列表
        """
        with self.lock:
            # 清空现有流
            self._clear_streams()

            # 处理新的配置列表
            mjpeg_list = []

            for i, config in enumerate(config_list[:4]):  # 最多处理4个流
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
                config["b1"]=config["passway"][0]


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
                config_path = os.path.join(self.temp_dir, f"stream_config_{i}.json")

                # 保存配置到JSON文件
                with open(config_path, 'w') as f:
                    json.dump(config, f, cls=NumpyEncoder)

                # 生成MJPEG URL
                mjpeg_url = self.generate_mjpeg_url(url, i)

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
                    "mjpeg_url": f"/customer-flow/video_feed?video_id={i}",
                    "is_rtsp": is_rtsp,
                    "stream_index": i
                })

            return mjpeg_list

    def get_stream_info(self, index=None) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        获取流信息

        Args:
            index: 流索引，如果不提供则返回所有流信息

        Returns:
            流信息字典或列表
        """
        with self.lock:
            if index is not None:
                if 0 <= index < len(self.streams):
                    stream = self.streams[index]
                    return {
                        "source_url": stream.url,
                        "mjpeg_url": stream.mjpeg_url,
                        "is_rtsp": stream.is_rtsp,
                        "config_path": stream.config_path,
                        "active": stream.active,
                        "last_update": stream.last_update,
                        "reconnect_count": stream.reconnect_count,
                        "show_window": stream.show_window
                    }
                return None

            return [
                {
                    "source_url": stream.url,
                    "mjpeg_url": stream.mjpeg_url,
                    "is_rtsp": stream.is_rtsp,
                    "config_path": stream.config_path,
                    "active": stream.active,
                    "last_update": stream.last_update,
                    "reconnect_count": stream.reconnect_count,
                    "show_window": stream.show_window
                }
                for stream in self.streams
            ]

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

    def set_show_window(self, index: int, show: bool) -> bool:
        """
        设置是否显示视频窗口

        Args:
            index: 流索引
            show: 是否显示

        Returns:
            bool: 设置是否成功
        """
        with self.lock:
            if 0 <= index < len(self.streams):
                self.streams[index].show_window = show
                return True
            return False

    def get_stream_config_path(self, index: int) -> Optional[str]:
        """
        获取流配置文件路径

        Args:
            index: 流索引

        Returns:
            str: 配置文件路径或None
        """
        with self.lock:
            if 0 <= index < len(self.streams):
                return self.streams[index].config_path
            return None

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

    def _clear_streams(self):
        """清除所有流信息（内部方法）"""
        self.streams = []

    def process_quad_videos(self,video_path1=None, video_path2=None, video_path3=None, video_path4=None,
                            tempDataPath1='v1.json', tempDataPath2='v2.json', tempDataPath3='v3.json',
                            tempDataPath4='v4.json',
                            skip_frames=2, match_thresh=0.15, is_track=True, save_video=True,
                            stop_event=None, stream_manager=None, show_windows=None):
        """
        独立函数，处理1-4个视频（分别使用独立的ReIDTracker实例）

        Args:
            video_path1-4: 视频路径或RTSP URL，可以为None表示不处理该路径
            tempDataPath1-4: 四个视频的临时数据存储路径
            skip_frames: 跳帧数
            match_thresh: 匹配阈值
            is_track: 是否启用跟踪
            save_video: 是否保存结果视频
            stop_event: 停止事件，用于中断处理
            stream_manager: 流管理器实例，用于更新状态
            show_windows: 是否显示窗口的列表，对应每个视频
        """
        # 准备视频路径和配置路径列表
        global mainloop

        video_paths = [video_path1, video_path2, video_path3, video_path4]
        temp_data_paths = [tempDataPath1, tempDataPath2, tempDataPath3, tempDataPath4]

        # 如果未提供show_windows，默认全部显示
        if show_windows is None:
            show_windows = [True, True, True, True]

        # 检查是否需要显示任何窗口
        need_display = any(show_windows)

        # 创建独立的日志系统和跟踪器实例
        log_systems = []
        trackers = []
        videos_active = []
        window_names = []
        video_captures = []
        is_rtsp_list = []

        # 遍历所有视频路径
        for i, (video_path, temp_data_path, show_window) in enumerate(zip(video_paths, temp_data_paths, show_windows)):
            # 跳过为空的视频路径
            if not video_path:
                continue

            # 为此视频创建日志系统和跟踪器
            log_system = LogSystem()
            log_systems.append(log_system)

            tracker = ReIDTracker(log_system=log_system)

            # 检查是否为RTSP流
            is_rtsp = video_path.lower().startswith('rtsp://')
            is_rtsp_list.append(is_rtsp)

            # 设置跟踪器的处理环境
            if tracker.setup_processing(video_path, temp_data_path):
                trackers.append(tracker)
                videos_active.append(True)
                window_names.append(f"Video {i + 1}")

                # 为视频流创建视频捕获对象
                if is_rtsp:
                    print(f"配置RTSP流 {video_path}")
                    # 设置环境变量以使用TCP传输协议
                    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;5000000"
                    cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # 设置缓冲区大小
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))  # 使用H264解码器
                    try:
                        cap.set(cv2.CAP_PROP_TIMEOUT, 10000)  # 设置超时时间(毫秒)
                    except:
                        pass

                    # 尝试读取第一帧验证连接
                    ret, test_frame = cap.read()
                    if ret:
                        print(f"成功读取RTSP流第一帧，尺寸: {test_frame.shape[1]}x{test_frame.shape[0]}")
                        # 释放并重新连接，确保从头开始
                        cap.release()
                        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;5000000"
                        cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # 设置缓冲区大小
                else:
                    cap = cv2.VideoCapture(video_path)

                # 检查是否成功打开
                if not cap.isOpened():
                    print(f"无法打开视频/流 {video_path}")
                    videos_active[-1] = False
                    cap = None

                video_captures.append(cap)
            else:
                print(f"无法设置视频 {video_path} 的处理环境")

        # 如果没有成功设置任何视频，则退出
        if not trackers:
            print("没有成功设置任何视频，退出处理")
            return

        # 设置视频写入器（如果需要保存）
        if save_video:
            for i, (tracker, video_path) in enumerate(zip(trackers, [p for p in video_paths if p])):
                tracker.setup_video_writer(video_path, suffix=f"_processed_{i + 1}")

        # 如果需要显示，创建窗口
        if need_display and show:
            for i, name in enumerate(window_names):
                if show_windows[i]:
                    cv2.namedWindow(name, cv2.WINDOW_NORMAL)

        # 记录帧计数和上次重连时间
        frame_counts = [0] * len(trackers)
        last_reconnect_time = [0] * len(trackers)
        reconnect_interval = 5  # 重连间隔，秒

        # 主循环，只要有一个视频还在处理且没有收到停止信号就继续
        while any(videos_active) and (stop_event is None or not stop_event.is_set()):
            for i, (tracker, active, cap, is_rtsp) in enumerate(
                    zip(trackers, videos_active, video_captures, is_rtsp_list)):
                # 如果收到停止信号，退出循环
                if stop_event is not None and stop_event.is_set():
                    break

                if active and cap is not None:
                    try:
                        # 尝试读取帧
                        ret, frame = cap.read()

                        # 处理读取失败的情况，可能是视频结束或RTSP断开
                        if not ret:
                            current_time = time.time()
                            # 对于RTSP流，尝试重连
                            if is_rtsp:
                                # 更新重连计数
                                if stream_manager:
                                    stream_manager.update_stream_status(i, True, reconnect_increment=True)

                                # 检查是否应该继续重连
                                should_reconnect = True
                                if stream_manager:
                                    should_reconnect = stream_manager.should_reconnect(i)

                                if should_reconnect and current_time - last_reconnect_time[i] > reconnect_interval:
                                    print(f"{window_names[i]}连接断开，尝试重新连接...")
                                    cap.release()
                                    time.sleep(1)  # 等待1秒后尝试重新连接
                                    # 创建新的捕获对象

                                    # 设置环境变量以使用TCP传输协议
                                    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;5000000"
                                    new_cap = cv2.VideoCapture(video_paths[i], cv2.CAP_FFMPEG)
                                    if new_cap.isOpened():
                                        # 对RTSP流进行特殊配置
                                        new_cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
                                        new_cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))
                                        try:
                                            new_cap.set(cv2.CAP_PROP_TIMEOUT, 10000)  # 设置超时时间(毫秒)
                                        except:
                                            pass

                                        # 更新捕获对象
                                        video_captures[i] = new_cap
                                        cap = new_cap
                                        last_reconnect_time[i] = current_time
                                        print(f"{window_names[i]}重新连接成功")

                                        # 尝试读取一帧
                                        ret, frame = cap.read()
                                        if not ret:
                                            print(f"{window_names[i]}重新连接后无法读取帧")
                                            continue
                                    else:
                                        print(f"{window_names[i]}重新连接失败")
                                        last_reconnect_time[i] = current_time
                                        continue
                                else:
                                    # 未达到重连间隔或超过最大重连次数，跳过本次处理
                                    continue
                            else:
                                # 非RTSP流，视频可能已结束
                                print(f"{window_names[i]}读取完毕或出错。")
                                videos_active[i] = False
                                if stream_manager:
                                    stream_manager.update_stream_status(i, False)
                                continue

                        # 增加帧计数
                        frame_counts[i] += 1

                        # 跳帧处理
                        if skip_frames > 0 and frame_counts[i] % skip_frames != 0:
                            continue

                        # 使用跟踪器处理帧
                        processed_frame, info = tracker.process_frame(frame, 0, match_thresh, is_track)
                        # self.handle_frame.put(processed_frame)

                        # 往第i个队列里面插入已处理好的帧
                        asyncio.run_coroutine_threadsafe(self.handle_frame[i].put(processed_frame), mainloop)
                       # print(self.handle_frame.qsize())
                       # print(threading.current_thread())
                        if show:
                            cv2.imshow("test1",processed_frame)
                            cv2.waitKey(1)

                        # 显示处理后的帧
                        if processed_frame is not None:
                            # 只在需要显示窗口时才显示
                            if show:
                                cv2.imshow(window_names[i], processed_frame)

                            # 如果检测到进店事件，更新所有跟踪器的搜索引擎
                            if 'events' in info and any(event.get('type') == 'enter' for event in info['events']):
                                print(f"{window_names[i]}检测到进店事件，更新所有跟踪器的搜索引擎")
                                # 更新所有跟踪器的搜索引擎
                                for update_tracker in trackers:
                                    update_tracker.re_load_search_engine()

                    except Exception as e:
                        print(f"处理{window_names[i]}时出错: {str(e)}")
                        #    traceback.print_exc()

                        # 对于RTSP流错误处理
                        if is_rtsp:
                            if stream_manager:
                                stream_manager.update_stream_status(i, True, reconnect_increment=True)

                            # 检查是否应该继续重连
                            should_reconnect = True
                            if stream_manager:
                                should_reconnect = stream_manager.should_reconnect(i)

                            if not should_reconnect:
                                videos_active[i] = False
                                if stream_manager:
                                    stream_manager.update_stream_status(i, False)
                        else:
                            videos_active[i] = False
                            if stream_manager:
                                stream_manager.update_stream_status(i, False)
            # 只有在需要显示时才检查键盘事件
            if need_display and show:
                # 按 'q' 键退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        # 释放资源
        for cap in video_captures:
            if cap is not None:
                cap.release()
        for i, tracker in enumerate(trackers):
            try:
                tracker.release()
            except Exception as e:
                print(f"释放{window_names[i]}资源时出错: {str(e)}")

        # 关闭所有窗口
        if need_display and show:
            cv2.destroyAllWindows()
        # 打印总结果
        results = []
        for i, log_system in enumerate(log_systems):
            try:
                counts = log_system.get_counts()
                print(f"{window_names[i]}统计结果:")
                print(f"Enter Count: {counts['enter']}")
                print(f"Exit Count: {counts['exit']}")
                print(f"Pass Count: {counts['pass']}")
                print(f"Re-enter Count: {counts['re_enter']}")
                results.append(counts)
            except Exception as e:
                print(f"无法获取{window_names[i]}的统计结果: {e}")
                results.append(None)
        return results
    def start_processing(self, skip_frames=4, match_thresh=0.15, is_track=True, save_video=False):
        """
        开始处理所有设置的视频流
        Args:
            skip_frames: 跳帧数
            match_thresh: 匹配阈值
            is_track: 是否启用跟踪
            save_video: 是否保存结果视频
        Returns:
            bool: 是否成功启动处理
        """
        with self.lock:
            # 如果已经有处理线程在运行，先停止它
            if self.processing_thread and self.processing_thread.is_alive():
                self.stop_processing()

            # 重置停止事件
            self.stop_event.clear()

            # 重置所有流的重连计数
            for i in range(len(self.streams)):
                self.streams[i].reconnect_count = 0

            # 获取流路径和配置文件路径
            stream_paths = [stream.url for stream in self.streams]
            config_paths = [stream.config_path for stream in self.streams]
            show_windows = [stream.show_window for stream in self.streams]

            # 填充不足4个的情况
            while len(stream_paths) < 4:
                stream_paths.append(None)
            while len(config_paths) < 4:
                config_paths.append(None)
            while len(show_windows) < 4:
                show_windows.append(False)

            # 启动处理线程
            self.processing_thread = threading.Thread(
                target=self.process_quad_videos,
                args=(stream_paths[0], stream_paths[1], stream_paths[2], stream_paths[3]),
                kwargs={
                    'tempDataPath1': config_paths[0],
                    'tempDataPath2': config_paths[1],
                    'tempDataPath3': config_paths[2],
                    'tempDataPath4': config_paths[3],
                    'skip_frames': skip_frames,
                    'match_thresh': match_thresh,
                    'is_track': is_track,
                    'save_video': save_video,
                    'stop_event': self.stop_event,
                    'stream_manager': self,  # 传入self以便回调更新状态
                    'show_windows': show_windows
                }
            )

            self.processing_thread.daemon = True
            self.processing_thread.start()
            return True



    def stop_processing(self, timeout=5) -> bool:
        """
        停止视频流处理
        Args:
            timeout: 等待线程结束的最长时间（秒）
        Returns:
            bool: 是否成功停止处理
        """
        with self.lock:
            if not self.stop_event.is_set():
                self.stop_event.set()
                if self.processing_thread and self.processing_thread.is_alive():
                    self.processing_thread.join(timeout=timeout)
                    return not self.processing_thread.is_alive()
            return True

    def is_processing(self) -> bool:
        """
        检查是否有视频流正在处理
        Returns:
            bool: 是否有视频流正在处理
        """
        return self.processing_thread is not None and self.processing_thread.is_alive()



    def format_data(self,video_datas):
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

    def custumer_analysis(self):
        # 准备配置
        config_list = [
            {
                "rtsp_url": 'rtsp://localhost:5555/live',
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

        # 开始处理视频流
        # 注意: 这是非阻塞的，函数会立即返回，处理在后台线程中进行
        # self.start_processing(skip_frames=4, match_thresh=0.15, is_track=True)



    async def consume_frame(self,video_id):
       # print(threading.current_thread())
        #video_id=0
        print("视频流：{}".format(video_id))
        while True:
            print('...1')
            frame = await self.handle_frame[video_id].get()
            if show:
                cv2.imshow('frame', frame)
                cv2.waitKey(1)

            _, buffer = cv2.imencode('.jpg', frame)
            _frame_cache = buffer.tobytes()
            yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    _frame_cache + b'\r\n'
            )

    async def consume_frame_queue(self,frame_queue):
       # print(threading.current_thread())
       # 准备配置
       config_list = [
           {
               "rtsp_url": 'rtsp://localhost:5558/live',
               "points": [[500, 600], [750, 600], [750, 400], [500, 400]]
           }
       ]

       # 设置流并获取MJPEG URL列表
       mjpeg_list =self.setup_streams(config_list, show_windows=True)
       # 打印MJPEG URL列表 (这些URL可以提供给前端显示)
       print("MJPEG流列表:")
       for stream in mjpeg_list:
           print(f"原始URL: {stream['source_url']}")
           print(f"MJPEG URL: {stream['mjpeg_url']}")
           print(f"是否RTSP: {stream['is_rtsp']}")
           print(f"流索引: {stream['stream_index']}")
           print()

       # 开始处理视频流
       # 注意: 这是非阻塞的，函数会立即返回，处理在后台线程中进行
       self.start_processing(skip_frames=4, match_thresh=0.15, is_track=True)

       while True:
            frame = await frame_queue.get()
            # cv2.imshow('frame', frame)
            # cv2.waitKey(1)
            _, buffer = cv2.imencode('.jpg', frame)
            _frame_cache = buffer.tobytes()
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



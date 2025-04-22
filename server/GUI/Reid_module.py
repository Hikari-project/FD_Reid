# -*- coding:utf-8 -*-
"""
@Author: self-798
@Contact: 123090233@link.cuhk.edu.cn
@Version: 4.0
@Date: 2025/4/5 
@Describe:
加入log系统，加入数据库，重构为类结构，改进进出店检测逻辑
"""

from datetime import datetime
import re
import gc
import os
import cv2
import sys
# 确保能找到项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
import torch
sys.path.append('../')
import json
import numpy as np
from collections import defaultdict
from Algorithm.reid_outer_api import ReidPipeline
from log.log import LogSystem, GlobalCounter
from Algorithm.libs.detect.area_boundary_detect import area_boundary_detect
from Algorithm.libs.IDdata.IDDict import IDDict
import Algorithm.libs.config.model_cfgs as cfgs
import sqlite3
from ultralytics.utils.plotting import Annotator, colors
from libs.reid_sqlV2 import init_db, add_feature, update_feature, delete_feature, load_features_from_sqlite, get_max_person_id, clear_all_features
from body_quality import BodyCompletenessDetector
from Algorithm.libs.IDdata.TrackManager import TrackManager, TrackInfo
from shapely.geometry import Point, LineString, Polygon
import time
import argparse
from dataclasses import dataclass
from typing import Dict, Optional
from ultralytics import YOLO

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
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

# 确保能找到项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append('../')

from json import JSONEncoder
import threading
import json
import os
import tempfile
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
import time
import cv2

# 保存原始的 dumps 函数
original_dumps = json.dumps

# 创建 monkey patch 函数替换原始函数
def np_dumps(obj, *args, **kwargs):
    kwargs['cls'] = NumpyEncoder
    return original_dumps(obj, *args, **kwargs)
# 替换 json.dumps 函数
json.dumps = np_dumps

class ReIDTracker:
    def __init__(self, log_system=None):
        """初始化ReID跟踪器"""
        self.reid_pipeline = None
        self.track_manager = None
        self.db_path = cfgs.DB_PATH
        self.log_system = log_system if log_system else LogSystem()
        self.torch_device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

        print(f"当前使用的设备: {self.torch_device}")
        self.cuda_available = torch.cuda.is_available()
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

        if self.cuda_available:
            self.model = YOLO(cfgs.YOLO_MODEL_PATH_PT, task="detect").to(self.torch_device)
        else:
            self._model = YOLO(cfgs.YOLO_MODEL_PATH, task="detect").to(self.device)

        # 初始化数据库
        try:
            init_db(self.db_path)
            self.log_system.log_system_event("system_init", {
                "status": "success",
                "db_path": self.db_path
            })
        except Exception as e:
            self.log_system.log_system_event("db_init_error", {
                "error": str(e),
                "db_path": self.db_path
            })

        # 人员质量检测器
        self.detector = BodyCompletenessDetector()

        # 跟踪相关变量
        self.track_history = defaultdict(list)
        self.qualityl = [0.0 for _ in range(10000)]

        # 区域和边界定义
        self.area_polygon = None
        self.entry_line = None
        self.side_lines = []
        self.rect_points = []

        # 对象状态
        self.object_status = {}
        self.counted_objects = set()
        self.last_seen = {}
        self.current_in_roi = set()
        self.previous_in_roi = set()
        base_feat_lists, base_idx_lists = load_features_from_sqlite(self.db_path, cfgs.DB_NAME, dims=1280)
        print(f'根据数据库中内容，加载行人数量{len(base_feat_lists)}')

        # 初始化ReID Pipeline
        self.reid_pipeline = ReidPipeline(base_feat_lists=base_feat_lists, base_idx_lists=base_idx_lists, dims=1280)
    def _create_track_info(self, track_id: int) -> dict:
        """创建跟踪信息字典"""
        return {
            "track_id": track_id,          # 跟踪ID
            "person_id": -1,               # 人员ID
            "quality": 0.0,                # 图像质量
            "last_seen": 0.0,              # 最后出现时间
            "feature": None,               # 特征向量
            "is_reid": False,              # 是否已重识别
            "location": "unknown",         # 位置状态
            "last_reid": 0.0               # 最后重识别时间
        }

    def _get_box_center(self, box):
        """计算边界框下方中心点坐标"""
        x1, y1, x2, y2 = box
        return (x1 + x2) / 2, y2  # 返回下框中点

    def _convert_boundary_format(self, data):
        """转换边界线格式
        输入: 嵌套数组格式的JSON数据
        输出: [x1,y1,x2,y2]格式的边界线数组
        """
        b1 = [
            data['b1'][0][0], data['b1'][0][1],  # x1,y1
            data['b1'][1][0], data['b1'][1][1]   # x2,y2
        ]

        b2 = [
            data['b2'][0][0], data['b2'][0][1],
            data['b2'][1][0], data['b2'][1][1]
        ]

        b3 = [
            data['g2'][0][0], data['g2'][0][1],  # 使用g2作为b3
            data['g2'][1][0], data['g2'][1][1]
        ]

        points = data['points']

        return b1, b2, b3, points

    def _setup_area_boundaries(self, json_data):
        """设置区域边界"""
        self.rect_points = [(point[0], point[1]) for point in json_data["points"]]

        # 创建shapely Polygon对象用于区域检测
        self.area_polygon = Polygon(self.rect_points)

        # 定义进店线(点0到点1)
        self.entry_line = LineString([self.rect_points[0], self.rect_points[1]])

        # 获取所有边，除了入口边(points[0]到points[1])
        self.side_lines = []
        num_points = len(self.rect_points)
        for i in range(1, num_points):
            # 从第二个点开始，依次连接到最后一个点和第一个点
            next_point = self.rect_points[(i + 1) % num_points]
            self.side_lines.append(LineString([self.rect_points[i], next_point]))

    def _draw_rois(self, frame, json_data):
        """绘制门店前部区域"""
        # 从一维数组转换为元组对格式
        b3 = [tuple(p) for p in json_data['b1']]  # [(x1,y1), (x2,y2)]
        b2 = [tuple(p) for p in json_data['b2']]
        b1 = [tuple(p) for p in json_data['g2']]  # g2作为b3
        points = np.array(json_data['points'], np.int32).reshape((-1, 1, 2))
        overlay = frame.copy()
        cv2.fillPoly(overlay, [points], color=(128, 128, 128))

        alpha = 0.5
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        cv2.line(frame, b3[0], b3[1], (255, 0, 0), 2)  # B3

    def _draw_match(self, image, boxes, labels, confs):
        """绘制匹配框和置信度"""
        for bbox, label, conf in zip(boxes, labels, confs):
            annotator = Annotator(image, example=str(cfgs.YOLO_LABELS))
            # 如果label是元组,说明包含person_id和state
            if isinstance(label, tuple):
                person_id, state = label
                label_text = f"id:{person_id} {state} {conf:.2f}"
            else:
                label_text = f"{label} {conf:.2f}"
            annotator.box_label(bbox, label_text, color=colors(label, True))

            # 绘制轨迹
            if label in self.track_history:
                for i in range(1, len(self.track_history[label])):
                    # 为不同的ID使用不同的颜色
                    color = (
                        hash(str(label) + "r") % 256,
                        hash(str(label) + "g") % 256,
                        hash(str(label) + "b") % 256
                    )
                    cv2.line(image,
                            self.track_history[label][i-1],
                            self.track_history[label][i],
                            color, 2)

        return image

    def setup_processing(self, video_path=None, tempDataPath='v1.json'):
        """
        设置处理环境，初始化必要的组件

        参数:
            video_path: 视频文件路径或RTSP URL，如不提供则只配置环境不打开视频
            tempDataPath: 包含ROI和边界信息的JSON文件路径

        返回:
            success: bool, 设置是否成功
        """
        # 检查JSON配置文件是否存在，不存在则创建默认配置
        if not os.path.exists(tempDataPath):
            # 创建默认配置
            default_json_data = {
                "b1": [[100, 400], [500, 400]],
                "b2": [[150, 300], [550, 300]],
                "g2": [[200, 200], [600, 200]],
                "points": [[100, 200], [600, 200], [600, 400], [100, 400]]
            }
            with open(tempDataPath, 'w') as f:
                json.dump(default_json_data, f)
            print(f"创建了默认配置文件: {tempDataPath}")

        # 读取JSON文件
        try:
            with open(tempDataPath, 'r') as f:
                self.json_data = json.load(f)

            # 设置区域边界
            self._setup_area_boundaries(self.json_data)
        except Exception as e:
            print(f"读取边界配置出错: {e}")
            return False

        # 初始化跟踪管理器
        self.track_manager = TrackManager(max_age=10)

        # 初始化边界检测和ID管理
        b1, b2, b3, points = self._convert_boundary_format(self.json_data)
        self.boundary_detector = area_boundary_detect(b1, b2, b3)
        self.id_dict = IDDict(max_age=5, area_boundary=self.boundary_detector.get_location_type,
                            log_system=self.log_system, b1=b1)

        # 加载特征库
        self.base_feat_lists, self.base_idx_lists = load_features_from_sqlite(self.db_path, cfgs.DB_NAME, dims=1280)
        print(f'根据数据库中内容，加载行人数量{len(self.base_feat_lists)}')

        # 初始化或更新ReID Pipeline
        if not hasattr(self, 'reid_pipeline') or self.reid_pipeline is None:
            self.reid_pipeline = ReidPipeline(base_feat_lists=self.base_feat_lists,
                                            base_idx_lists=self.base_idx_lists, dims=1280)
        else:
            self.reid_pipeline.reload_search_engine(
                base_feat_lists=np.array(self.base_feat_lists),
                base_idx_lists=list(self.base_idx_lists),
                dims=1280
            )

        # 初始化/重置计数器和状态
        self.frame_count = 0
        self.people_count = get_max_person_id(self.db_path)
        self.pre = self.people_count

        # 如果提供了视频路径，打开视频
        if video_path:
            # 判断是否为RTSP URL
            is_rtsp = video_path.lower().startswith('rtsp://')

            if not is_rtsp and not os.path.exists(video_path):
                print(f"错误: 视频文件不存在 - {video_path}")
                return False

            # 设置环境变量以使用TCP传输协议（针对RTSP）
            if is_rtsp:
                print(f"配置RTSP流: {video_path}")
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;5000000"

            # 打开视频流
            self.cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)

            # 对RTSP流进行特殊配置
            if is_rtsp:
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # 设置缓冲区大小
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H','2','6','4'))  # 使用H264解码器
                try:
                    self.cap.set(cv2.CAP_PROP_TIMEOUT, 10000)  # 设置超时时间(毫秒)
                except:
                    pass

            if not self.cap.isOpened():
                print(f"无法打开视频: {video_path}")
                return False

            # 获取视频属性
            self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.video_fps = int(self.cap.get(cv2.CAP_PROP_FPS))

            # 对于RTSP流，不尝试获取总帧数
            if not is_rtsp:
                self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            else:
                self.total_frames = 0  # RTSP流无法获取总帧数

            # 尝试读取第一帧验证连接
            if is_rtsp:
                ret, test_frame = self.cap.read()
                if not ret:
                    print(f"无法从RTSP流读取帧: {video_path}")
                    return False
                print(f"成功读取RTSP流第一帧，尺寸: {test_frame.shape[1]}x{test_frame.shape[0]}")
                # 释放并重新连接，确保从头开始
                self.cap.release()
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;5000000"
                self.cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # 设置缓冲区大小

        return True

    def setup_video_writer(self, video_path=None, output_dir="processed",suffix=""):
        """
        设置视频写入器

        参数:
            video_path: 源视频路径，用于生成输出文件名
            output_dir: 输出目录

        返回:
            success: bool, 设置是否成功
        """
        if not hasattr(self, 'video_width') or not hasattr(self, 'video_height'):
            print("错误: 未设置视频宽高，请先调用setup_processing")
            return False

        # 设置保存路径
        if video_path:
            save_dir = os.path.join(os.path.dirname(video_path), output_dir)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
        else:
            save_dir = output_dir
            video_name = f"stream_{int(time.time())}"

        os.makedirs(save_dir, exist_ok=True)
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            return False

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 提取文件名和扩展名以添加后缀
        base_name, extension = os.path.splitext(video_path)
        output_path = f"{base_name}_processed{suffix}{extension}"

        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(save_dir, f"{video_name}_{timestamp}_processed.mp4")

        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        print(f"视频将保存至: {output_path}")

        return True

    def process_frame(self, frame=None, skip_frames=2, match_thresh=0.5, is_track=True):
        """
        处理单帧图像

        参数:
            frame: 要处理的帧，如果为None则从已打开的视频源读取
            skip_frames: 跳帧数
            match_thresh: 匹配阈值
            is_track: 是否进行跟踪

        返回:
            output_frame: 处理后的帧
            info: 包含当前帧处理信息的字典
        """
        # 如果没有提供帧且有视频源，则从视频源读取
        if frame is None:
            if not hasattr(self, 'cap') or self.cap is None:
                print("错误: 未初始化视频源，请先调用setup_processing并提供视频路径")
                return None, {'error': 'No video source initialized'}

            ret, frame = self.cap.read()
            if not ret:
                return None, {'error': 'End of video'}

        # 确保已经设置了处理环境
        if not hasattr(self, 'id_dict') or self.id_dict is None:
            print("错误: 未初始化处理环境，请先调用setup_processing")
            return None, {'error': 'Processing environment not initialized'}

        # 开始计时
        start_time = time.time()
        self.frame_count += 1

        # 准备返回信息
        info = {
            'frame_count': self.frame_count,
            'tracks': [],
            'events': []
        }

        # 跳帧处理
        if skip_frames > 0 and self.frame_count % skip_frames != 0:
            return frame, {'skipped': True, 'frame_count': self.frame_count}

        # 清除当前帧的ROI内ID集合
        self.current_in_roi = set()

        # 检查行人数量是否变化
        current_person_count = get_max_person_id(self.db_path)
        if self.pre != current_person_count:
            print('当前行人库中的行人数量：', current_person_count)
            self.pre = current_person_count

        # 目标检测和跟踪
        # boxes, track_ids, labels, confs = self.reid_pipeline.detect(
        #     frame,
        #     class_idx_list=self.reid_pipeline._target_class_idx_list,
        #     format='video',
        #     is_track=is_track
        # )
        results = self.model.track(
            frame,
            persist=True,
            tracker=cfgs.YOLO_TRACKER_TYPE,
            conf=0.2,
            iou=0.4,
            classes=self.reid_pipeline._target_class_idx_list
        )

        # Extract detection data from results
        boxes = []
        track_ids = []
        labels = []
        confs = []

        if results and len(results) > 0:
            result = results[0]  # Get the first result object
            if result.boxes and len(result.boxes) > 0:
                boxes = result.boxes.xyxy.cpu().numpy()  # Get bounding boxes
                confs = result.boxes.conf.cpu().numpy()  # Get confidence scores
                if result.boxes.cls.numel() > 0:
                    labels = result.boxes.cls.int().cpu().numpy()  # Get class labels
                if hasattr(result.boxes, 'id') and result.boxes.id is not None:
                    track_ids = result.boxes.id.int().cpu().numpy()  # Get track IDs
                else:
                    track_ids = np.arange(len(boxes))  # Fallback if tracking IDs not available
        # 更新跟踪
        self.track_manager.update_tracks(track_ids if track_ids is not None else [])

        had_search_trackid_list = []

        # 如果启用了跟踪
        if is_track and track_ids is not None and len(track_ids) > 0:
            for bbox, track_id, conf in zip(boxes, track_ids, confs):
                # 质量检测
                if bbox[3] - bbox[1] < 50 or bbox[2] - bbox[0] < 50 or conf < 0.5:
                    continue

                # 获取ROI
                x1, y1, x2, y2 = map(int, bbox)
                roi_frame = frame[y1:y2, x1:x2].copy()

                # 完整度检测
                quality_score = conf
                self.track_manager.update_track_info(track_id, quality=quality_score)
                track_info = self.track_manager.get_track_info(track_id)

                # 创建当前点坐标
                x_center, y_center = self._get_box_center(bbox)
                curr_point = Point(x_center, y_center)

                # 检查点是否在区域内
                curr_in_area = self.area_polygon.contains(curr_point)

                # 如果在ROI区域内，添加到当前帧的ROI内ID集合
                if curr_in_area:
                    self.current_in_roi.add(track_id)

                # 更新最后可见时间
                self.last_seen[track_id] = time.time()

                # 更新轨迹历史和区域状态
                self._update_track_history_and_status(track_id, x_center, y_center, curr_in_area, curr_point, info)

                # 位置更新 - 使用IDDict进行状态管理
                person_id = track_info.person_id if track_info.person_id != -1 else track_id
                event = self.id_dict.add_update(track_id, 'cam1', x_center, y_center, reid_id=person_id)

                # 处理事件和ReID
                if event:
                    self._process_event_and_reid(event, track_id, track_info, frame, bbox,
                                            quality_score, conf, match_thresh, info)
                    info['events'].append(event)

                # 获取最新的track_info（可能在处理事件过程中有更新）
                track_info = self.track_manager.get_track_info(track_id)

                # 添加到跟踪列表
                had_search_label = track_info.person_id if track_info.person_id != -1 else -1
                had_search_trackid_list.append([bbox, had_search_label, conf])

                # 添加到返回信息
                info['tracks'].append({
                    'track_id': track_id,
                    'person_id': had_search_label,
                    'box': bbox,
                    'conf': conf,
                    'position': (x_center, y_center),
                    'in_area': curr_in_area
                })

            output_frame = self._draw_match(frame.copy(),
                    [row[0] for row in had_search_trackid_list],  # boxes
                    [row[1] for row in had_search_trackid_list],  # labels(id,status)
                    [row[2] for row in had_search_trackid_list])  # confs
        else:
            output_frame = frame.copy()

        # 计算FPS
        end_time = time.time()
        fps_current = 1.0 / (end_time - start_time)
        info['fps'] = fps_current

        # 绘制ROI区域
        self._draw_rois(output_frame, self.json_data)

        # 在处理后的图片上显示信息
        cv2.putText(output_frame, f'FPS:{fps_current:.2f}', (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # 显示计数信息
        counts = self.log_system.get_counts()
        cv2.putText(output_frame, f"Enter: {counts['enter']}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(output_frame, f"Exit: {counts['exit']}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(output_frame, f"Pass: {counts['pass']}", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(output_frame, f"Re_enter: {counts['re_enter']}", (30, 270), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(output_frame, f"Area: {len(self.current_in_roi)}", (30, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 保存视频
        if hasattr(self, 'video_writer') and self.video_writer is not None:
            self.video_writer.write(output_frame)

        # 定期执行内存清理
        if self.frame_count % 500 == 0:
            self._cleanup_old_data()

        info['counts'] = counts
        return output_frame, info

    def _update_track_history_and_status(self, track_id, x_center, y_center, curr_in_area, curr_point, info):
        """更新轨迹历史和区域状态"""
        if track_id in self.track_history:
            # 获取上一个状态
            if track_id in self.object_status:
                prev_in_area = self.object_status[track_id]['in_area']
            else:
                prev_in_area = False

            self.track_history[track_id].append((int(x_center), int(y_center)))
            # 限制轨迹长度
            if len(self.track_history[track_id]) > 30:
                self.track_history[track_id].pop(0)

            # 初始化或获取对象状态
            if track_id not in self.object_status:
                self.object_status[track_id] = {
                    'in_area': curr_in_area,
                    'first_in_area_point': None,
                    'last_in_area_point': None,
                    'entered_from': None,
                    'exited_from': None
                }

            status = self.object_status[track_id]

            # 目标刚进入区域
            if curr_in_area and not prev_in_area:
                status['in_area'] = True
                status['first_in_area_point'] = curr_point

                # 计算到各边的距离
                entry_dist = self.entry_line.distance(curr_point)
                side_dists = [line.distance(curr_point) for line in self.side_lines]

                # 找到最小距离的边
                all_dists = [entry_dist] + side_dists
                min_dist_idx = all_dists.index(min(all_dists))

                if min_dist_idx == 0:
                    status['entered_from'] = 'entry'
                else:
                    status['entered_from'] = f'side_{min_dist_idx-1}'

                print(f"ID {track_id} 进入区域，从 {status['entered_from']} 进入")
                # 添加事件到返回信息
                info['events'].append({
                    'type': 'area_enter',
                    'track_id': track_id,
                    'entry_point': status['entered_from']
                })

            # 目标在区域内，更新最后一个区域内点
            if curr_in_area:
                status['last_in_area_point'] = curr_point

            # 目标离开区域
            if prev_in_area and not curr_in_area:
                status['in_area'] = False

                # 使用最后一个区域内点计算离开边
                if status['last_in_area_point'] is not None:
                    last_point = status['last_in_area_point']

                    # 计算到各边的距离
                    entry_dist = self.entry_line.distance(last_point)
                    side_dists = [line.distance(curr_point) for line in self.side_lines]

                    # 找到最小距离的边
                    all_dists = [entry_dist] + side_dists
                    min_dist_idx = all_dists.index(min(all_dists))

                    if min_dist_idx == 0:
                        status['exited_from'] = 'entry'
                    else:
                        status['exited_from'] = f'side_{min_dist_idx-1}'

                    print(f"ID {track_id} 离开区域，从 {status['exited_from']} 离开")
                    # 添加事件到返回信息
                    info['events'].append({
                        'type': 'area_exit',
                        'track_id': track_id,
                        'exit_point': status['exited_from']
                    })

                    # 只有在完整记录了进入和离开时才进行计数
                    if track_id not in self.counted_objects and status['entered_from'] is not None:
                        track_info = self.track_manager.get_track_info(track_id)
                        person_id = track_info.person_id if track_info.person_id != -1 else track_id

                        # 过店逻辑保持不变
                        if status['entered_from'] and status['entered_from'].startswith('side') and \
                        status['exited_from'] and status['exited_from'].startswith('side'):
                            # 从侧边进入，从侧边出去 = 过店
                            print(f"人员内部编码： {person_id} 过店")
                            self.log_system.log_business_event({
                                "event_type": "pass",
                                "person_id": person_id,
                                "reid_id": person_id,
                                "camera_id": 'cam1',
                                "old_state": "passing",
                                "new_state": "passed"
                            })
                            # 添加事件到返回信息
                            info['events'].append({
                                'type': 'pass',
                                'track_id': track_id,
                                'person_id': person_id
                            })

                        self.counted_objects.add(track_id)
        else:
            # 新的跟踪ID
            self.track_history[track_id] = [(int(x_center), int(y_center))]
            self.object_status[track_id] = {
                'in_area': curr_in_area,
                'first_in_area_point': curr_point if curr_in_area else None,
                'last_in_area_point': curr_point if curr_in_area else None,
                'entered_from': None,
                'exited_from': None
            }

            if curr_in_area:
                # 如果第一次检测就在区域内，计算最近边
                entry_dist = self.entry_line.distance(curr_point)
                side_dists = [line.distance(curr_point) for line in self.side_lines]

                all_dists = [entry_dist] + side_dists
                min_dist_idx = all_dists.index(min(all_dists))

                if min_dist_idx == 0:
                    self.object_status[track_id]['entered_from'] = 'entry'
                else:
                    self.object_status[track_id]['entered_from'] = f'side_{min_dist_idx-1}'

                print(f"新ID {track_id} 在区域内首次出现，假设从 {self.object_status[track_id]['entered_from']} 进入")
                # 添加事件到返回信息
                info['events'].append({
                    'type': 'area_new_detection',
                    'track_id': track_id,
                    'entry_point': self.object_status[track_id]['entered_from']
                })

    def _process_event_and_reid(self, event, track_id, track_info, frame, bbox, quality_score, conf, match_thresh, info):
        """处理事件和ReID"""
        event_type = event['type']
        info['events'].append(event)

        Res = -1  # 默认为新人员

        if event_type == 'enter':
            if conf > 0.8:
                # ReID处理
                if not track_info.is_reid:
                    _feat_list = self.reid_pipeline.SingleExtract(frame, bbox)
                    # Save extracted person image
                    person_crop = frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]
                    os.makedirs('extracted_persons2', exist_ok=True)
                    timestamp = int(time.time() * 1000)
                    Res, dist = self.reid_pipeline.VecPair(_feat_list, match_thresh)
                    # save_path = f'extracted_persons2/person_{track_id}_{timestamp}_{Res}.jpg'
                    # cv2.imwrite(save_path, person_crop)
                    if Res == -1:
                        # 新人员
                        self.people_count += 1
                        self.track_manager.update_track_info(
                            track_id,
                            person_id=self.people_count,
                            feature=_feat_list,
                            is_reid=True,
                            quality=quality_score + conf*0.5
                        )
                        self.qualityl[track_id] = quality_score + conf*0.5
                        self.base_feat_lists.append(_feat_list)
                        self.base_idx_lists.append(self.people_count)
                        add_feature(self.db_path, self.people_count, np.array([_feat_list]))
                        self.reid_pipeline.reload_search_engine(
                            base_feat_lists=np.array(self.base_feat_lists),
                            base_idx_lists=list(self.base_idx_lists),
                            dims=1280
                        )
                        self.pre = get_max_person_id(self.db_path)
                        print(f'当前行人库中的行人数量：{self.pre}')
                    else:
                        # 匹配到已有人员
                        # 检查Res索引是否有效
                        if Res >= 0 and Res < len(self.base_idx_lists):
                            person_id = self.base_idx_lists[Res]
                            print(f"Track {track_id} 匹配到已有人员 {person_id}，距离: {dist:.2f}")
                            if track_info.person_id != -1 and dist < match_thresh - 0.05:
                                self.track_manager.update_track_info(
                                    track_id,
                                    person_id=self.base_idx_lists[Res],
                                    feature=_feat_list
                                )
                            self.track_manager.update_track_info(
                                track_id,
                                person_id=self.base_idx_lists[Res],
                                feature=_feat_list
                            )
                        else:
                            print(f"警告：Res={Res}，超出base_idx_lists范围（长度={len(self.base_idx_lists)}）")
                            # 将Res重置为-1，视为新人员
                            Res = -1
                            # 新人员处理逻辑
                            self.people_count += 1
                            self.track_manager.update_track_info(
                                track_id,
                                person_id=self.people_count,
                                feature=_feat_list,
                                is_reid=True,
                                quality=quality_score + conf*0.5
                            )
                            self.qualityl[track_id] = quality_score + conf*0.5
                            self.base_feat_lists.append(_feat_list)
                            self.base_idx_lists.append(self.people_count)
                            add_feature(self.db_path, self.people_count, np.array([_feat_list]))
                            self.reid_pipeline.reload_search_engine(
                                base_feat_lists=np.array(self.base_feat_lists),
                                base_idx_lists=list(self.base_idx_lists),
                                dims=1280
                            )
                            self.pre = get_max_person_id(self.db_path)
                            print(f'当前行人库中的行人数量：{self.pre}')
                else:
                    quality = quality_score + conf*0.5
                    if quality > self.qualityl[track_id] + 0.1:
                        _feat_list = self.reid_pipeline.SingleExtract(frame, bbox)
                        track_info = self.track_manager.get_track_info(track_id)
                        quality = quality_score + conf*0.5

                        # 更新track信息
                        self.track_manager.update_track_info(
                            track_id,
                            feature=_feat_list,
                            quality=quality
                        )
                        self.qualityl[track_id] = quality
                        # 如果已经匹配到人物ID，更新特征
                        if track_info.person_id != -1:
                            update_feature(self.db_path, track_info.person_id, _feat_list)

            # 获取最新的track_info信息
            track_info = self.track_manager.get_track_info(track_id)
            person_id = track_info.person_id if track_info.person_id != -1 else track_id

            if Res == -1:
                print(f"人员内部编码： {event['person_id']} 进店")
                self.log_system.log_business_event({
                    "event_type": "enter",
                    "person_id": event['person_id'],
                    "reid_id": person_id,
                    "camera_id": 'cam1',
                    "old_state": event['old_state'],
                    "new_state": event['new_state']
                })
            else:
                print(f"人员内部编码： {person_id} 重复进店")
                self.log_system.log_business_event({
                    "event_type": "re_enter",
                    "person_id": person_id,
                    "reid_id": person_id,
                    "camera_id": 'cam1',
                    "old_state": event['old_state'],
                    "new_state": event['new_state']
                })
        elif event_type == 'exit':
            print(f"人员内部编码： {event['person_id']} 出店")
            track_info = self.track_manager.get_track_info(track_id)
            person_id = track_info.person_id if track_info.person_id != -1 else track_id
            self.log_system.log_business_event({
                "event_type": "exit",
                "person_id": event['person_id'],
                "reid_id": person_id,
                "camera_id": 'cam1',
                "old_state": event['old_state'],
                "new_state": event['new_state']
            })

    def _cleanup_old_data(self):
        """清理长时间未见的数据以节省内存及未使用的特征"""
        current_time = time.time()

        # 清理长时间未见的轨迹
        ids_to_remove = []
        for track_id, last_time in self.last_seen.items():
            if current_time - last_time > 30:  # 30秒未见的对象
                ids_to_remove.append(track_id)

        # 移除过期数据
        for track_id in ids_to_remove:
            if track_id in self.track_history:
                del self.track_history[track_id]
            if track_id in self.last_seen:
                del self.last_seen[track_id]
            if track_id in self.object_status:
                del self.object_status[track_id]
            if track_id in self.counted_objects:
                self.counted_objects.remove(track_id)
            # self.track_manager.remove_track(track_id)

        # 如果有移除的轨迹，打印信息
        if len(ids_to_remove) > 0:
            print(f"清理了 {len(ids_to_remove)} 个长时间未见的轨迹")

        # 清理长时间未使用的特征
        try:
            # 连接数据库
            conn = sqlite3.connect(self.db_path,timeout=10,check_same_thread=False)
            cursor = conn.cursor()

            # 获取当前时间戳
            thirty_mins_ago = int(time.time() - 30 * 60)  # 30分钟前的时间戳

            # 查询长时间未使用的特征
            cursor.execute(f"""
                SELECT person_id FROM {cfgs.DB_NAME} 
                WHERE last_used < ? AND is_locked = 0
            """, (thirty_mins_ago,))

            unused_features = cursor.fetchall()
            unused_ids = [row[0] for row in unused_features]

            if unused_ids:
                # 删除这些特征
                for person_id in unused_ids:
                    delete_feature(self.db_path, person_id)

                # 从内存中的特征列表中删除
                if self.base_feat_lists and self.base_idx_lists:
                    # 创建新的特征列表和ID列表
                    new_feat_lists = []
                    new_idx_lists = []

                    for feat, idx in zip(self.base_feat_lists, self.base_idx_lists):
                        if idx not in unused_ids:
                            new_feat_lists.append(feat)
                            new_idx_lists.append(idx)

                    # 更新内存中的特征列表
                    self.base_feat_lists = new_feat_lists
                    self.base_idx_lists = new_idx_lists

                    # 重新加载搜索引擎
                    if self.reid_pipeline:
                        self.reid_pipeline.reload_search_engine(
                            base_feat_lists=np.array(self.base_feat_lists),
                            base_idx_lists=list(self.base_idx_lists),
                            dims=1280
                        )

                print(f"清理了 {len(unused_ids)} 个长时间未使用的特征 (IDs: {unused_ids})")

            # 更新所有剩余特征的最后使用时间
            cursor.execute(f"""
                UPDATE {cfgs.DB_NAME}
                SET last_used = ?
                WHERE last_used < ? AND is_locked = 1
            """, (int(time.time()), thirty_mins_ago))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"清理特征库时出错: {e}")

    def re_load_search_engine(self):
        """重新加载搜索引擎"""
        self.base_feat_lists, self.base_idx_lists = load_features_from_sqlite(self.db_path, cfgs.DB_NAME, dims=1280)
        print(f'根据数据库中内容，加载行人数量{len(self.base_feat_lists)}')
        self.reid_pipeline.reload_search_engine(
            base_feat_lists=np.array(self.base_feat_lists),
            base_idx_lists=list(self.base_idx_lists),
            dims=1280
        )
        print("搜索引擎已重新加载")

    def release(self):
        """释放资源"""
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()

        if hasattr(self, 'video_writer') and self.video_writer:
            self.video_writer.release()

        cv2.destroyAllWindows()
        print("资源已释放")

    def run(self, video_path, tempDataPath='v1.json', skip_frames=2, match_thresh=0.5, is_track=True, save_video=True):
        """
        处理视频（保持原有功能不变，但使用单帧处理接口）
        """
        # 设置处理环境
        if not self.setup_processing(video_path, tempDataPath):
            return

        # 设置视频写入器（如果需要保存）
        if save_video:
            self.setup_video_writer(video_path)

        # 创建窗口
        cv2.namedWindow("Processed Frame", cv2.WINDOW_NORMAL)

        try:
            # 主循环
            while True:
                # 使用单帧处理接口
                frame, info = self.process_frame(None, skip_frames, match_thresh, is_track)

                if frame is None:
                    print("视频读取完毕或出错。")
                    break

                # 如果是跳帧，则继续
                if 'skipped' in info and info['skipped']:
                    continue

                # 显示处理后的帧
                cv2.imshow("Processed Frame", frame)

                # 按 'q' 键退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            # 释放资源
            self.release()

        # 打印总结果
        counts = self.log_system.get_counts()
        print(f"Enter Count: {counts['enter']}")
        print(f"Exit Count: {counts['exit']}")
        print(f"Pass Count: {counts['pass']}")
        print(f"Re-enter Count: {counts['re_enter']}")

# 在文件末尾添加主函数入口
if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='ReID 跟踪系统')
    parser.add_argument('--video_path', type=str, required=True, help='视频文件路径或RTSP流地址')
    parser.add_argument('--temp_data_path', type=str, default='v1.json', help='配置文件路径')
    parser.add_argument('--skip_frames', type=int, default=2, help='跳帧数量')
    parser.add_argument('--match_thresh', type=float, default=0.25, help='匹配阈值')
    parser.add_argument('--save_video', action='store_true', help='是否保存处理后的视频')
    parser.add_argument('--clear_db', action='store_true', help='是否清空数据库')
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 确认YOLO模型文件存在
    yolo_model_pt = os.path.join(project_root, 'GUI/models/yolov8x.pt')
    if not os.path.exists(yolo_model_pt):
        print(f"模型文件 {yolo_model_pt} 不存在，使用默认路径")
    else:
        print(f"找到模型文件 {yolo_model_pt}，使用此路径")
        # 更新配置文件中的路径
        cfgs.YOLO_MODEL_PATH = yolo_model_pt
        cfgs.YOLO_MODEL_PATH_PT = yolo_model_pt

    # 确认ReID模型文件存在
    reid_model = os.path.join(project_root, 'GUI/models/reid_person_0.737.onnx')
    if os.path.exists(reid_model):
        print(f"找到ReID模型文件: {reid_model}")
        cfgs.EXTRACTOR_PERSON = reid_model
    else:
        print(f"ReID模型文件 {reid_model} 不存在，使用默认设置")
    
    # 清空数据库
    if args.clear_db:
        clear_all_features(cfgs.DB_PATH, cfgs.DB_NAME)
        print("数据库已清空")
    
    # 初始化日志系统
    log_system = LogSystem()
    
    # 初始化跟踪器
    tracker = ReIDTracker(log_system=log_system)
    
    # 运行视频处理
    print(f"处理视频: {args.video_path}")
    tracker.run(
        video_path=args.video_path,
        tempDataPath=args.temp_data_path,
        skip_frames=args.skip_frames,
        match_thresh=args.match_thresh,
        is_track=True,
        save_video=args.save_video
    )


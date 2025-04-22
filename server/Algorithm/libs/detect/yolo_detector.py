import sys
import os
import numpy as np
from collections import defaultdict
import torch
import Algorithm.libs.config.model_cfgs as cfgs

os.environ['YOLO_VERBOSE'] = str(cfgs.YOLO_LOG)

from ultralytics import YOLO

from Algorithm.libs.logger.log import get_logger

log_info = get_logger(__name__)
ISLOG = cfgs.ISLOG
yolo_idx_names = cfgs.YOLO_LABELS
yolo_pt_path = cfgs.YOLO_MODEL_PATH_PT
yolo_onnx_path = cfgs.YOLO_MODEL_PATH
print(f"yolo:{yolo_pt_path}")
print(f"yolo_onnx:{yolo_onnx_path}")


class YoloDetect(object):
    def __init__(self, model_path=yolo_pt_path):
        # 禁止打印输出

        self.cuda_available = torch.cuda.is_available()
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        if self.cuda_available:
            print(f"CUDA available: {torch.cuda.is_available()}")
            self._model = YOLO(yolo_pt_path).to(self.device)
            self._model_track = YOLO(yolo_pt_path).to(self.device)
            if ISLOG:
                log_info.info('{} model load succeed!!!'.format(yolo_pt_path))
           # torch.autocast(device_type="cuda", dtype=torch.bfloat16).__enter__()
        else:

            self._model = YOLO(yolo_onnx_path, task="detect").to(self.device)
            self._model_track = YOLO(yolo_onnx_path).to(self.device)
            if ISLOG:
                log_info.info('{} model load succeed!!!'.format(yolo_onnx_path))
           # torch.autocast(device_type="cpu", dtype=torch.bfloat16).__enter__()

    def create_new_instance(self):
        """创建完全独立的检测器实例"""
        new_detector = YoloDetect(self.model_path)
        return new_detector
    
    def detect(self, img, class_idx_list=cfgs.YOLO_DEFAULT_LABEL, min_size=cfgs.YOLO_MIN_SIZE):
        boxes, clss, confs = [], [], []  # 添加confs列表存储置信度
        if self.cuda_available:
            results = self._model.predict(img, conf=0.2, iou=0.4, classes=class_idx_list, verbose=False)
        else:
            results = self._model.predict(img, conf=0.2, iou=0.4, classes=class_idx_list, verbose=False)
        if results[0].boxes.xyxy is not None:
            _boxes = results[0].boxes.xyxy.cpu().tolist()
            _clss = results[0].boxes.cls.int().cpu().tolist()
            _confs = results[0].boxes.conf.cpu().tolist()  # 获取置信度
            for _box, _cls, _conf in zip(_boxes, _clss, _confs):
                if _box[3] - _box[1] > min_size and _box[2] - _box[0] > min_size:
                    boxes.append(_box)
                    clss.append(_cls)
                    confs.append(_conf)  # 添加置信度
        return boxes, clss, confs  # 返回置信度

    def track(self, frame, class_idx_list=cfgs.YOLO_DEFAULT_LABEL, persist=False, min_size=cfgs.YOLO_MIN_SIZE,
              tracker=cfgs.YOLO_TRACKER_TYPE):
        boxes, track_ids, clss, confs = [], [], [], []  # 添加confs列表
        results = self._model_track.track(frame, persist=persist, tracker=tracker, conf=0.2, iou=0.4,
                                          classes=class_idx_list)
        if results[0].boxes.id is not None:
            _boxes = results[0].boxes.xyxy.cpu().tolist()
            _track_ids = results[0].boxes.id.int().cpu().tolist()
            _clss = results[0].boxes.cls.int().cpu().tolist()
            _confs = results[0].boxes.conf.cpu().tolist()
            for _box, _track_id, _cls, _conf in zip(_boxes, _track_ids, _clss, _confs):
                if _box[3] - _box[1] > min_size and _box[2] - _box[0] > min_size:
                    boxes.append(_box)
                    track_ids.append(_track_id)
                    clss.append(_cls)
                    confs.append(_conf)  # 添加置信度
        return boxes, track_ids, clss, confs  # 返回置信度

    def reset_track(self):
        self._model_track = YOLO(cfgs.YOLO_MODEL_PATH)
# coding: utf-8
# @Author    : LittleAnt
# @Time      :
# @Descrip   : Please contact [wechat:cv_littleant] on WeChat for any questions.

import cv2
import sys
import os
import pdb
from collections import defaultdict
import numpy as np
from Algorithm.libs.extract.reid_extract import ReIdExtract
from Algorithm.libs.detect.yolo_detector import YoloDetect
from Algorithm.libs.search.search_engine import SearchEngine
import Algorithm.libs.config.model_cfgs as cfgs
from Algorithm.libs.logger.log import get_logger
from GUI.libs.reid_sqlV2 import delete_feature
import torch
log_info = get_logger(__name__)
ISLOG_common=cfgs.ISLOG_common
ISLOG=cfgs.ISLOG
colo_idx_names = cfgs.YOLO_LABELS

def Singleton(cls):
    _instance = {}
    def wrapper(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]
    return wrapper

    
@Singleton 
class ReidPipeline(object):
    """
    Pipeline to process reid.
    """

    def __init__(self, base_feat_lists, base_idx_lists, dims=1024, target_class="person", device_info="cpu"):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        self._target_class = target_class
        self._device_info = self.device
        self._detector = YoloDetect(cfgs.YOLO_MODEL_PATH)
        self.base_feat_lists = base_feat_lists
        self.base_idx_lists = base_idx_lists
        self.dims = dims
        self._search_engine = SearchEngine(base_feat_lists, base_idx_lists, dims=dims)
        self.track_method = cfgs.YOLO_TRACKER_TYPE
        if self._target_class == "person":
            self._input_size = [256, 128]
            self._target_class_idx_list = [0]
            extractor_path = cfgs.EXTRACTOR_PERSON
        else:
            raise NotImplementedError("This function only support person reid")

        if "cpu" in self._device_info.lower():
            self._extractor = ReIdExtract(self._target_class, extractor_path, self._input_size,
                                          providers=['CPUExecutionProvider'])
        elif "cuda" in self._device_info.lower():
            self._extractor = ReIdExtract(self._target_class, extractor_path, self._input_size,
                                          providers=['CUDAExecutionProvider'])

    def reload_reid_model(self, in_extractor_path=None, target_class=None, device=None):
        if target_class != None or device != None:
            if target_class != None:
                self._target_class = target_class
            else:
                self._device_info = device
            if ISLOG:
                log_info.info("!!!reload reid model, convert the model to {} and based on {}".format(target_class, device))
            if self._target_class == "person":
                self._input_size = [256,128]
                self._target_class_idx_list = [0]
                extractor_path = cfgs.EXTRACTOR_PERSON
            else:
                raise NotImplementedError("This function only support person reid")
            if in_extractor_path is not None:
                extractor_path = in_extractor_path
            if "cpu" in self._device_info.lower():
                self._extractor = ReIdExtract(self._target_class, extractor_path, self._input_size, providers=['CPUExecutionProvider'])
            elif "gpu" in self._device_info.lower():
                self._extractor = ReIdExtract(self._target_class, extractor_path, self._input_size, providers=['CUDAExecutionProvider'])

    def reload_search_engine(self, base_feat_lists, base_idx_lists, dims=1024):
        if ISLOG_common:
            log_info.info("!!!reload faiss search engine")
        self._search_engine = SearchEngine(base_feat_lists, base_idx_lists, dims=dims)


    def detect(self, img, class_idx_list, format='image', is_track=False):
        if format == 'image':
            boxes, clss, confs = self._detector.detect(img, class_idx_list=class_idx_list)
            track_ids = None
        elif format == 'video':
            if is_track:
                boxes, track_ids, clss, confs = self._detector.track(img, class_idx_list, persist=True, tracker=self.track_method)
            else:
                boxes, clss, confs = self._detector.detect(img, class_idx_list=class_idx_list)
                track_ids = None
        return boxes, track_ids, clss, confs


    def detect_npu(self, img, class_idx_list, format='image', is_track=False):
        if format == 'image':
            boxes, clss = self._detector.detect(img, class_idx_list=class_idx_list)
            track_ids = None
        elif format == 'video':
            if is_track:
                boxes, track_ids, clss = self._detector.track(img, class_idx_list, persist=True, tracker=self.track_method)
            else:
                boxes, clss = self._detector.detect(img, class_idx_list=class_idx_list)
                track_ids = None
        return boxes, track_ids, clss
    def extract(self, img):
        _each_img_norm_feat = self._extractor(img)
        return _each_img_norm_feat
    
    def search(self, img, bboxs, thresh=0.2):
        search_labels_list, search_dist_list = [], []
        before_sort_list = []
        filter_box_list = []
        for bbox in bboxs:
            _each_crop_img = img[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2]),:]
            _each_img_norm_feat = self._extractor(_each_crop_img)
            search_labels, search_dist = self._search_engine.search(_each_img_norm_feat, 1)
            if search_dist[0] <= thresh:
                search_labels_list.append(search_labels[0])
                search_dist_list.append(search_dist[0])
                filter_box_list.append(bbox)
                before_sort_list.append(search_labels[0])
            else:
                before_sort_list.append("unknown")
        return search_labels_list, search_dist_list, filter_box_list, before_sort_list

    def reset_track(self):
        self._detector.reset_track()

    def VecPair(self, Vec, thresh=0.2,similar_thresh=0.1):
        search_label, search_dist = self._search_engine.search(Vec, 1)
        if search_dist == [] or search_dist[0] >= thresh:
            return -1, 1.0
        else:
            return search_label[0], search_dist[0]

    def SingleExtract(self, img, bbox):
        _each_crop_img = img[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2]),:]
        _each_img_norm_feat = self._extractor(_each_crop_img)
        return _each_img_norm_feat
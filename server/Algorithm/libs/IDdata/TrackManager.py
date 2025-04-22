from dataclasses import dataclass
import numpy as np
import time
from typing import Dict, Optional, List
import threading

@dataclass
class TrackInfo:
    track_id: int               # 跟踪ID
    person_id: int = -1        # 人员ID
    quality: float = 0.0       # 图像质量
    last_seen: float = 0.0     # 最后出现时间
    feature: Optional[np.ndarray] = None  # 特征向量
    is_reid: bool = False      # 是否已重识别
    location: str = "unknown"  # 位置状态
    last_reid: float = 0.0     # 最后重识别时间

class TrackManager:
    def __init__(self, max_age: int = 30 , reid_interval: float = 1):
        self.tracks: Dict[int, TrackInfo] = {}
        self.max_age = max_age
        self.lock = threading.Lock()
        self.reid_interval = reid_interval

        # 启动清理线程
        self.cleaner = threading.Thread(target=self._auto_clean, daemon=True)
        self.reid_checker = threading.Thread(target=self._auto_check_reid, daemon=True)
        self.reid_checker.start()
        # self.cleaner.start()



        
    def update_tracks(self, current_track_ids: List[int]):
        """更新跟踪状态"""
        with self.lock:
            # 清理消失的tracks
            current_time = time.time()
            disappeared = set(self.tracks.keys()) - set(current_track_ids)
            for track_id in disappeared:
                del self.tracks[track_id]
                
            # 初始化新tracks
            new_tracks = set(current_track_ids) - set(self.tracks.keys())
            for track_id in new_tracks:
                self.tracks[track_id] = TrackInfo(
                    track_id=track_id,
                    last_seen=current_time
                )


    def update_track_info(self, 
                         track_id: int,
                         person_id: Optional[int] = None,
                         quality: Optional[float] = None,
                         feature: Optional[np.ndarray] = None,
                         location: Optional[str] = None ,
                         is_reid: Optional[bool] = None):
        """更新track信息"""
        with self.lock:
            if track_id not in self.tracks:
                return
                
            track = self.tracks[track_id]
            track.last_seen = time.time()
            
            if person_id is not None:
                track.person_id = person_id
                track.is_reid = True
                track.last_reid = time.time() 
            if quality is not None:
                track.quality = quality
            if feature is not None:
                track.feature = feature
            if location is not None:
                track.location = location
            if is_reid is not None:
                track.is_reid = is_reid

    def _auto_clean(self):
        """自动清理过期tracks"""
        while True:
            time.sleep(1)
            current_time = time.time()
            with self.lock:
                expired = [
                    track_id for track_id, info in self.tracks.items()
                    if current_time - info.last_seen > self.max_age
                ]
                for track_id in expired:
                    del self.tracks[track_id]
    
    def _auto_check_reid(self):
        """自动检查是否需要重新识别"""
        while True:
            time.sleep(300)  # 每3秒检查一次
            with self.lock:
                current_time = time.time()
                for track_id, track in self.tracks.items():
                    if track.is_reid and current_time - track.last_reid > self.reid_interval:
                        track.is_reid = False
                        # print(f"Track {track_id} 需要重新识别")


    def get_track_info(self, track_id: int) -> Optional[TrackInfo]:
        """获取track信息"""
        return self.tracks.get(track_id)
        
    def get_all_tracks(self) -> Dict[int, TrackInfo]:
        """获取所有tracks"""
        return self.tracks.copy()
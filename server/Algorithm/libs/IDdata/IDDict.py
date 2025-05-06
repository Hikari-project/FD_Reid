# -*- coding: UTF-8 -*-
'''
@Project :AIProject
@Author  :self-798
@Contack :123090233@link.cuhk.edu.cn
@Version :V1.0
@Date    :2025/3/11 1:31
@Describe:
IDDict.py - 行人ID管理模块
功能描述:
- 用于管理行人检测和重识别系统中的ID映射关系
- 提供ID分配、存储和检索的功能
- 维护检测到的行人ID与特征信息的对应关系
'''
import sys
sys.path.append('E:/git')
sys.path.append('E:/git/MultiHeadPassengerFlow')
import time
import threading
from collections import defaultdict
import time
import threading
from collections import defaultdict

class IDDict:
    """行人ID管理系统主类"""
    
    def __init__(self, max_age=5, area_boundary=None,log_system = None,b1 = None):
        """
        初始化ID管理器
        :param max_age: 数据有效期(秒)
        :param area_boundary: 区域判定函数，需返回 'inside'/'outside'/'pass_area'
        """
        self.data = {}  # {person_id: entry}
        self.cam_index = defaultdict(set)  # {cam_id: set(person_ids)}
        self.lock = threading.RLock()
        self.max_age = max_age
        if area_boundary is None:
            raise ValueError("未提供区域判定函数")
        self.area_check = area_boundary
        # 启动清理线程
        self.cleaner = threading.Thread(target=self._auto_clean, daemon=True)
        self.cleaner.start()
        self.log_system = log_system

    def add_update(self, person_id, cam_id, x, y, reid_id=None):
        """
        添加或更新行人位置信息，并判断状态变化事件
        :return: 状态变化事件，如 'enter', 'exit', 'pass'，或 None
        """
        with self.lock:
            current_time = time.time()
            new_location = self.area_check(x, y)  # 可能返回 'inside', 'outside', 'pass_area'
            entry = self.data.get(person_id)
            event = None
            if entry:
                old_state = entry.get('current_location')
                # 计算速度向量：基于上一帧的位置信息和最近一次更新时间last_seen
                dt = current_time - entry['last_seen']
                if dt > 0:
                    prev_x = entry['position']['x']
                    prev_y = entry['position']['y']
                    vx = (x - prev_x) 
                    vy = (y - prev_y) 
                    entry['velocity'] = {'vx': vx, 'vy': vy}
                else:
                    entry['velocity'] = {'vx': 0, 'vy': 0}
                
                # 状态变化及过店逻辑判断(保留原逻辑)
                if old_state != new_location:
                    event = self._handle_state_change(entry, old_state, new_location)
                    if new_location == 'pass_area' and old_state != 'pass_area':
                        entry['entry_time'] = current_time
                # 更新条目信息
                entry.update({
                    'current_location': new_location,
                    'last_seen': current_time,
                    'position': {'cam_id': cam_id, 'x': x, 'y': y}
                })
            else:
                # 新建条目，初始化时不计算速度
                self.data[person_id] = {
                    'person_id': person_id,
                    "reid_id": reid_id,
                    'current_location': new_location,
                    'position': {'cam_id': cam_id, 'x': x, 'y': y},
                    'last_seen': current_time,
                    'entry_time': current_time,
                    'is_counted': False,
                    'pass_counted': False,  # 过店计数标记
                    'in_pass': False,       # 过店状态标记
                    'velocity': {'vx': 0, 'vy': 0}  # 初始速度为0
                }
                self.cam_index[cam_id].add(person_id)
                # 当第一帧就在 pass_area，不做立即标记，等待后续2s判断
                return None
            return event
            
    def _log_event(self, event):
        """记录事件日志"""
        if self.log_system:
            self.log_system.log_business_event({
                "event_type": event['type'],
                "person_id": event['person_id'],
                "reid_id"  : event["reid_id"], 
                "camera_id": self.data[event['person_id']]['position']['cam_id'],
                "old_state": event['old_state'],
                "new_state": event['new_state'],
                
            })

    def _handle_state_change(self, entry, old_state, new_state):
        """
        处理状态变化事件:
        - 进出店: 不再限制只记录第一次 # 使用is_counted标记
        - 过店: 需要完整经过pass_area区域,使用pass_counted标记
        """
        # 添加过店中间状态判断
        if new_state == 'pass_area' and old_state == 'outside':
            entry['in_pass'] = True
            return None
        
        if new_state == 'pass_area':
            entry['in_pass'] = True
        event_map = {
            ('outside', 'inside'): ('enter', 'store'),
            ('inside', 'outside'): ('exit', 'store'),
            ('pass_area', 'outside'): ('pass', 'pass') if entry.get('in_pass') else None,
            ('pass_area', 'inside'): ('enter', 'store'),
            ('inside', 'pass_area'): ('exit', 'store')
        }
        
        event_info = event_map.get((old_state, new_state))
        if not event_info:
            return None
            
        event_type, count_type = event_info
        
        # 修改计数逻辑，移除只记录一次的限制
        should_count = True
        # 过店逻辑仍然保留，因为过店需要完整经过passarea
        if count_type =='pass' and not entry.get('pass_counted'):
            entry['pass_counted'] = True
            entry['in_pass'] = False  # 重置过店标记      
        if should_count:
            return {
                'type': event_type,
                'person_id': entry['person_id'],
                "reid_id"  : entry["reid_id"] ,
                'old_state': old_state,
                'new_state': new_state,
                'timestamp': time.time()
            }
        return None
    def _auto_clean(self):
        """后台清理过期数据，并处理未完成的过店事件"""
        while True:
            time.sleep(self.max_age // 2)
            cutoff = time.time() - self.max_age
            with self.lock:
                expired = []
                for pid, entry in self.data.items():
                    if entry['last_seen'] < cutoff:
                        # 检查是否有未完成的过店事件
                        if entry.get('in_pass') and not entry.get('pass_counted') and entry["reid_id"] != -1 and entry.get('is_counted'):
                            # 触发过店事件
                            event = {
                                'type': 'pass',
                                'person_id': pid,
                                "reid_id"  : entry["reid_id"],
                                'old_state': 'pass_area',
                                'new_state': 'outside',
                                'timestamp': time.time()
                            }
                            print(f"人员{event['person_id']} 过店")
                            # 更新状态
                            if self.log_system != None:
                                self._log_event(event) 
                            else:
                                print("log_system is None")
                            entry['pass_counted'] = True
                            entry['in_pass'] = False
                        expired.append(pid)
                        
                # 清理过期数据
                for pid in expired:
                    cam_id = self.data[pid]['position']['cam_id']
                    self.cam_index[cam_id].discard(pid)
                    del self.data[pid]
    @staticmethod

    # 查询接口
    def get_by_cam(self, cam_id):
        """
        获取指定摄像头下的所有行人信息
        :param cam_id: 摄像头ID
        :return: Dict[person_id, person_info]
        """
        with self.lock:
            result = {}
            for person_id in self.cam_index[cam_id]:
                entry = self.data.get(person_id)
                if entry:
                    result[person_id] = {
                        'position': entry['position'],
                        'status': entry['current_location'],
                        'last_seen': entry['last_seen']
                    }
            return result

    def get_status(self, person_id):
        """
        获取指定行人的状态信息
        :param person_id: 行人ID
        :return: Dict 或 None
        """
        with self.lock:
            entry = self.data.get(person_id)
            if entry:
                return {
                    'current_location': entry['current_location'],
                    'last_seen': entry['last_seen'],
                    'is_counted': entry['is_counted'],
                    'pass_counted': entry.get('pass_counted', False)
                }
            return None
    
    def get_all_in_area(self, area_type='inside'):
        """获取指定区域内的所有ID"""
        with self.lock:
            return {pid: entry for pid, entry in self.data.items() 
                   if entry['current_location'] == area_type}
    
    def get_data(self):
        """获取所有数据"""
        with self.lock:
            return self.data.copy()
        
if __name__  == "__main__":
    # 初始化
    id_dict = IDDict(max_age=30, area_boundary=lambda x,y: x>100)

    # 添加/更新数据示例
    id_dict.add_update(
        person_id=1,         # 人员唯一标识（int或str类型）
        cam_id="cam1",       # 摄像头标识（字符串）
        x=150, y=200         # 坐标位置（数值）
    )

    # 数据结构示例
    '''
    self.data = {
        1: {
            'position': {
                'cam_id': "cam1",  # 最后出现的摄像头
                'x': 150,          # 最后出现的x坐标
                'y': 200           # 最后出现的y坐标
            },
            'status': "inside",    # 区域状态（根据坐标判断）
            'last_seen': 1620034500.123456  # 最后更新时间戳
        },
        2: {
            'position': {"cam_id": "cam2", "x": 50, "y": 70},
            'status': "outside",
            'last_seen': 1620034490.456789
        }
    }

    self.cam_index = {
        "cam1": {1},
        "cam2": {2}
    }
    '''
    # 查询方法返回示例
    id_dict.get_by_cam("cam1") 
    # 返回：{1: {'position':..., 'status': 'inside', 'last_seen':...}}

    id_dict.get_status(1)  # 返回："inside"
    # id_dict.total_count()  # 返回：2
    # id_dict.get_all_inside()  # 返回所有status为inside的条目

    # 跨摄像头移动示例
    id_dict.add_update(1, "cam3", 180, 220)
    # cam_index会变为：
    # {
    #     "cam1": set(),
    #     "cam2": {2},
    #     "cam3": {1}
    # }
    print(id_dict.get_by_cam("cam3"))  # 返回空字典
    print(id_dict.get_by_cam("cam1"))  # 返回{1: ...}


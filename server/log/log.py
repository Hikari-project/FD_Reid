from collections import defaultdict
import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from logging import Logger, handlers, Formatter, getLogger
from threading import Lock
sys.path.append('../')
class GlobalCounter:
    def __init__(self):
        self._counts = {
            'enter': 0,
            'exit': 0, 
            'pass': 0,
            're_enter': 0
        }
        self._lock = threading.Lock()
    
    def increment(self, count_type):
        with self._lock:
            self._counts[count_type] += 1
            
    def get_count(self, count_type):
        with self._lock:
            return self._counts[count_type]
            
    def get_all_counts(self):
        with self._lock:
            return self._counts.copy()
            
    def reset(self):
        with self._lock:
            for key in self._counts:
                self._counts[key] = 0
class LogSystem:
    """
    日志系统：提供业务日志和系统日志的记录功能
    支持日志缓存、批量写入和自动转储等功能
    """
    def __init__(self):
        """初始化日志系统"""
        self.log_buffer = []
        self.buffer_lock = threading.Lock()
        self.last_push_time = time.time()
        self.counter = GlobalCounter()
        # 初始化目录结构
        self.log_dir = "logs"
        self._init_directories()
        
        # 初始化后台转存线程
        self.check_interval = 60  # 每60秒检查一次
        self.timer_thread = threading.Thread(target=self._check_buffer_loop, daemon=True)
        self.timer_thread.start()

        # 初始化日志处理器
        self.business_logger = self._create_logger("business")
        self.system_logger = self._create_logger("system")
    
    def get_counts(self):
        return self.counter.get_all_counts()
    
    def _init_directories(self):
        """创建必要的日志目录结构"""
        os.makedirs(os.path.join(self.log_dir, "business/permanent"), exist_ok=True)
        os.makedirs(os.path.join(self.log_dir, "system/permanent"), exist_ok=True)
        os.makedirs(os.path.join(self.log_dir, "temp"), exist_ok=True)

    def _check_buffer_loop(self):
        """后台转存线程主循环"""
        while True:
            time.sleep(self.check_interval)
            self._check_buffer_age()

    def _check_buffer_age(self):
        """检查并转存超过30分钟的日志"""
        now = datetime.now()
        threshold = now - timedelta(minutes=30)
        
        # 分离过期日志
        expired_logs = []
        with self.buffer_lock:
            remaining_logs = []
            for log in self.log_buffer:
                if log["timestamp"] < threshold:
                    expired_logs.append(log)
                else:
                    remaining_logs.append(log)
            self.log_buffer = remaining_logs
        
        # 处理过期日志
        for log in expired_logs:
            self._write_to_permanent(log)

    def _create_logger(self, logger_name):
        """
        创建并配置日志记录器
        :param logger_name: 日志记录器名称
        :return: 配置好的Logger对象
        """
        logger = getLogger(logger_name)
        logger.setLevel(20)  # INFO级别
        
        # 创建日志文件处理器
        today = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(self.log_dir, f"{logger_name}/{logger_name}_{today}.log")
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # 创建日志处理器
        handler = handlers.TimedRotatingFileHandler(
            log_file, 
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        
        # 设置日志格式
        formatter = Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # 如果logger已有处理器，先清除
        if logger.handlers:
            for h in logger.handlers:
                logger.removeHandler(h)
                
        # 添加处理器
        logger.addHandler(handler)
        return logger

    def log_business_event(self, event_data):
        """
        记录业务事件日志
        :param event_data: 事件数据字典，包含以下字段：
            - event_type: 'enter', 'exit', 'pass', 'add_id', 'remove_id'
            - person_id: 人员ID
            - reid_id (可选): 行人识别ID
            - camera_id: 摄像头ID  
            - old_state/new_state: 状态变更
            - 其他可选字段
        """
        log_entry = {
            "timestamp": datetime.now(),
            "type": "business",
            "data": self._generate_business_data(event_data)
        }
        if event_data["event_type"] in ['enter', 'exit', 'pass','re_enter']:
            # 仅对特定事件类型进行计数
            self.counter.increment(event_data["event_type"])
        with self.buffer_lock:
            self.log_buffer.append(log_entry)
        self.business_logger.info(f"BUSINESS {json.dumps(log_entry['data'])}")
        self._auto_push()

    def get_counts(self):
        return self.counter.get_all_counts()
    
    def log_system_event(self, error_type, details):
        """
        记录系统事件日志
        :param error_type: 错误类型，如'rtsp_error', 'hardware_recovery'等
        :param details: 详细信息字典
        """
        log_entry = {
            "timestamp": datetime.now(),
            "type": "system",
            "data": self._generate_system_data(error_type, details)
        }
        with self.buffer_lock:
            self.log_buffer.append(log_entry)
        self.system_logger.info(f"SYSTEM {json.dumps(log_entry['data'])}")
        self._auto_push()

    def _generate_business_data(self, event_data):
        """
        生成业务日志数据结构
        :param event_data: 原始事件数据
        :return: 格式化的业务日志数据
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_data['event_type'],
            "person_id": event_data['person_id'],
            "reid_id"  : event_data["reid_id"] ,
            "camera_id": event_data['camera_id'],
            "expiration_time": event_data.get('expiration_time', 
                              (datetime.now() + timedelta(minutes=30)).isoformat()),
            "count_status": event_data.get('count_status', 'new'),
            "trigger_reason": event_data.get('trigger_reason', '')
        }

    def _generate_system_data(self, error_type, details):
        """
        生成系统日志数据结构
        :param error_type: 错误类型
        :param details: 详细信息
        :return: 格式化的系统日志数据
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "details": details
        }
        
    def _auto_push(self):
        """
        根据缓冲区大小和时间间隔自动推送日志
        """
        should_push = False
        with self.buffer_lock:
            if len(self.log_buffer) >= 10:  # 缓冲区达到10条日志
                should_push = True
            elif time.time() - self.last_push_time > 300:  # 5分钟未推送
                should_push = True
                
        if should_push:
            self._push_buffer()
            
    def _push_buffer(self):
        """
        将缓冲日志写入临时文件
        """
        with self.buffer_lock:
            if not self.log_buffer:
                return
                
            # 生成临时文件名
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            temp_file = os.path.join(self.log_dir, f"temp/log_buffer_{timestamp}.json")
            
            # 写入临时文件
            try:
                with open(temp_file, "w", encoding="utf-8") as f:
                    for log in self.log_buffer:
                        log_data = {
                            "timestamp": log["timestamp"].isoformat(),
                            "type": log["type"],
                            "data": log["data"]
                        }
                        f.write(json.dumps(log_data) + "\n")
                        
                # 更新状态
                self.last_push_time = time.time()
                self.log_buffer.clear()
                
                # 异步处理临时文件
                threading.Thread(
                    target=self._process_temp_file,
                    args=(temp_file,),
                    daemon=True
                ).start()
                    
            except Exception as e:
                error_log = {
                    "error_type": "LOG_SAVE_ERROR",
                    "timestamp": datetime.now().isoformat(),
                    "details": str(e)
                }
                with self.buffer_lock:
                    self.log_buffer.append({
                        "timestamp": datetime.now(),
                        "type": "system",
                        "data": error_log
                    })
    
    def _process_temp_file(self, temp_file):
        """
        处理临时日志文件，转存至永久存储
        :param temp_file: 临时文件路径
        """
        try:
            with open(temp_file, "r", encoding="utf-8") as f:
                for line in f:
                    log = json.loads(line)
                    self._write_to_permanent(log)
                    
            # 处理完成后删除临时文件
            os.remove(temp_file)
        except Exception as e:
            self.system_logger.error(f"处理临时文件失败: {str(e)}")
    
    def _write_to_permanent(self, log):
        """
        将日志写入永久存储
        :param log: 日志条目
        """
        log_type = log["type"]
        date_str = datetime.fromisoformat(log["timestamp"]).strftime("%Y%m%d")
        
        # 确定存储文件路径
        log_file = os.path.join(self.log_dir, f"{log_type}/permanent/{log_type}_{date_str}.log")
        
        # 写入文件
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log) + "\n")
        except Exception as e:
            error_log = {
                "error_type": "LOG_SAVE_ERROR",
                "timestamp": datetime.now().isoformat(),
                "details": str(e)
            }
            with self.buffer_lock:
                self.log_buffer.append({
                    "timestamp": datetime.now(),
                    "type": "system",
                    "data": error_log
                })

    def calculate_counts_from_logs(self, start_time):
        """基于 reid_id 进行去重。若 reid_id 缺失或为 -1，一样计入，但不做冷却判断。"""
        counts = defaultdict(int)
        last_count_time = {}
        for event_type in ['enter', 'exit', 'pass']:
            counts[event_type] = 0
        log_filename = f"business_{start_time.strftime('%Y%m%d')}.log"
        log_path = os.path.join(self.log_dir, "business", "permanent")
        log_file = os.path.join(log_path, log_filename)

        if not os.path.exists(log_file):
            return dict(counts)

        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # print(line)
                try:
                    log_data = json.loads(line.strip())
                    event_data = log_data.get('data', {})
                    if not event_data:
                        continue

                    reid_id = event_data.get('reid_id', -1)
                    log_time = datetime.fromisoformat(
                        event_data['timestamp'].replace('T', ' ').split('.')[0]
                    )
                    # if log_time < start_time:
                    #     continue

                    event_type = event_data.get('event_type')
                    if event_type in ['enter', 'exit', 'pass']:
                        # 若 reid_id合法，则记录最后一次计数时间；否则直接计数
                        if reid_id != -1:
                            if (reid_id not in last_count_time 
                                    or (log_time - last_count_time[reid_id]) >= timedelta(minutes=30)):
                                counts[event_type] += 1
                                last_count_time[reid_id] = log_time
                        else:
                            # 对于 reid_id == -1 或缺失，直接计数
                            counts[event_type] += 1
                except:
                    continue

        return dict(counts)
if __name__ == "__main__":
    # 初始化日志系统
    log_system = LogSystem()
    
    # 记录业务事件示例
    log_system.log_business_event({
        "event_type": "enter",
        "person_id": "reid_123",
        "reid_id": 123,
        "camera_id": "cam_01",
        "old_state": "outside",
        "new_state": "inside",
        "count_status": "new"
    })
    
    # 记录系统事件示例
    log_system.log_system_event("rtsp_error", {
        "camera_id": "cam_02",
        "error_code": "connection_failed",
        "retry_count": 3
    })
    print(log_system.get_counts())
    print("日志已记录。检查logs目录查看结果。")
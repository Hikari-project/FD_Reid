# -*- coding: UTF-8 -*-
'''
@Project :FD_REID_Project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2024/12/19 2:34 
@Describe: 改进版本，添加连接池管理
'''

import numpy as np
import sqlite3
from Algorithm.libs.logger.log import get_logger
import Algorithm.libs.config.model_cfgs as cfgs
import time
import threading
from contextlib import contextmanager

log_info = get_logger(__name__)
ISLOG = cfgs.ISLOG


# 定义连接池类
class ConnectionPool:
    _instance = None
    _instance_lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        """单例模式获取连接池实例"""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = ConnectionPool()
        return cls._instance

    def __init__(self):
        """初始化连接池"""
        self.pool = {}  # 格式: {db_path: {conn: connection, lock: lock, last_used: timestamp}}
        self.pool_lock = threading.Lock()
        self.max_connections = 5  # 每个数据库文件的最大连接数
        self.connection_timeout = 60  # 连接空闲超时时间（秒）

    # 改进连接池释放连接的逻辑
    def release_connection(self, db_path, conn):
        """释放连接回连接池"""
        with self.pool_lock:
            if db_path not in self.pool:
                # 如果连接池中没有这个数据库的条目，直接关闭连接
                conn.close()
                return

            pool_entry = self.pool[db_path]
            if conn in pool_entry["in_use"]:
                # 检查连接是否仍然有效
                try:
                    # 执行一个简单的查询来测试连接
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()

                    # 连接有效，添加回池中
                    pool_entry["in_use"].remove(conn)
                    pool_entry["connections"].append(conn)
                    if ISLOG:
                        log_info.info(
                            f"释放连接到连接池: {db_path}, 可用连接: {len(pool_entry['connections'])}, 使用中连接: {len(pool_entry['in_use'])}")
                except sqlite3.Error:
                    # 连接已无效，从使用中移除但不添加回池
                    pool_entry["in_use"].remove(conn)
                    try:
                        conn.close()
                    except:
                        pass
                    if ISLOG:
                        log_info.warning(f"移除无效连接: {db_path}")

    # 改进连接获取逻辑，确保返回有效连接
    def get_connection(self, db_path):
        """获取数据库连接"""
        with self.pool_lock:
            # 初始化数据库连接池条目
            if db_path not in self.pool:
                self.pool[db_path] = {
                    "connections": [],
                    "in_use": set(),
                    "db_lock": threading.Lock()
                }

            pool_entry = self.pool[db_path]

            # 尝试获取现有连接并验证其有效性
            while pool_entry["connections"]:
                conn = pool_entry["connections"].pop()
                try:
                    # 验证连接是否有效
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()

                    # 连接有效，可以使用
                    pool_entry["in_use"].add(conn)
                    return conn
                except sqlite3.Error:
                    # 连接已失效，忽略并尝试下一个
                    try:
                        conn.close()
                    except:
                        pass
                    if ISLOG:
                        log_info.warning(f"移除池中无效连接: {db_path}")

            # 如果没有可用连接且未达到最大连接数，创建新连接
            if len(pool_entry["in_use"]) < self.max_connections:
                try:
                    conn = sqlite3.connect(db_path, timeout=10, check_same_thread=False)
                    pool_entry["in_use"].add(conn)
                    if ISLOG:
                        log_info.info(f"创建新数据库连接: {db_path}, 当前连接数: {len(pool_entry['in_use'])}")
                    return conn
                except sqlite3.Error as e:
                    if ISLOG:
                        log_info.error(f"创建数据库连接错误: {e}")
                    raise

            # 如果已达到最大连接数，等待并重试
            if ISLOG:
                log_info.warning(f"已达到最大连接数 {self.max_connections}，等待可用连接...")

            # 释放连接池锁，等待一个连接被释放
            self.pool_lock.release()
            time.sleep(0.1)
            self.pool_lock.acquire()

            # 再次尝试获取连接
            return self.get_connection(db_path)

    def close_all_connections(self):
        """关闭所有连接"""
        with self.pool_lock:
            for db_path, pool_entry in self.pool.items():
                # 关闭所有未使用的连接
                for conn in pool_entry["connections"]:
                    try:
                        conn.close()
                    except:
                        pass

                # 关闭所有使用中的连接
                for conn in pool_entry["in_use"]:
                    try:
                        conn.close()
                    except:
                        pass

                if ISLOG:
                    log_info.info(f"关闭数据库 {db_path} 的所有连接")

            # 清空连接池
            self.pool.clear()

    def get_db_lock(self, db_path):
        """获取数据库操作锁"""
        with self.pool_lock:
            if db_path not in self.pool:
                self.pool[db_path] = {
                    "connections": [],
                    "in_use": set(),
                    "db_lock": threading.Lock()
                }
            return self.pool[db_path]["db_lock"]


# 全局连接池实例
_connection_pool = ConnectionPool.get_instance()

# 全局锁（兼容原有代码）
_db_lock = threading.Lock()


@contextmanager
def _get_connection_context(db_path):
    """连接上下文管理器，自动释放连接"""
    conn = None
    try:
        conn = _connection_pool.get_connection(db_path)
        yield conn
    finally:
        if conn:
            _connection_pool.release_connection(db_path, conn)


def _get_connection(db_path):
    """
    获取数据库连接，保持与原始API兼容
    :param db_path: 数据库文件路径
    :return: 数据库连接对象
    """
    try:
        # 从连接池获取连接
        conn = _connection_pool.get_connection(db_path)
        if ISLOG:
            log_info.info("Successfully connected to database: {}".format(db_path))
        return conn
    except sqlite3.Error as e:
        if ISLOG:
            log_info.error("Error connecting to database: {}".format(e))
        raise


# 初始化数据库
# 修改init_db函数，确保表包含所有必要的列
def init_db(db_path):
    """
    初始化数据库并创建存储特征向量的表。
    """
    with _get_connection_context(db_path) as conn:
        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{cfgs.DB_NAME}'")
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            # 如果表不存在，创建新表，包含所有必要的列
            cursor.execute(f"""
            CREATE TABLE {cfgs.DB_NAME} (
                feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL UNIQUE,
                feature_vector BLOB NOT NULL,
                last_used INTEGER DEFAULT {int(time.time())},
                is_locked INTEGER DEFAULT 0
            )
            """)
            conn.commit()
            if ISLOG:
                log_info.info(f"数据库初始化完成: {db_path}")
        else:
            # 如果表已存在，检查是否有所有必要的列
            cursor.execute(f"PRAGMA table_info({cfgs.DB_NAME})")
            columns = [column[1] for column in cursor.fetchall()]

            # 如果缺少last_used列，添加它
            if 'last_used' not in columns:
                cursor.execute(f"ALTER TABLE {cfgs.DB_NAME} ADD COLUMN last_used INTEGER DEFAULT {int(time.time())}")
                if ISLOG:
                    log_info.info(f"为表 {cfgs.DB_NAME} 添加了 last_used 列")

            # 如果缺少is_locked列，添加它
            if 'is_locked' not in columns:
                cursor.execute(f"ALTER TABLE {cfgs.DB_NAME} ADD COLUMN is_locked INTEGER DEFAULT 0")
                if ISLOG:
                    log_info.info(f"为表 {cfgs.DB_NAME} 添加了 is_locked 列")

            conn.commit()


# 存储多个特征向量
def save_features_to_sqlite(db_path, data, person_ids):
    """
    将高维特征向量以 BLOB 格式存储到 SQLite 数据库。
    :param db_path: 数据库文件路径
    :param data: NumPy 数组，形状为 (n_samples, n_features)
    :param person_ids: 对应的行人 ID 列表
    """
    with _get_connection_context(db_path) as conn:
        cursor = conn.cursor()
        current_time = int(time.time())

        for i, feature in enumerate(data):
            feature_blob = feature.tobytes()  # 将 NumPy 数组转换为二进制数据
            try:
                cursor.execute(
                    f"INSERT INTO {cfgs.DB_NAME} (person_id, feature_vector, last_used, is_locked) VALUES (?, ?, ?, ?)",
                    (person_ids[i], feature_blob, current_time, 0)
                )
            except sqlite3.IntegrityError:
                cursor.execute(
                    f"UPDATE {cfgs.DB_NAME} SET feature_vector=?, last_used=? WHERE person_id=?",
                    (feature_blob, current_time, person_ids[i])
                )
        conn.commit()


# 读取特征向量列表
def load_features_from_file(db_path):
    """
    从数据库中读取所有特征向量和对应的 person_id 列表。
    :param db_path: 数据库文件路径
    :return: (feat_list, label_list) 特征向量列表和对应的行人 ID 列表
    """
    with _get_connection_context(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT person_id, feature_vector FROM {cfgs.DB_NAME}")
        feat_list, label_list = [], []

        for row in cursor.fetchall():
            person_id = row[0]
            feature_blob = row[1]
            label_list.append(person_id)
            feat_list.append(np.frombuffer(feature_blob, dtype=np.float32))

        return feat_list, label_list


# 读取特征向量
# 修改load_features_from_sqlite函数
def load_features_from_sqlite(db_path, db_name, dims):
    """
    从数据库中读取所有特征向量及其对应的 person_id。
    :param db_path: 数据库文件路径
    :param db_name: 数据库表名
    :param dims: 特征向量维度
    :return: (features, person_ids) 特征向量列表和对应的行人 ID 列表
    """
    with _get_connection_context(db_path) as conn:
        cursor = conn.cursor()

        # 检查last_used列是否存在
        cursor.execute(f"PRAGMA table_info({db_name})")
        columns = [column[1] for column in cursor.fetchall()]

        # 如果存在last_used列，更新时间戳
        if 'last_used' in columns:
            current_time = int(time.time())
            cursor.execute(f"UPDATE {db_name} SET last_used=?", (current_time,))
            conn.commit()

        # 读取特征数据
        cursor.execute(f"SELECT person_id, feature_vector FROM {db_name}")
        feat_list, label_list = [], []

        for row in cursor.fetchall():
            label_list.append(row[0])
            feature = np.frombuffer(row[1], dtype='float32').reshape(dims)
            feat_list.append(feature)

        return feat_list, label_list


# 获取最大person_id
def get_max_person_id(db_path):
    """
    获取数据库中存储的最大行人 ID。
    :param db_path: 数据库文件路径
    :return: 最大行人 ID（整数）。如果数据库为空，返回 None。
    """
    with _get_connection_context(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT MAX(person_id) FROM {cfgs.DB_NAME}")
        result = cursor.fetchone()[0]

        if result is None:
            return 0
        return result


# 添加特征向量
def add_feature(db_path, person_id, feature):
    """
    添加单条特征向量到数据库。
    :param db_path: 数据库文件路径
    :param person_id: 行人 ID
    :param feature: NumPy 数组（特征向量）
    """
    with _get_connection_context(db_path) as conn:
        cursor = conn.cursor()

        feature_blob = feature.tobytes()  # 将 NumPy 数组转换为二进制数据
        current_time = int(time.time())  # 获取当前时间戳

        try:
            cursor.execute(
                f"INSERT INTO {cfgs.DB_NAME} (person_id, feature_vector, last_used, is_locked) VALUES (?, ?, ?, ?)",
                (person_id, feature_blob, current_time, 0)
            )
            conn.commit()
            print(f"Feature for person_id {person_id} added successfully.")
        except sqlite3.IntegrityError as e:
            print(f"Error: person_id {person_id} already exists. {e}")


# 更新特征向量
def update_feature(db_path, person_id, feature):
    """
    更新特征向量
    :param db_path: 数据库文件路径
    :param person_id: 行人 ID
    :param feature: 新的特征向量
    """
    with _get_connection_context(db_path) as conn:
        cursor = conn.cursor()

        feature_blob = feature.tobytes()
        current_time = int(time.time())

        cursor.execute(
            f"UPDATE {cfgs.DB_NAME} SET feature_vector=?, last_used=? WHERE person_id=?",
            (feature_blob, current_time, person_id)
        )
        conn.commit()


# 删除特征向量
def delete_feature(db_path, person_id):
    """
    从数据库中删除特征向量
    :param db_path: 数据库文件路径
    :param person_id: 要删除的行人 ID
    """
    with _get_connection_context(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(f"DELETE FROM {cfgs.DB_NAME} WHERE person_id=?", (person_id,))
        conn.commit()


# 清空特征库
def clear_all_features(db_path, db_name):
    """
    清空特征库
    :param db_path: 数据库文件路径
    :param db_name: 数据库表名
    """
    with _get_connection_context(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(f"DELETE FROM {db_name}")
        conn.commit()


# 关闭所有连接
def close_all_connections():
    """关闭连接池中所有数据库连接"""
    _connection_pool.close_all_connections()
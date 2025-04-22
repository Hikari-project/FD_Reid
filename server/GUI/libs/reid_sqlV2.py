# -*- coding: UTF-8 -*-
'''
@Project :FD_REID_Project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2024/12/19 2:34 
@Describe:
'''


import numpy as np
import sqlite3
from Algorithm.libs.logger.log import get_logger
import Algorithm.libs.config.model_cfgs as cfgs

log_info = get_logger(__name__)
ISLOG=cfgs.ISLOG

# 全局连接变量
conn =None

# 数据库连接函数
def _get_connection(db_path):
    """
    获取数据库连接，如果数据库文件不存在则自动创建。
    """
    global conn
    if conn is None:
        try:
            conn = sqlite3.connect(db_path,timeout=10,check_same_thread=False)
            if ISLOG:
                log_info.info("Successfully connected to database: {}".format(db_path))
            return conn
        except sqlite3.Error as e:
            if ISLOG:
                log_info.error("Error connecting to database: {}".format(e))
            raise
    return conn



# 初始化数据库
def init_db(db_path):
    """
    初始化数据库并创建存储特征向量的表。
    """

    conn = _get_connection(db_path)

    cursor = conn.cursor()

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {cfgs.DB_NAME} (
        feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL UNIQUE,
        feature_vector BLOB NOT NULL
    )
    """)
    conn.commit()


# 存储多个特征向量
def save_features_to_sqlite(db_path, data, person_ids):
    """
    将高维特征向量以 BLOB 格式存储到 SQLite 数据库。
    :param db_path: 数据库文件路径
    :param data: NumPy 数组，形状为 (n_samples, n_features)
    :param person_ids: 对应的行人 ID 列表
    """
    conn = _get_connection(db_path)

    cursor = conn.cursor()

    for i, feature in enumerate(data):
        feature_blob = feature.tobytes()  # 将 NumPy 数组转换为二进制数据
        cursor.execute(
            f"INSERT INTO {cfgs.DB_NAME} (person_id, feature_vector) VALUES (?, ?)",
            (person_ids[i], feature_blob)
        )

    conn.commit()


# 添加特征向量
# 将新的特征向量添加到数据库中。这里要求 person_id 是唯一的（用于标识行人）。
def add_feature(db_path, person_id, feature):
    """
    添加单条特征向量到数据库。
    :param db_path: 数据库文件路径
    :param person_id: 行人 ID
    :param feature_vector: NumPy 数组（特征向量）
    """
    conn = _get_connection(db_path)

    cursor = conn.cursor()
    feature_blob = feature.tobytes()  # 将 NumPy 数组转换为二进制数据

    try:
        cursor.execute(
            f"INSERT INTO {cfgs.DB_NAME} (person_id, feature_vector) VALUES (?, ?)",
            (person_id, feature_blob)
        )
        conn.commit()
        print(f"Feature for person_id {person_id} added successfully.")
    except sqlite3.IntegrityError:
        print(f"Error: person_id {person_id} already exists.")

def clear_all_features(db_path):
    """清空特征数据库"""
    conn = _get_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"DELETE FROM {cfgs.DB_NAME}")
        conn.commit()
        print("特征库已清空")
        
        # 重置自增ID
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{cfgs.DB_NAME}'")
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"清空数据库失败: {e}")
    finally:
        cursor.close()
# 更新特征向量
# 根据 person_id 更新对应的特征向量。
def update_feature(db_path, person_id, feature_vector):
    """
    更新数据库中某行人的特征向量。
    :param db_path: 数据库文件路径
    :param person_id: 行人 ID
    :param feature_vector: NumPy 数组（特征向量）
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()
    feature_blob = feature_vector.tobytes()  # 将 NumPy 数组转换为二进制数据

    cursor.execute(
        f"UPDATE {cfgs.DB_NAME} SET feature_vector = ? WHERE person_id = ?",
        (feature_blob, person_id)
    )

    if cursor.rowcount == 0:
        print(f"No feature found for person_id {person_id}. Nothing updated.")
    else:
        print(f"Feature for person_id {person_id} updated successfully.")

    conn.commit()


# 删除特征向量
# 根据 person_id 删除对应的特征向量。
def delete_feature(db_path, person_id):
    """
    删除数据库中某行人的特征向量。
    :param db_path: 数据库文件路径
    :param person_id: 行人 ID
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        f"DELETE FROM {cfgs.DB_NAME} WHERE person_id = ?",
        (person_id,)
    )

    if cursor.rowcount == 0:
        print(f"No feature found for person_id {person_id}. Nothing deleted.")
    else:
        print(f"Feature for person_id {person_id} deleted successfully.")

    conn.commit()

# 读取特征向量
# 从数据库中读取所有特征向量_TEXT格式的feature,及其对应的 person_id，并将结果转换为 NumPy 数组。
def load_sql_feat_info(db_path, db_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT person_id, feature_TEXT FROM {}".format(db_name))
        feat_list, label_list = [], []
        for row in cursor.fetchall():
            label_list.append(row[0])
            feat_list.append(list(map(float, row[1].split(','))))  # 转换特征为浮点数列表

        # print(f"共计{len(feat_list)}条注册用户")
        # for i, feat in enumerate(feat_list):
        # print(f"{i}.{label_list[i]}:已记录{len(feat)}维特征")

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return [], []
    except Exception as e:
        print(f"其他错误: {e}")
        return [], []
    finally:
        cursor.close() if cursor else None
        conn.close() if conn else None

    return feat_list, label_list


# 读取特征向量
# 从数据库中读取所有特征向量及其对应的 person_id，并将结果转换为 NumPy 数组。
def load_features_from_sqlite(db_path, db_name,dims):
    """
    从数据库中读取所有特征向量。
    :param db_path: 数据库文件路径
    :param dims: 特征向量维度
    :return: (features, person_ids) NumPy 数组和对应的行人 ID
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT person_id, feature_vector FROM {db_name}")
    feat_list, label_list = [], []
    for row in cursor.fetchall():
        label_list.append(row[0])
        feature = np.frombuffer(row[1], dtype='float32').reshape(dims)  # 从 BLOB 转换为 NumPy 数组
        feat_list.append(feature)


    return feat_list, label_list

def get_max_person_id(db_path):
    """
    获取数据库中存储的最大行人 ID。
    :param db_path: 数据库文件路径
    :return: 最大行人 ID（整数）。如果数据库为空，返回 None。
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT MAX(person_id) FROM {cfgs.DB_NAME}")  # 查询最大 person_id
    result = cursor.fetchone()[0]  # 获取查询结果（最大值）
    if result is None or result==None:
        result = 0
    return result  # 如果数据库为空，结果会是 None

def close_connection():
    global conn
    if conn:
        try:
            conn.close()
            if ISLOG:
                log_info.info("Successfully deconnected to database: ")
        except sqlite3.Error as e:
            if ISLOG:
                log_info.error("Error deconnecting to database: {}".format(e))

if __name__ == '__main__':
    # 初始化数据库
    db_path = "reid_features_blob1.db"
    init_db(db_path)


    # 批量添加数据
    dims = 1280  # 特征向量维度
    nb = 500  # 特征数量
    data = np.random.random((100, dims)).astype('float32')  # 生成随机特征向量
    person_ids = list(range(nb-100, nb ))  # 模拟行人 ID

    save_features_to_sqlite(db_path, data, person_ids)  # 存储特征向量

    # 生成随机特征向量和对应的行人 ID
    feature_1 = np.random.random(dims).astype('float32')  # 随机生成特征向量 1
    feature_2 = np.random.random(dims).astype('float32')  # 随机生成特征向量 2
    person_id_1 = 1
    person_id_2 = 2

    # 添加特征向量
    add_feature(db_path, person_id_1, feature_1)
    add_feature(db_path, person_id_2, feature_2)

    # 尝试添加重复的 person_id（会报错）
    add_feature(db_path, person_id_1, feature_2)  # person_id_1 已存在

    # 更新特征向量
    updated_feature = np.random.random(dims).astype('float32')  # 新的特征向量
    update_feature(db_path, person_id_1, updated_feature)

    # 删除特征向量
    delete_feature(db_path, person_id_2)  # 删除 person_id_2 的特征向量

    # 读取所有特征向量
    features, person_ids = load_features_from_sqlite(db_path, dims)
    print("Features shape:", features.shape)
    print("Person IDs:", person_ids)

# -*- coding:utf-8 -*-
"""
@Author: 风吹落叶
@Contact: waitKey1@outlook.com
@Version: 1.0
@Date: 2024/12/6 18:41
@Describe:
"""
import os
import sys
sys.path.append('../FeasibilityVerification/1_PersonReid/')
from Algorithm.reid_outer_api import ReidPipeline
import Algorithm.libs.config.model_cfgs as cfgs
import cv2
os.environ['KMP_DUPLICATE_LIB_OK']='True'

import sqlite3

def load_sql_feat_info(db_path, db_name):
    conn = sqlite3.connect(db_path,timeout=10,check_same_thread=False)  # 连接到数据库
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name, feat FROM {}".format(db_name))  # 执行查询
        feat_list = []
        label_list = []

        for row in cursor.fetchall():
            data1 = row[0]  # 第一列的值
            data2 = row[1]  # 第二列的值
            label_list.append(data1)
            feat_list.append(list(map(float, data2.split(','))))  # 转换特征为浮点数列表
        print("共计{}条注册用户".format(len(feat_list)))
        for i in range(len(feat_list)):
            print(f"{i}.{label_list[i]}:已记录{len(feat_list[i])}维特征")

    except Exception as e:
        print("Error:", e)
        # 这里可以添加其他的错误处理逻辑
        
    finally:
        cursor.close()  # 关闭游标
        conn.close()  # 关闭数据库连接
        
    return feat_list, label_list

#TODO: 实现把新的id、特征存入列表的函数

#TODO: 完成一个工作流：处理视频，对每个检测到的人脸，提取特征，然后检测现有特征，看是否有相似程度大于阈值的，如果没有，将特征加入现有特征，再命个名，如果有，给人物画个框，标个名字

# 初始基础数据
base_feat_lists, base_idx_lists = load_sql_feat_info(cfgs.DB_PATH, cfgs.DB_NAME)
reid_pipeline = ReidPipeline(base_feat_lists, base_idx_lists, dims=1280)
img = cv2.imread(r"/MultiHeadPassengerFlow/data/画面.png")

class_idx_list = [0]  # 检测人类
boxes, track_ids, clss = reid_pipeline.detect(img, class_idx_list)

features = []
for box in boxes:
    cropped_img = img[int(box[1]):int(box[3]), int(box[0]):int(box[2])]
    feature = reid_pipeline.extract(cropped_img)
    features.append(feature)

search_labels_list = []
search_dist_list = []
filter_box_list = []

search_labels_list, search_dist_list, target_box_list, before_sort_list = reid_pipeline.search(img, boxes)
print(search_labels_list)

search_labels_list.extend(search_labels_list)
search_dist_list.extend(search_dist_list)
filter_box_list.extend(target_box_list)

for label, dist, box in zip(search_labels_list, search_dist_list, filter_box_list):
    print(f'Label: {label}, Distance: {dist}, Box: {box}')




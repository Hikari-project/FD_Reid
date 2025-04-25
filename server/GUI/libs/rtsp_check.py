# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/25 0:09 
@Describe:
'''
import os

import cv2


import cv2
import numpy as np
import matplotlib.pyplot as plt
import cv2
import numpy as np

def is_abnormal_image(image_path):
    if isinstance(image_path,str):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    else:
        img = image_path

    if img is None:
        return True  # 无法读取图像视为异常
    mean = abs(np.mean(img)-128)
    std = np.std(img)
    # 根据经验设定阈值，这里只是示例，可能需要根据实际情况调整
    #print(mean,std)
    if mean < 10 and std < 20:
        return True,mean,std
    return False,-1,-1

def is_abnormal_image_hist(image_path):
    if isinstance(image_path,str):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    else:
        img = image_path
    if img is None:
        return True
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    # 计算直方图的熵，熵越低表示分布越集中，可能是异常图像
    hist = hist.flatten()
    hist = hist / np.sum(hist)
    entropy = -np.sum([p * np.log2(p) if p > 0 else 0 for p in hist])
    # 根据经验设定阈值，这里只是示例，可能需要根据实际情况调整
   #print(entropy)
    if entropy < 8:
        return True,entropy
    return False,-1
def is_img_not_valid(image_path):
    ret1,mean,std=is_abnormal_image(image_path)
    ret2,entropy=is_abnormal_image_hist(image_path)
    if ret1 and ret2:
        print(f'case1:mead {mean} std {std}')
        print(f'case2:entropy {entropy} ')
        return True
    else:
        return False
if __name__ == '__main__':

    imgpath=r'H:\fd_project\FD\FD_REID_Project\GUI\static'

    for root, dirs, files in os.walk(imgpath):
        for name in files:
            file_path = os.path.join(root, name)

            if is_abnormal_image(file_path) and is_abnormal_image_hist(file_path):
                print("图片损坏：",file_path)
            else:
                #print("图片没损坏：", file_path)
                pass
# -*- coding: UTF-8 -*-
'''
@Project :FD_Reid_Web 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/05/07 20:44 
@Describe:
'''
import cv2
from ultralytics import YOLO

# 初始化YOLOv5模型（自动下载或加载本地权重）
<<<<<<< Updated upstream
model = YOLO('human_face.pt')  # 使用yolov8n.pt for YOLOv8
=======
model = YOLO('best.pt')  # 使用yolov8n.pt for YOLOv8
>>>>>>> Stashed changes

# RTSP流地址（替换成你的摄像头地址）
rtsp_url = "rtsp://localhost:5557/live"

# 打开视频流
cap = cv2.VideoCapture(rtsp_url)

# 检查是否成功打开
if not cap.isOpened():
    print("无法打开RTSP流")
    exit()

# 处理视频流
while cap.isOpened():
    # 读取帧
    ret, frame = cap.read()

    if not ret:
        print("无法获取帧，退出...")
        break

    # YOLO检测（调整为合适尺寸，device='cuda'使用GPU）
    results = model(frame, imgsz=640, conf=0.5)  # 调整参数

    # 绘制检测结果
    annotated_frame = results[0].plot()  # 自动绘制边框和标签

    # 显示结果
    cv2.imshow('RTSP YOLO Detection', annotated_frame)

    # 按'q'退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()

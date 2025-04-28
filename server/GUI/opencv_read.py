# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/27 19:52 
@Describe:
'''
import cv2

# RTSP地址
rtsp_url = "rtsp://127.0.0.1:8554/test_2"

# 设置FFmpeg参数（关键：增大缓冲区、使用TCP协议）
ffmpeg_params = {
    'rtsp_transport': 'tcp',  # 强制TCP传输减少丢包
    'buffer_size': '1024000',  # 缓冲区大小（单位：字节）
    'max_delay': '500000',  # 最大延迟（微秒）
    'analyzeduration': '5000000',  # 解析流信息的时长
    'probesize': '5000000'  # 探测流的数据量
}

# 将参数转换为OpenCV格式
open_params = [f'{k}={v}' for k, v in ffmpeg_params.items()]
open_params = ';'.join(open_params)

# 创建视频流对象
cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_FFMPEG_PARAMETERS, open_params)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("帧读取失败，尝试重连...")
        break

    cv2.imshow('RTSP Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

import cv2

rtsp_url = 'rtsp://localhost:5557/live'  # 强制TCP
# rtsp_url = 'rtsp://127.0.0.1:5558/live'  # 强制TCP
cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)    # 显式指定FFmpeg后端

# 设置超时（非所有版本支持）
cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)

if not cap.isOpened():
    print("无法打开RTSP流")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("帧读取失败，重试或退出")
        break
    print(ret)

    cv2.imshow('RTSP Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

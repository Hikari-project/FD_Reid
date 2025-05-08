# -*- coding: UTF-8 -*-
'''
@Project :FD_Reid_Web 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/05/08 17:18 
@Describe:
'''
from main_ReIDTrackerV2 import StreamManager
from RTSPData import RTSPData
import time
if __name__ == '__main__':

    rtsp_datas={}
    stream_manager = StreamManager(mjpeg_server_port=8554, max_reconnect=10,rtsp_datas=rtsp_datas)


    rtsp_url='rtsp://localhost:5557/live'


    # 实例化rtsp对象
    rtsp_data=RTSPData(rtsp_url)
    test_data={'rtsp_url': 'rtsp://localhost:5557/live', 'points': [[551, 324], [733, 308], [586, 197], [548, 259]], 'passway': [[[551, 324], [733, 308]]], 'area_type': 'outside'}

    stream_manager.setup_streams([test_data], 0, stream_id=rtsp_data.stream_id,show_windows=True)

    rtsp_datas[rtsp_url]=rtsp_data

    # 生成已处理的帧
    import threading
    threading.Thread(target=stream_manager.process_video_in_thread,args=(rtsp_url,test_data)).start()


    # 消费已处理的针
    stream_manager.consume_frame(rtsp_url)

    time.sleep(1000)
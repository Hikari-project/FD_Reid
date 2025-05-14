# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/21 9:22 
@Describe:
'''
from urllib.request import Request

import fastapi
import uvicorn


from main_ReIDTrackerV2 import StreamManager
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from contextlib import asynccontextmanager
import os
import threading
import cv2
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# 自定义的类
from base_models import RTSP,VideoConfig
from RTSPData import RTSPData

from fastapi import FastAPI
from logs_server.db.database import engine
from logs_server.models.log import Log
from logs_server.api.log_routes import router as logs_router
from logs_server.db.database import get_db
from logs_server.schemas.log import LogCreate
import logs_server.crud  as crud


Log.metadata.create_all(bind=engine)


# 添加ROI设置的模型
class ROIRequest(BaseModel):
    source_url: str
    roi: List[int]  # [x1, y1, x2, y2]


@asynccontextmanager
async def lifespan(app:FastAPI):
    # 四个算法处理的生成者队列队列
   # app.state.stream_manager = StreamManager(mjpeg_server_port=8554, max_reconnect=10,frame_queue=frame_queue)
    # app.state.stream_manager.custumer_analysis()
    # 存储实例化的RTSP流对象
    app.state.rtsp_datas={}
    app.state.stream_manager = StreamManager(mjpeg_server_port=8554, max_reconnect=10,rtsp_datas=app.state.rtsp_datas)

    # 知道stream_id 返回rtsp
    app.state.stream_2_rtsp_dict={}

    # 已处理的RTSP流信息
    app.state.handleRTSPData={}


    # 视频的线程信息
    app.state.video_thread_info={}
    
    # 存储ROI设置
    app.state.roi_settings = {}
    
    yield
    # 清理资源
    pass
    # 待开发
    #app.state.stream_manager.cleanup()

app = FastAPI(lifespan=lifespan)
app.include_router(logs_router)# 插入日志模块


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# 创建可以访问数据层
static_path='./static'
os.makedirs(static_path,exist_ok=True)
app.mount(static_path[1:], StaticFiles(directory="static"), name="static")

# 全局变量存储推流状态
stream_objects = {}


@app.post('/api/set_roi')
async def set_roi(roi_request: ROIRequest, db: Session = Depends(get_db)):
    """
    设置视频流的ROI（感兴趣区域）
    
    参数:
        roi_request: 包含source_url和roi坐标的请求体
    
    返回:
        设置结果信息
    """
    try:
        source_url = roi_request.source_url
        roi = roi_request.roi
        
        if len(roi) != 4:
            raise HTTPException(status_code=400, detail="ROI必须包含4个坐标点: [x1, y1, x2, y2]")
        
        print(f"收到ROI设置请求: URL={source_url}, ROI={roi}")
        print(f"视频线程信息: {list(app.state.video_thread_info.keys())}")
        
        # 查找视频对应的stream_id
        stream_id = None
        for sid, url in app.state.stream_2_rtsp_dict.items():
            if url == source_url:
                stream_id = sid
                break
        
        if not stream_id:
            # 如果找不到，尝试直接使用URL作为key
            print(f"未找到视频流ID，尝试直接查找: {source_url}")
            if source_url not in app.state.video_thread_info:
                # 最后尝试查找所有视频线程，找到第一个
                if app.state.video_thread_info:
                    first_key = list(app.state.video_thread_info.keys())[0]
                    print(f"使用第一个可用线程: {first_key}")
                    tracker_instance = app.state.video_thread_info[first_key].get('tracker')
                else:
                    raise HTTPException(status_code=404, detail=f"未找到任何视频流")
            else:
                tracker_instance = app.state.video_thread_info[source_url].get('tracker')
        else:
            print(f"找到视频流ID: {stream_id}")
            if stream_id not in app.state.video_thread_info:
                raise HTTPException(status_code=404, detail=f"未找到视频流ID: {stream_id}")
            tracker_instance = app.state.video_thread_info[stream_id].get('tracker')
        
        if not tracker_instance:
            raise HTTPException(status_code=500, detail=f"未找到视频处理实例")
        
        # 设置ROI
        print(f"设置ROI: {roi}")
        tracker_instance.set_roi_rectangle(roi[0], roi[1], roi[2], roi[3])
        
        # 保存ROI设置以便后续使用
        app.state.roi_settings[source_url] = roi
        
        # 记录详细日志
        print(f"成功设置ROI区域: URL={source_url}, 坐标=[{roi[0]}, {roi[1]}, {roi[2]}, {roi[3]}]")
        
        # 记录日志
        log_entry = LogCreate(
            operator_module="客流分析",
            operator_type="设置ROI区域",
            person_name="admin",
            describes=f"为视频流 {source_url} 设置ROI区域: {roi}"
        )
        crud.create_log(db, log_entry)
        
        return {
            "status": "success",
            "message": "ROI区域设置成功",
            "roi": roi
        }
    except Exception as e:
        print(f"设置ROI错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"设置ROI失败: {str(e)}")


def rtsp_generate_mjpeg(rtsp_url):
    # if isinstance(rtsp_url,str):
    #     cap = cv2.VideoCapture(rtsp_url)
    # elif isinstance(rtsp_url,cv2.VideoCapture):
    #     cap = rtsp_url

    cap = cv2.VideoCapture(rtsp_url,cv2.CAP_FFMPEG)
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                break
            ret, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        except Exception as e:
            print('rtsp_generate_mjpeg',str(e))
    cap.release()
from RTSPData import HandleRTSPData
@app.post('/customer-flow/check-rtsp')
async def check_rtsp(rtsp:RTSP,db:Session=Depends(get_db)):
    # 实例化rtsp对象
    rtsp_data=RTSPData(rtsp.rtsp_url)

    # 通过stream_id查询rtsp
    app.state.stream_2_rtsp_dict[rtsp_data.stream_id]=rtsp_data.rtsp_url

    # 在全局变量中存储rtsp数据便于不同变量访问
    app.state.rtsp_datas[rtsp.rtsp_url] = rtsp_data

    # 保存首帧图片
    os.makedirs("static/frames", exist_ok=True)
    frame_path = f"static/frames/{rtsp_data.stream_id}.jpg"
    cv2.imwrite(frame_path,rtsp_data.screen_img)

    # 创建rtsptt
    #app.state.stream_manager.rtsp_2_frames(rtsp_data.rtsp_url)

    # 创建MJPEG推流
    stream_objects[rtsp_data.stream_id]=rtsp_data.rtsp_url # 记录根据id转到对应的rtsp流

    threading.Thread(target=lambda: StreamingResponse(
        rtsp_generate_mjpeg(rtsp_data.rtsp_url),
        media_type="multipart/x-mixed-replace;boundary=frame"
    )).start()

    # 存储已处理信息
    hanle_rtsp_data=HandleRTSPData(rtsp_url=rtsp.rtsp_url,frame_url=f"/static/frames/{rtsp_data.stream_id}.jpg",mjpeg_stream=f"/customer-flow/video-stream/{rtsp_data.stream_id}",name=rtsp_data.name)
    app.state.handleRTSPData[rtsp.rtsp_url]=hanle_rtsp_data

    # 记录开始日志

    start_log = LogCreate(
        operator_module="客流分析",
        operator_type="RTSP流检测",
        person_name="admin",
        describes=f"开始检测RTSP流: {rtsp.rtsp_url}"
    )
    crud.create_log(db, start_log)

    return {
        "status": "success",
        "frame_id": rtsp_data.stream_id,
        "frame_url": f"/static/frames/{rtsp_data.stream_id}.jpg",
        "size": {"height": rtsp_data.height, "width": rtsp_data.width},
        "mjpeg_stream": f"/customer-flow/video-stream/{rtsp_data.stream_id}"
    }


@app.get("/customer-flow/video-stream/{stream_id}")
async def video_stream(stream_id: str):
    """推流默认视频流"""
    if stream_id not in stream_objects:
        raise HTTPException(status_code=404, detail="推流不存在")
    return StreamingResponse(
        rtsp_generate_mjpeg(stream_objects[stream_id]),
        media_type="multipart/x-mixed-replace;boundary=frame"
    )


@app.get('/customer-flow/video_feed')
async def video_feed(stream_id):
    """推流处理的视频流"""


    rtsp_url=app.state.stream_2_rtsp_dict[stream_id]

    print("。、video_feed3 调用", stream_id,' rtsp_url: ',rtsp_url)

    return StreamingResponse(
        app.state.stream_manager.consume_frame(rtsp_url),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )


@app.post('/customer-flow/custome-analysisV2')
async def custome_analysisV2(video_config:VideoConfig):
    # 获取传入的视频
    config = video_config.dict()['videos']
    print("videoData:", str(config))

    rtsp_data=app.state.rtsp_datas[config[0]['rtsp_url']]
    print(rtsp_data)

    #
    # index=
    index=0
    mjpeg_list = app.state.stream_manager.setup_streams(config, index, stream_id=rtsp_data.stream_id,show_windows=True)
    print('f返回数据：',str(mjpeg_list))
    #app.state.rtsp_datas[rtsp_url]

    # 启动处理线程 ，存储处理线程的信息,队列信息
    app.state.video_thread_info[rtsp_data.stream_id] =await app.state.stream_manager.process_video_in_thread(config[0]['rtsp_url'],config[0])
    
    # 检查是否存在预设的ROI设置
    source_url = config[0]['rtsp_url']
    if source_url in app.state.roi_settings:
        # 如果存在预设ROI，自动应用
        roi = app.state.roi_settings[source_url]
        tracker_instance = app.state.video_thread_info[rtsp_data.stream_id].get('tracker')
        if tracker_instance:
            tracker_instance.set_roi_rectangle(roi[0], roi[1], roi[2], roi[3])
            print(f"已自动应用预设ROI: {roi} 到视频流: {source_url}")
    else:
        # 如果不存在预设ROI，设置默认值在中间位置
        tracker_instance = app.state.video_thread_info[rtsp_data.stream_id].get('tracker')
        if tracker_instance:
            # 获取视频宽高
            if hasattr(tracker_instance, 'video_width') and hasattr(tracker_instance, 'video_height'):
                width = tracker_instance.video_width
                height = tracker_instance.video_height
                # 计算中间位置的ROI
                x1 = int(width * 0.2)
                y1 = int(height * 0.15)
                x2 = int(width * 0.8)
                y2 = int(height * 0.85)
                # 设置ROI
                tracker_instance.set_roi_rectangle(x1, y1, x2, y2)
                print(f"已设置默认ROI在中间位置: [{x1}, {y1}, {x2}, {y2}] 到视频流: {source_url}")
                # 保存ROI设置
                app.state.roi_settings[source_url] = [x1, y1, x2, y2]

    # 存储rtsp流信息
    app.state.handleRTSPData[config[0]['rtsp_url']].mjpeg_url=mjpeg_list[0]['mjpeg_url']
    return {"ret": 0, "message": '已开启', "res": mjpeg_list}

@app.post('/customer-flow/stop-analysis')
def stop_analysis(rtsp:RTSP):
    app.state.stream_manager.stop_process_video_in_thread(rtsp.rtsp_url)
    return {"ret":0,"message":"停止成功"}

@app.get('/customer-flow/get-rtsp')
def get_rtsp():
    """返回rtsp流信息"""
    return {"ret":0,"HandleRTSPData":app.state.handleRTSPData}


@app.post('/customer-flow/set-rtsp-name')
def set_rtsp_name(rtsp:RTSP):
    """返回rtsp流信息"""
    app.state.handleRTSPData[rtsp.rtsp_url].name = rtsp.name
    return {"ret":0,"message":f"{rtsp.rtsp_url}设置别名{rtsp.name} 设置成功"}
# 内存占用分析模块
# import tracemalloc
# tracemalloc.start(10)  # 记录前10个内存分配点
# @app.get("/memory_snapshot")
# async def get_memory_snapshot():
#     snapshot = tracemalloc.take_snapshot()
#     top_stats = snapshot.statistics('lineno')
#     return {"memory_stats": [str(stat) for stat in top_stats[:5]]}

if __name__ == '__main__':
    uvicorn.run("appV2:app", host='127.0.0.1', port=3002)

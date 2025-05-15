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


from main_ReIDTrackerV3 import StreamManager
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

# 自定义的类
from base_models import RTSP,VideoConfig
from RTSPData import RTSPData

from fastapi import FastAPI
from logs_server.db.database import engine
from logs_server.models.log import Log
from logs_server.api.log_routes import router as logs_router
from logs_server.db.database import get_db
from logs_server.schemas.log import LogCreate
import logs_server.log_crud as crud


Log.metadata.create_all(bind=engine)

from ws_manager import ConnectionManager
from fastapi import FastAPI,WebSocket,WebSocketDisconnect




@asynccontextmanager
async def lifespan(app:FastAPI):
    # 四个算法处理的生成者队列队列
   # app.state.stream_manager = StreamManager(mjpeg_server_port=8554, max_reconnect=10,frame_queue=frame_queue)
    # app.state.stream_manager.custumer_analysis()
    # 存储实例化的RTSP流对象
    app.state.rtsp_datas={}
    app.state.stream_manager = StreamManager(mjpeg_server_port=8554, max_reconnect=10,rtsp_datas=app.state.rtsp_datas)

    # 知道stream_id 返回rtsp_url
    app.state.stream_2_rtsp_dict={}

    # 已处理的RTSP流信息
    app.state.handleRTSPData={}


    # 视频的线程信息
    app.state.video_thread_info={}

    # wsmanage
    app.state.ws_manager = ConnectionManager(app.state.rtsp_datas)
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

    # index=
    index=0
    mjpeg_list = app.state.stream_manager.setup_streams(config, index, stream_id=rtsp_data.stream_id,show_windows=True)
    print('f返回数据：',str(mjpeg_list))
    #app.state.rtsp_datas[rtsp_url]

    # 启动处理线程 ，存储处理线程的信息,队列信息
    app.state.video_thread_info[rtsp_data.stream_id] =await app.state.stream_manager.process_video_in_thread(config[0]['rtsp_url'],config[0])

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


@app.websocket("/customer-flow/ws")
async def websocket_endpoint(websocket: WebSocket):
    """请求这个rtsp，返回这个rtsp流的处理结果"""
    rtsp_url = websocket.query_params.get("rtsp_url")
    if not rtsp_url:
        await websocket.close(code=1008, reason="RTSP URL required")
        return

    await app.state.ws_manager.connect(websocket, rtsp_url)

    try:
        while True:
            # 保持连接活跃，接收任意消息（可选）
            await websocket.receive_text()
    except WebSocketDisconnect:
        await app.state.ws_manager.disconnect(rtsp_url)

if __name__ == '__main__':
    uvicorn.run("appV3:app", host='0.0.0.0', port=3002)

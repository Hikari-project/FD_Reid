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

import fastapi


from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse,HTMLResponse
import asyncio
import cv2
import time
import threading
from typing import List,Tuple
from main_ReIDTrackerV2 import StreamManager

from contextlib import asynccontextmanager
import os
import uuid

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

# 自定义的库
from libs.rtsp_check import is_img_not_valid
@asynccontextmanager
async def lifespan(app:FastAPI):
    # 四个算法处理的生成者队列队列
    frame_queue=[asyncio.Queue(maxsize=10),asyncio.Queue(maxsize=10),asyncio.Queue(maxsize=10),asyncio.Queue(maxsize=10)]
    # 存储处理视频队列
    app.state.frame_queue = frame_queue
    # 存储视频信息
    app.state.videos_data={}
    # 存储处理线程的信息,用于后端管理线程资源
    app.state.video_thread_info={}
    # 记录从rtsp到队列序号的映射
    app.state.video_rtsp_dict= {}

    app.state.stream_manager = StreamManager(mjpeg_server_port=8554, max_reconnect=10,frame_queue=frame_queue)
    # app.state.stream_manager.custumer_analysis()


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

    #
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


@app.get('/customer-flow/video_feed')
async def video_feed(video_id:int):
    print("。、video_feed3 调用")
    print(video_id)
    return StreamingResponse(
        app.state.stream_manager.consume_frame(video_id),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )


@app.get('/hello')
async def hello(video_id:str):
    print("。、hello 调用")
    print(video_id)
    return {"hello":video_id}

from pydantic import BaseModel, conlist
from pydantic import BaseModel, Field
from typing import Annotated


class VideoData(BaseModel):
    """视频分析基础数据模型"""
    rtsp_url: str = Field(
        example="rtsp://localhost:5555/live",
        description="RTSP视频流地址"
    )

    points: list[Annotated[list[int], Field(
        min_length=2,
        max_length=2,
        example=[100, 400]
    )]]

    passway: list[list[Annotated[list[int], Field(
        min_length=2,
        max_length=2,
        example=[[500, 200]]
    )]]]
    area_type:str
# {'videos': [{'rtsp_url': 'rtsp://localhost:5555/live', 'points': [[100, 400], [500, 400], [500, 200], [100, 200]], 'passway': [[[500, 200], [100, 200]]], 'area_type': 'inline'}]}

class VideoConfig(BaseModel):
    """单个视频流配置"""
    videos: List[VideoData]

@app.post('/customer-flow/setting')
async def setting(items:VideoConfig):
    config_list=items.dict()
    print(config_list)
    mjpeg_list = app.state.stream_manager.setup_streams(config_list, show_windows=True)
    return {"ret":0,"message":str(mjpeg_list)}


@app.post('/customer-flow/custome-analysis')
async def custome_analysis(items: VideoConfig):
    VideoConfig=items.dict()
    print("videoData:",str(VideoConfig))
    config=VideoConfig['videos']
    # 设置视频值
    mjpeg_list = app.state.stream_manager.setup_streams(config, show_windows=True)
    print(mjpeg_list)
    # 处理视频

    app.state.stream_manager.start_processing(skip_frames=4, match_thresh=0.15, is_track=True)
    return {"ret": 0, "message": '已开启',"res":mjpeg_list}

@app.post('/customer-flow/custome-analysisV2')
async def custome_analysis(items: VideoConfig):
    VideoConfig=items.dict()
    print("videoData:",str(VideoConfig))
    config=VideoConfig['videos']

    # 设置视频值
    queue_index = app.state.stream_manager.get_valid_queue_index()
    print(f'获取到可用队列：{queue_index}')

    mjpeg_list = app.state.stream_manager.setup_streams(config,queue_index, show_windows=True)
    print(mjpeg_list)

    video_data=config[0]

    # 清除队列信息
    app.state.stream_manager.clear_queue(queue_index)
    # 存储处理线程的信息,队列信息
    app.state.video_thread_info[queue_index]=app.state.stream_manager.process_video_in_thread(video_data['rtsp_url'],video_data,queue_index=queue_index)

    app.state.video_rtsp_dict[video_data['rtsp_url']]=queue_index


    # 处理视频
   # app.state.stream_manager.start_processing(skip_frames=4, match_thresh=0.15, is_track=True)
    return {"ret": 0, "message": '已开启',"res":mjpeg_list}

class VideoTemp(BaseModel):
    rtsp_url: str = Field()

@app.post('/customer-flow/stop-analysis')
def stop_analysis(videoTemp:VideoTemp):
    app.state.stream_manager.stop_process_video_in_thread(videoTemp.rtsp_url)
    return {"ret":0,"message":"停止成功"}



def generate_mjpeg(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    cap.release()


from pydantic import BaseModel
class RTSP(BaseModel):
    rtsp_url:str


@app.post("/customer-flow/check-rtsp")
async def check_rtsp(rtsp: RTSP):
    # 尝试打开RTSP流
    rtsp_url=rtsp.rtsp_url
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="无法打开RTSP流")

    # 增加重连次数和超时处理

    valid_frame =None
    # for i in range(20):
    #     ret,valid_frame=cap.read()

    # 捕获首帧
    max_attempts=100
    for i in range(max_attempts):
        ret, frame = cap.read()
        if ret and frame is not None and frame.size != 0:
            if is_img_not_valid(frame):
                continue
            else:
                print('发现未损坏图片',str(i))
                valid_frame=frame
                break
        cv2.waitKey(1)


    if not ret or valid_frame is None:
        cap.release()
        raise HTTPException(status_code=400, detail="无法读取视频帧")

    h,w=valid_frame.shape[:2]
    print("宽高")
    print(w,h)
    # 保存首帧图片
    os.makedirs("static/frames", exist_ok=True)
    frame_id = str(uuid.uuid4())
    frame_path = f"static/frames/{frame_id}.jpg"
    cv2.imwrite(frame_path, valid_frame)

    # 创建MJPEG推流
    stream_id = str(uuid.uuid4())
    stream_objects[stream_id] = {
        'rtsp_url': rtsp_url,
        'active': True
    }

    app.state.stream_manager.rtsp_2_frames(rtsp_url)

    # 启动推流线程
    threading.Thread(target=lambda: StreamingResponse(
        generate_mjpeg(rtsp_url),
        media_type="multipart/x-mixed-replace;boundary=frame"
    )).start()

    videodata={
        "cap":cap,
        "frame_url": f"/static/frames/{frame_id}.jpg",
        "size":{"height":h,"width":w},
        "mjpeg_stream": f"/customer-flow/video-stream/{stream_id}",
        "last_used":time.time()
    }

    app.state.videos_data[frame_id]=videodata
    return {
        "status": "success",
        "frame_id":frame_id,
        "frame_url": f"/static/frames/{frame_id}.jpg",
        "size":{"height":h,"width":w},
        "mjpeg_stream": f"/customer-flow/video-stream/{stream_id}"
    }



@app.get("/customer-flow/video-stream/{stream_id}")
async def video_stream(stream_id: str):
    if stream_id not in stream_objects:
        raise HTTPException(status_code=404, detail="推流不存在")

    return StreamingResponse(
        generate_mjpeg(stream_objects[stream_id]['rtsp_url']),
        media_type="multipart/x-mixed-replace;boundary=frame"
    )

import tracemalloc
tracemalloc.start(10)  # 记录前10个内存分配点
@app.get("/memory_snapshot")
async def get_memory_snapshot():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    return {"memory_stats": [str(stat) for stat in top_stats[:5]]}



if __name__ == "__main__":
    import uvicorn


    # 获取主事件循环
    mainloop = asyncio.get_event_loop()
    asyncio.set_event_loop(mainloop)

    config = uvicorn.Config('app:app',
                         #   host="0.0.0.0",
                            host="127.0.0.1",
                            port=3002,
                            http="h11",
                            timeout_keep_alive=30,
                            limit_concurrency=40)

    # config = uvicorn.Config(app, host="127.0.0.1", port=8765, loop=main_loop)
    server = uvicorn.Server(config)

    mainloop.run_until_complete(server.serve())




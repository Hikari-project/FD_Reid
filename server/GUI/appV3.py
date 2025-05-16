# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/21 9:22 
@Describe:
'''
import asyncio
import queue
from concurrent.futures import ThreadPoolExecutor
from datetime import time
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
    app.state.rtsp_stream_id={}
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
# 降低分辨率
target_width = 1280
# 全局变量存储推流状态
stream_objects_rtsp = {}
def _encode_frame( frame):
    """独立编码函数"""
    # 可在此处添加硬件加速逻辑
    # if is_resize:
    #     frame=cv2.resize(frame,(width,height))
    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
    return buffer.tobytes()
# 创建编码线程池（根据CPU核心数调整）
encode_executor = ThreadPoolExecutor(max_workers=4)
async def rtsp_generate_mjpeg(rtsp_url):
    # 优化视频捕获参数
    cap = cv2.VideoCapture(rtsp_url+'?tcp', cv2.CAP_FFMPEG)

    # 强制使用 TCP 传输协议
    # cap.set(cv2.CAP_PROP_FFMPEG_TRANSPORT_OPT, "tcp")

    # 减少缓冲区大小（默认值：500ms）
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # 单位：帧数

    # 设置超时时间（单位：毫秒）
    #cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MS, 5000)

    # 配置解码参数
    cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)  # 启用硬件加速
    loop = asyncio.get_event_loop()

    # is_resize = False
    # # 如果画面大于1920则进行resize
    # min_width_px = 1280
    #
    # ret, frame = cap.read()
    # height, width = frame.shape[:2]
    #
    # if width > min_width_px:
    #     new_h = height * min_width_px // width
    #     width, height = min_width_px, new_h
    #     is_resize = True

    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                # 自动重连机制
                print("Connection lost, reconnecting...")
                cap.release()
                cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                continue

            # 将编码任务提交到线程池
            _frame_cache = await loop.run_in_executor(
                encode_executor,
                _encode_frame,  # 独立编码函数
                frame
            )

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + _frame_cache + b'\r\n\r\n')
        except Exception as e:
            print('rtsp_generate_mjpeg',str(e))
    cap.release()

queue_rtsp_map={}
queue_list=[asyncio.Queue(maxsize=5)for i in range(12)]
queue_valid_map={}
for i in range(len(queue_list)):
    queue_valid_map[i]=True
def getvalid_queue():
    for key,value in queue_valid_map.items():
        if value:
            queue_valid_map[key]=False
            return key

async def read_rtsp(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    cap.set(cv2.CAP_PROP_FPS, 25)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '5'))

    valid_index = getvalid_queue()
    queue_rtsp_map[rtsp_url] = valid_index

    loop = asyncio.get_event_loop()
    try:
        while True:
            # 异步执行阻塞的 read()
            ret, frame = await loop.run_in_executor(None, cap.read)
            if not ret:
                break
            await queue_list[valid_index].put(frame)
            await asyncio.sleep(0.02)
    finally:
        cap.release()
        queue_valid_map[valid_index] = True
        del queue_rtsp_map[rtsp_url]
async def generate_mjpegV2(rtsp_url):
    """专门一个队列用于获取和推流"""
    queue_index=queue_rtsp_map[rtsp_url]
    import time
    start=time.time()
    while True:
        frame=await queue_list[queue_index].get()
        fps=1/(time.time()-start)
        print(f'rtsp:{rtsp_url},{fps:.2f}')
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

async def generate_mjpegV3(rtsp_url):
    rtsp_data = app.state.rtsp_datas[rtsp_url]
    """专门一个队列用于获取和推流"""
    origin_frame_queue=rtsp_data.origin_frame_queue
    import time
    prestart=time.time()-2
    while True:
        frame= origin_frame_queue.get()
        div=min(0.002,time.time()-prestart)
        fps=1/div
        prestart=time.time()
        print(f'rtsp:{rtsp_url},{fps:.2f}')
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')



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

    # threading.Thread(target=lambda: StreamingResponse(
    #     rtsp_generate_mjpeg(rtsp_data.rtsp_url),
    #     media_type="multipart/x-mixed-replace;boundary=frame"
    # )).start()

    asyncio.create_task(read_rtsp(rtsp_data.rtsp_url))

    # 存储已处理信息
    hanle_rtsp_data=HandleRTSPData(rtsp_url=rtsp.rtsp_url,frame_url=f"/static/frames/{rtsp_data.stream_id}.jpg",mjpeg_stream=f"/customer-flow/video-stream/{rtsp_data.stream_id}",name=rtsp_data.name,stream_id=rtsp_data.stream_id)
    app.state.handleRTSPData[rtsp.rtsp_url]=hanle_rtsp_data
    app.state.rtsp_stream_id[rtsp_data.stream_id]=rtsp.rtsp_url # stream_id映射到rtsp


    # 记录开始日志
    start_log = LogCreate(
        operator_module="客流分析",
        operator_type="RTSP流检测",
        person_name="admin",
        describes=f"开始检测RTSP流: {rtsp.rtsp_url}"
    )

    crud.create_log(db, start_log)
    stream_objects_rtsp[rtsp_data.stream_id] = {
        'rtsp_url': rtsp_data.rtsp_url,
        'active': True
    }
    return {
        "status": "success",
        "frame_id": rtsp_data.stream_id,
        "frame_url": f"/static/frames/{rtsp_data.stream_id}.jpg",
        "size": {"height": rtsp_data.height, "width": rtsp_data.width},
        "mjpeg_stream": f"/customer-flow/video-stream/{rtsp_data.stream_id}",
        "stream_id": rtsp_data.stream_id,
    }

@app.get("/customer-flow/video-stream/{stream_id}")
async def video_stream(stream_id: str):
    if stream_id not in stream_objects_rtsp:
        raise HTTPException(status_code=404, detail="推流不存在")

    print(stream_id)
    return StreamingResponse(
        generate_mjpegV3(stream_objects_rtsp[stream_id]['rtsp_url']),
        media_type="multipart/x-mixed-replace;boundary=frame"
    )


@app.get("/customer-flow/video-streamV2/{stream_id}")
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
async def stop_analysis(rtsp:RTSP):
    app.state.stream_manager.stop_process_video_in_thread(rtsp.rtsp_url)

    stream_id=app.state.rtsp_stream_id[rtsp.rtsp_url]
    await app.state.ws_manager.disconnect(stream_id)


    return {"ret":0,"message":"停止成功"}


@app.get('/customer-flow/get-rtsp')
def get_rtsp():
    """返回rtsp流信息"""


    for key ,value in app.state.rtsp_stream_id.items():
        app.state.rtsp_stream_id[key]=value  #
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
    print(f'ws连接请求中。{ websocket.query_params.get("rtsp_url")}')
    rtsp_url = websocket.query_params.get("rtsp_url")
    try:
        rtsp_url=app.state.rtsp_stream_id[rtsp_url] # 将传入的stream_id转为rtsp_url
    except Exception as e:
        print(e)
        return

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

# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/21 9:22 
@Describe:
'''
import fastapi


from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse,HTMLResponse
import asyncio
import cv2
import time
import threading
from typing import List,Tuple
from main_ReIDTracker import StreamManager

from contextlib import asynccontextmanager
import os
import uuid
import threading
import cv2
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app:FastAPI):
    # 四个算法处理的生成者队列队列
    frame_queue=[asyncio.Queue(),asyncio.Queue(),asyncio.Queue(),asyncio.Queue()]
    app.state.frame_queue = frame_queue
    app.state.stream_manager = StreamManager(mjpeg_server_port=8554, max_reconnect=10,frame_queue=frame_queue)
    # app.state.stream_manager.custumer_analysis()


    yield
    # 清理资源
    pass
    # 待开发
    #app.state.stream_manager.cleanup()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
static_path='./static'
os.makedirs(static_path,exist_ok=True)

app.mount(static_path[1:], StaticFiles(directory="static"), name="static")

# 全局变量存储推流状态
stream_objects = {}



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
        example="rtsp://localhost:8554/live", # 5555
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

def generate_mjpeg(rtsp_url):
    # 使用FFMPEG解码器打开RTSP流
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 5)  # 设置缓冲区大小
    
    # 连接重试
    max_retries = 5
    retry_count = 0
    retry_delay = 2  # 秒
    
    while not cap.isOpened() and retry_count < max_retries:
        print(f"无法打开视频流，正在重试... ({retry_count+1}/{max_retries})")
        time.sleep(retry_delay)
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 5)
        retry_count += 1
    
    if not cap.isOpened():
        print(f"无法打开视频流: {rtsp_url}")
        return
        
    while True:
        ret, frame = cap.read()
        if not ret:
            print("视频流读取错误，尝试重新连接...")
            cap.release()
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 5)
            
            # 如果重连失败，等待一会再试
            if not cap.isOpened():
                time.sleep(1)
                continue
                
            # 尝试再次读取帧
            ret, frame = cap.read()
            if not ret:
                continue
                
        # 压缩图像质量以提高传输效率
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]  # 85%的质量
        ret, jpeg = cv2.imencode('.jpg', frame, encode_params)
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    
    cap.release()

from pydantic import BaseModel
class RTSP(BaseModel):
    rtsp_url:str


@app.post("/customer-flow/check-rtsp")
async def check_rtsp(rtsp: RTSP):
    # 尝试打开RTSP流
    rtsp_url = rtsp.rtsp_url
    
    # 使用FFMPEG解码器
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 5)  # 设置缓冲区大小
    
    # 连接重试
    max_retries = 5
    retry_count = 0
    retry_delay = 1  # 秒
    
    while not cap.isOpened() and retry_count < max_retries:
        print(f"无法打开视频流，正在重试... ({retry_count+1}/{max_retries})")
        await asyncio.sleep(retry_delay)
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 5)
        retry_count += 1
        
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="无法打开RTSP流，请检查地址和网络连接")

    # 捕获首帧，最多尝试30次
    frame = None
    for i in range(30):
        ret, frame = cap.read()
        if ret:
            break
        await asyncio.sleep(0.1)
            
    if frame is None:
        cap.release()
        raise HTTPException(status_code=400, detail="无法读取视频帧，请检查视频源")
        
    h, w = frame.shape[:2]
    print("视频分辨率:", w, h)
    
    # 保存首帧图片
    os.makedirs("static/frames", exist_ok=True)
    frame_id = str(uuid.uuid4())
    frame_path = f"static/frames/{frame_id}.jpg"
    cv2.imwrite(frame_path, frame)
    cap.release()

    # 创建MJPEG推流
    stream_id = str(uuid.uuid4())
    stream_objects[stream_id] = {
        'rtsp_url': rtsp_url,
        'active': True
    }
    # 启动推流线程
    threading.Thread(target=lambda: StreamingResponse(
        generate_mjpeg(rtsp_url),
        media_type="multipart/x-mixed-replace;boundary=frame"
    )).start()

    return {
        "status": "success",
        "frame_url": f"/static/frames/{frame_id}.jpg",
        "size":{"height":h,"width":w},
        "mjpeg_stream": f"/customer-flow/video-stream/{stream_id}"
    }


@app.get("/customer-flow/video-stream/{stream_id}")
async def video_stream(stream_id: str):
    if stream_id not in stream_objects:
        raise HTTPException(status_code=404, detail="推流不存在")
    
    # 检查流是否仍然活跃
    if not stream_objects[stream_id].get('active', False):
        raise HTTPException(status_code=410, detail="推流已关闭")
        
    return StreamingResponse(
        generate_mjpeg(stream_objects[stream_id]['rtsp_url']),
        media_type="multipart/x-mixed-replace;boundary=frame"
    )


if __name__ == "__main__":

    import uvicorn

    # 获取主事件循环
    mainloop = asyncio.get_event_loop()
    asyncio.set_event_loop(mainloop)

    config = uvicorn.Config('app:app',
                         #   host="0.0.0.0",
                            host="127.0.0.1",# 127.0.0.1
                            port=3009,
                            http="h11",
                            timeout_keep_alive=30,
                            limit_concurrency=40)

    # config = uvicorn.Config(app, host="127.0.0.1", port=8765, loop=main_loop)
    server = uvicorn.Server(config)

    mainloop.run_until_complete(server.serve())



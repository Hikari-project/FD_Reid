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

   # cap.set(cv2.CAP_PROP_BUFFERSIZE,2)

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



@app.get("/customer-flow/get-cap")
async def get_latest_frame(frame_id: str):
    video_data = app.state.videos_data.get(frame_id)
    if not video_data:
        raise HTTPException(status_code=404, detail="无效的frame_id")

    # 更新最后使用时间
    video_data['last_used'] = time.time()

    # 读取最新帧
    cap = video_data['cap']
    while True:  # 跳过部分帧
        for i in range(5):
            ret, frame = cap.read()
            print(ret)
            if ret:break
        if not ret :break
        cv2.imshow('frame', frame)
        cv2.waitKey(1)

@app.get("/customer-flow/video-stream/{stream_id}")
async def video_stream(stream_id: str):
    if stream_id not in stream_objects:
        raise HTTPException(status_code=404, detail="推流不存在")
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
                            host="127.0.0.1",
                            port=3009,
                            http="h11",
                            timeout_keep_alive=30,
                            limit_concurrency=40)

    # config = uvicorn.Config(app, host="127.0.0.1", port=8765, loop=main_loop)
    server = uvicorn.Server(config)

    mainloop.run_until_complete(server.serve())



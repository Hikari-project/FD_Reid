# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/28 15:09 
@Describe:
'''
# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/28 14:30 
@Describe:
'''

import fastapi,uvicorn
import requests
from pydantic import BaseModel, Field
from typing import Annotated
from typing import List
from fastapi.middleware.cors import CORSMiddleware

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

class VideoConfig(BaseModel):
    """单个视频流配置"""
    videos: List[VideoData]

class RTSP(BaseModel):
    rtsp_url:str


class VideoTemp(BaseModel):
    rtsp_url: str = Field()

target_url='http://127.0.0.1:3007'
app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get('/')
def index():
    return {'ret':0,'message':"中轉服務正常"}


@app.post('/customer-flow/check-rtsp')
def check_rtsp(rtsp:RTSP):
    """ 中转到内网的服务 """
    res=requests.post(target_url+'/customer-flow/check-rtsp',json=rtsp.model_dump())
    return res.json()

@app.post('/customer-flow/stop-analysis')
def stop_analysis(videoTemp:VideoTemp):
    """ 中转到内网的服务 """
    res=requests.post(target_url+'/customer-flow/stop-analysis',json=videoTemp.model_dump())
    return res.json()

@app.post('/customer-flow/custome-analysisV2')
async def custome_analysis(items: VideoConfig):
    """ 中转到内网的服务 """
    res = requests.post(target_url + '/customer-flow/custome-analysisV2', json=items.model_dump())
    return res.json()




if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=3008)


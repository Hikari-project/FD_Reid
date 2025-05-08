# -*- coding: UTF-8 -*-
'''
@Project :FD_Reid_Web 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/05/08 0:01 
@Describe:
'''
from pydantic import BaseModel, Field
from typing import Annotated
from typing import List

class RTSP(BaseModel):
    rtsp_url:str

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
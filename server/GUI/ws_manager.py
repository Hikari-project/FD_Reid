# -*- coding: UTF-8 -*-
'''
@Project :FD_Reid_Web 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/05/16 0:27 
@Describe:
'''
import asyncio
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from typing import Dict

app = FastAPI()


class ConnectionManager:
    def __init__(self,rtsp_datas={}):
        # 存储活跃连接及其对应的发送任务
        self.active_connections: Dict[str, WebSocket] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self.rtsp_datas = rtsp_datas


    async def connect(self, websocket: WebSocket, rtsp_url: str):
        await websocket.accept()
        self.active_connections[rtsp_url] = websocket
        # 为每个流创建独立的数据发送任务
        self.tasks[rtsp_url] = asyncio.create_task(
            self._send_data_loop(websocket, rtsp_url)
        )



    async def _send_data_loop(self, websocket: WebSocket, rtsp_url: str):
        """独立数据发送循环"""
        try:
            print(self.rtsp_datas)
            while True:
                data = await self.rtsp_datas[rtsp_url].process_frame_queue.get()
                await websocket.send_json(data)
              #  await asyncio.sleep(0.05)  # 50ms间隔
        except WebSocketDisconnect:
            print(f"Connection closed for {rtsp_url}")
        finally:
            await self.disconnect(rtsp_url)

    async def disconnect(self, stream_id: str):
        if stream_id in self.active_connections:
            rtsp_url=self.rtsp_stream_id[stream_id]
            del self.active_connections[rtsp_url]
        if rtsp_url in self.tasks:
            self.tasks[rtsp_url].cancel()
            try:
                await self.tasks[rtsp_url]
            except asyncio.CancelledError:
                pass
            del self.tasks[rtsp_url]
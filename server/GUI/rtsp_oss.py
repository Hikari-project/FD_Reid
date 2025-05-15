import asyncio
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from typing import Dict

app = FastAPI()


class ConnectionManager:
    def __init__(self,process_queue=asyncio.Queue()):
        # 存储活跃连接及其对应的发送任务
        self.active_connections: Dict[str, WebSocket] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self.process_queue = process_queue
    async def connect(self, websocket: WebSocket, rtsp_url: str):
        await websocket.accept()
        self.active_connections[rtsp_url] = websocket
        # 为每个流创建独立的数据发送任务
        self.tasks[rtsp_url] = asyncio.create_task(
            self._send_data_loop(websocket, rtsp_url)
        )

    async def _generate_data(self, rtsp_url: str):
        """根据不同的RTSP流生成不同的模拟数据"""


        return base_data

    async def _send_data_loop(self, websocket: WebSocket, rtsp_url: str):
        """独立数据发送循环"""
        try:
            while True:
                data = await self._generate_data(rtsp_url)
                await websocket.send_json(data)
                await asyncio.sleep(0.05)  # 50ms间隔
        except WebSocketDisconnect:
            print(f"Connection closed for {rtsp_url}")
        finally:
            await self.disconnect(rtsp_url)

    async def disconnect(self, rtsp_url: str):
        if rtsp_url in self.active_connections:
            del self.active_connections[rtsp_url]
        if rtsp_url in self.tasks:
            self.tasks[rtsp_url].cancel()
            try:
                await self.tasks[rtsp_url]
            except asyncio.CancelledError:
                pass
            del self.tasks[rtsp_url]


manager = ConnectionManager()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/customer-flow/ws")
async def websocket_endpoint(websocket: WebSocket):
    rtsp_url = websocket.query_params.get("rtsp_url")
    if not rtsp_url:
        await websocket.close(code=1008, reason="RTSP URL required")
        return

    await manager.connect(websocket, rtsp_url)

    try:
        while True:
            # 保持连接活跃，接收任意消息（可选）
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(rtsp_url)


# 运行命令：uvicorn main:app --reload
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

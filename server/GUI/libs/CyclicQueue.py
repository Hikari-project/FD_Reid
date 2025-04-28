# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/28 8:39 
@Describe:
'''
import asyncio
from collections import deque
from typing import Any

class CyclicQueue(asyncio.Queue):
    """自动丢弃旧元素的异步循环队列"""
    def __init__(self, maxsize: int = 0) -> None:
        super().__init__(maxsize)
        # 使用 deque 替代默认队列，支持maxlen自动截断
        self._queue = deque(maxlen=maxsize) if maxsize > 0 else deque()

    def _put(self, item: Any) -> None:
        # 非阻塞式放入，自动丢弃旧元素
        if self.maxsize > 0 and len(self._queue) >= self.maxsize:
            # 丢弃最旧元素
            self._queue.popleft()
        self._queue.append(item)
        # 立即唤醒等待的消费者
        self._wakeup_next(self._getters)

    async def put(self, item: Any) -> None:
        # 重写put方法，避免阻塞
        await self._put(item)

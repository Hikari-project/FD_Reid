# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/05/12 23:17 
@Describe:
'''
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class LogCreate(BaseModel):
    operator_module: str
    operator_type: str
    person_name: str
    describes: str

class LogResponse(LogCreate):
    id: Optional[int]=1
    create_time: Optional[datetime]=None
    state: Optional[str]='成功请求'
    class Config:
        orm_mode = True
# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/05/12 23:17 
@Describe:
'''
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..db.database import Base

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)  # 字符串类型的主键
    operator_module = Column(String, index=True)  # 操作模块
    operator_type = Column(String, index=True)  # 操作类型
    person_name = Column(String)  # 人员姓名
    create_time =Column(DateTime, default=datetime.utcnow) # 创建时间
    state =  Column(String(50), default="成功请求")
    describes = Column(String)  # 描述信息

# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/05/12 23:20 
@Describe:
'''
from sqlalchemy.orm import Session
from .models import log as model_log
from .schemas import log as schema_log

def create_log(db: Session, log: schema_log.LogCreate):
    db_log = model_log.Log(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model_log.Log).offset(skip).limit(limit).all()

def get_log_by_id(db: Session, log_id: int):
    return db.query(model_log.Log).filter(model_log.Log.id == log_id).first()

def update_log(db: Session, log_id: int, log: schema_log.LogCreate):
    db_log = db.query(model_log.Log).filter(model_log.Log.id == log_id).first()
    if db_log:
        for key, value in log.dict().items():
            setattr(db_log, key, value)
        db.commit()
        db.refresh(db_log)
    return db_log

def delete_log(db: Session, log_id: int):
    db_log = db.query(model_log.Log).filter(model_log.Log.id == log_id).first()
    if db_log:
        db.delete(db_log)
        db.commit()
        return True
    return False

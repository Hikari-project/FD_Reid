# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/05/12 23:18 
@Describe:
'''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..schemas import log as schemas
from .. import crud


router = APIRouter(prefix="/logs", tags=["logs"])

@router.post("/", response_model=schemas.LogResponse)
def create_log_entry(log: schemas.LogCreate, db: Session = Depends(get_db)):
    print(log.dict())
    return crud.create_log(db, log)

@router.get("/", response_model=list[schemas.LogResponse])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_logs(db, skip=skip, limit=limit)

@router.get("/{log_id}", response_model=schemas.LogResponse)
def read_log(log_id: int, db: Session = Depends(get_db)):
    db_log = crud.get_log_by_id(db, log_id)
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return db_log

@router.put("/{log_id}", response_model=schemas.LogResponse)
def update_log_entry(log_id: int, log: schemas.LogCreate, db: Session = Depends(get_db)):
    updated_log = crud.update_log(db, log_id, log)
    if not updated_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return updated_log

@router.delete("/{log_id}")
def delete_log_entry(log_id: int, db: Session = Depends(get_db)):
    success = crud.delete_log(db, log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"code":0,"message": f"Log {log_id} deleted successfully!"}

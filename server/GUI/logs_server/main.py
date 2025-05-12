# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/05/12 23:25 
@Describe:
'''
from fastapi import FastAPI
from .db.database import engine
from .models.log import Log
from .api.log_routes import router as logs_router

Log.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(logs_router)
# 跨域
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"message": "Logging System API"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8005)

"""
测试示例

# 创建日志
curl -X POST "http://localhost:8005/logs/" \
-H "Content-Type: application/json" \
-d '{"operator_module": "客流分析", "operator_type": "RTSP流检测","person_name":"admin","describes":"检测无误"}'

# 查询所有日志
curl "http://localhost:8000/logs/"

# 更新日志
curl -X PUT "http://localhost:8000/logs/1" \
-H "Content-Type: application/json" \
-d '{"level": "WARNING", "message": "Connection timeout"}'

# 删除日志
curl -X DELETE "http://localhost:8000/logs/1"
"""
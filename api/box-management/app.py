# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/13 1:53 
@Describe:
'''
# -*- coding: UTF-8 -*-
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, AnyUrl
from contextlib import asynccontextmanager
from typing import Optional, List, AsyncGenerator
import asyncpg
import os

# 配置管理
class Settings(BaseModel):
    database_url: AnyUrl = os.getenv("DATABASE_URL", "postgresql://postgres:Sztu%40love@47.96.253.87:5434/fd")
    pool_min_size: int = int(os.getenv("DB_POOL_MIN", "5"))
    pool_max_size: int = int(os.getenv("DB_POOL_MAX", "20"))
    pool_timeout: int = int(os.getenv("DB_TIMEOUT", "60"))

settings = Settings()

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # 初始化连接池
    app.state.db_pool = await asyncpg.create_pool(
        dsn=str(settings.database_url),
        min_size=settings.pool_min_size,
        max_size=settings.pool_max_size,
        command_timeout=settings.pool_timeout
    )
    yield
    # 关闭连接池
    if app.state.db_pool:
        await app.state.db_pool.close()

app = FastAPI(lifespan=lifespan)

# 依赖注入
async def get_db_pool() -> asyncpg.Pool:
    if not app.state.db_pool:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection pool not initialized"
        )
    return app.state.db_pool

# Pydantic 模型
class AIBoxCreate(BaseModel):
    ip: str
    mask: str
    gateway: str
    upload_data: Optional[str] = None
    target_server: Optional[str] = None
    power_time: Optional[datetime] = None
    shutdown_time: Optional[datetime] = None
    describe: Optional[str] = None
    img: Optional[str] = None

class AIBox(AIBoxCreate):
    id: int

# 核心 CRUD 操作
async def create_box(pool: asyncpg.Pool, box: AIBoxCreate) -> AIBox:
    async with pool.acquire() as conn:
        query = """
            INSERT INTO ai_boxs (
                ip, mask, gateway, upload_data,
                target_server, power_time,
                shutdown_time, describe, img
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING *
        """
        try:
            record = await conn.fetchrow(
                query,
                box.ip, box.mask, box.gateway,
                box.upload_data, box.target_server,
                box.power_time, box.shutdown_time,
                box.describe, box.img
            )
            return AIBox(**record)
        except asyncpg.PostgresError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Create failed: {e}"
            )

async def get_box(pool: asyncpg.Pool, box_id: int) -> Optional[AIBox]:
    async with pool.acquire() as conn:
        try:
            record = await conn.fetchrow(
                "SELECT * FROM ai_boxs WHERE id = $1",
                box_id
            )
            return AIBox(**record) if record else None
        except asyncpg.PostgresError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Query failed: {e}"
            )

async def get_all_boxes(pool: asyncpg.Pool) -> List[AIBox]:
    async with pool.acquire() as conn:
        try:
            records = await conn.fetch("SELECT * FROM ai_boxs ORDER BY id DESC")
            return [AIBox(**record) for record in records]
        except asyncpg.PostgresError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Query failed: {e}"
            )

async def update_box(pool: asyncpg.Pool, box_id: int, box: AIBoxCreate) -> AIBox:
    async with pool.acquire() as conn:
        query = """
            UPDATE ai_boxs SET
                ip = $1, mask = $2, gateway = $3,
                upload_data = $4, target_server = $5,
                power_time = $6, shutdown_time = $7,
                describe = $8, img = $9
            WHERE id = $10
            RETURNING *
        """
        try:
            record = await conn.fetchrow(
                query,
                box.ip, box.mask, box.gateway,
                box.upload_data, box.target_server,
                box.power_time, box.shutdown_time,
                box.describe, box.img, box_id
            )
            if not record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Box not found"
                )
            return AIBox(**record)
        except asyncpg.PostgresError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Update failed: {e}"
            )

async def delete_box(pool: asyncpg.Pool, box_id: int) -> bool:
    async with pool.acquire() as conn:
        try:
            result = await conn.execute(
                "DELETE FROM ai_boxs WHERE id = $1",
                box_id
            )
            return "DELETE 1" in result
        except asyncpg.PostgresError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Delete failed: {e}"
            )

# 路由端点
@app.post("/boxes", response_model=AIBox, status_code=status.HTTP_201_CREATED)
async def create_box_endpoint(
    box: AIBoxCreate,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    return await create_box(pool, box)

@app.get("/boxes/{box_id}", response_model=AIBox)
async def read_box(
    box_id: int,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    box = await get_box(pool, box_id)
    if not box:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Box not found"
        )
    return box

@app.get("/boxes", response_model=List[AIBox])
async def read_all_boxes(pool: asyncpg.Pool = Depends(get_db_pool)):
    return await get_all_boxes(pool)

@app.put("/boxes/{box_id}", response_model=AIBox)
async def update_box_endpoint(
    box_id: int,
    box: AIBoxCreate,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    return await update_box(pool, box_id, box)

@app.delete("/boxes/{box_id}")
async def delete_box_endpoint(
    box_id: int,
    pool: asyncpg.Pool = Depends(get_db_pool)
):

    success = await delete_box(pool, box_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Box not found"
        )
    return {"status": "deleted"}

@app.get("/health")
async def health_check(pool: asyncpg.Pool = Depends(get_db_pool)):
    try:
        async with pool.acquire() as conn:
            await conn.fetch("SELECT 1")
            return {"status": "ok"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {e}"
        )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8007)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8007)
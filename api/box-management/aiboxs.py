from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncpg
from contextlib import asynccontextmanager

# 异步连接池 (全局共享)
DB_URL = "postgresql://postgres:Sztu@love@47.96.253.87:5434/fd"
db_pool = None

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    db_pool = await asyncpg.create_pool(
        dsn=DB_URL,
        min_size=5,
        max_size=20,
        command_timeout=60
    )

    yield
    await db_pool.close()

app = FastAPI(lifespan=lifespan)

# Pydantic 模型
class AIBoxCreate(BaseModel):
    ip: str
    mask: str
    gateway: str
    upload_data: Optional[str] = None
    target_server: Optional[str] = None
    power_time: Optional[str] = None
    shutdown_time: Optional[str] = None
    describe: Optional[str] = None
    img: Optional[str] = None

class AIBox(AIBoxCreate):
    id: int

# 数据库行转换模型
class RowModel:
    @classmethod
    def from_record(cls, record):
        return cls(**dict(record))

# 核心 CRUD 操作
async def create_box(box: AIBoxCreate) -> AIBox:
    async with db_pool.acquire() as conn:
        query = """
            INSERT INTO ai_boxs (
                ip, mask, gateway, upload_data, 
                target_server, power_time, 
                shutdown_time, describe, img
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING *
        """
        record = await conn.fetchrow(
            query,
            box.ip, box.mask, box.gateway,
            box.upload_data, box.target_server,
            box.power_time, box.shutdown_time,
            box.describe, box.img
        )
        return AIBox(**dict(record))

async def get_box(box_id: int) -> Optional[AIBox]:
    async with db_pool.acquire() as conn:
        record = await conn.fetchrow(
            "SELECT * FROM ai_boxs WHERE id = $1",
            box_id
        )
        return AIBox(**dict(record)) if record else None

async def get_all_boxes() -> List[AIBox]:
    async with db_pool.acquire() as conn:
        records = await conn.fetch("SELECT * FROM ai_boxs")
        return [AIBox(**dict(r)) for r in records]

async def update_box(box_id: int, box: AIBoxCreate) -> AIBox:
    async with db_pool.acquire() as conn:
        query = """
            UPDATE ai_boxs SET
                ip = $1, mask = $2, gateway = $3,
                upload_data = $4, target_server = $5,
                power_time = $6, shutdown_time = $7,
                describe = $8, img = $9
            WHERE id = $10
            RETURNING *
        """
        record = await conn.fetchrow(
            query,
            box.ip, box.mask, box.gateway,
            box.upload_data, box.target_server,
            box.power_time, box.shutdown_time,
            box.describe, box.img, box_id
        )
        if not record:
            raise HTTPException(404, "Box not found")
        return AIBox(**dict(record))

async def delete_box(box_id: int) -> bool:
    async with db_pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM ai_boxs WHERE id = $1",
            box_id
        )
        return "DELETE 1" in result

# 路由端点
@app.post("/boxes/", response_model=AIBox)
async def create_box_endpoint(box: AIBoxCreate):
    return await create_box(box)

@app.get("/boxes/{box_id}", response_model=AIBox)
async def read_box(box_id: int):
    if box := await get_box(box_id):
        return box
    raise HTTPException(404, "Box not found")

@app.get("/boxes/", response_model=List[AIBox])
async def read_all_boxes():
    return await get_all_boxes()

@app.put("/boxes/{box_id}", response_model=AIBox)
async def update_box_endpoint(box_id: int, box: AIBoxCreate):
    return await update_box(box_id, box)

@app.delete("/boxes/{box_id}")
async def delete_box_endpoint(box_id: int):
    success = await delete_box(box_id)
    return {"status": "deleted"} if success else {"status": "failed"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8007)
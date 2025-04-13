from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Customer Flow Analysis API")

# --- CORS Configuration --- Allow requests from your frontend
origins = [
    "http://localhost:3000",  # Assuming your Next.js frontend runs here
    "http://127.0.0.1:3000",
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- Pydantic Models (based on store/types.ts) ---

class Point(BaseModel):
    x: float
    y: float

class GetFrameRequest(BaseModel):
    url: str

class GetFrameResponse(BaseModel):
    frameDataUrl: str
    width: int
    height: int

class StartAnalysisRequest(BaseModel):
    rtsp_address: str
    polygon_points: List[Point]
    crossing_lines: List[List[Point]] # List of lines, each line is [startPoint, endPoint]
    zone_type: Literal['inside', 'outside']

class StartAnalysisResponse(BaseModel):
    mjpegStreamUrl: str

# --- API Endpoints ---

@app.post("/get-frame", response_model=GetFrameResponse)
async def get_frame(request: GetFrameRequest):
    """Simulates fetching the first frame from an RTSP stream."""
    logger.info(f"Received /get-frame request for URL: {request.url}")
    # Simulate processing and return fixed data (like the Next.js API)
    await asyncio.sleep(0.5) # Simulate short delay
    response_data = GetFrameResponse(
        frameDataUrl="/images/placeholder-image.jpg", # Fixed placeholder image
        width=1920,
        height=1080,
    )
    return response_data

@app.post("/start-analysis", response_model=StartAnalysisResponse)
async def start_analysis(request: StartAnalysisRequest):
    """Simulates starting the analysis process on the backend."""
    logger.info(f"Received /start-analysis request for: {request.rtsp_address}")
    logger.info(f"  Zone Type: {request.zone_type}")
    logger.info(f"  Polygon Points Count: {len(request.polygon_points)}")
    logger.info(f"  Crossing Lines Count: {len(request.crossing_lines)}")

    # Simulate backend processing time (like the Next.js API)
    await asyncio.sleep(1.5)

    # Return the fixed MJPEG stream URL
    response_data = StartAnalysisResponse(
        mjpegStreamUrl="http://47.97.71.139:8003/video_feed", # Fixed stream URL
    )
    return response_data

@app.get("/")
async def read_root():
    return {"message": "Customer Flow Analysis API is running."}

# To run this app: uvicorn main:app --reload --port 8000 
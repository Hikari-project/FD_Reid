# Customer Flow Analysis - FastAPI Backend

This directory contains the Python FastAPI backend for the customer flow analysis application.

## Setup

1.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

1.  **Start the development server:**
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    *   `--reload`: Automatically restarts the server when code changes are detected.
    *   `--host 0.0.0.0`: Makes the server accessible on your local network.
    *   `--port 8000`: Specifies the port to run on.

2.  **Access the API:**
    *   The API will be running at `http://localhost:8000` or `http://<your-ip-address>:8000`.
    *   Interactive documentation (Swagger UI) is available at `http://localhost:8000/docs`.
    *   Alternative documentation (ReDoc) is available at `http://localhost:8000/redoc`.

## Endpoints

*   `POST /get-frame`: Accepts `{"url": "<rtsp_url>"}` and returns simulated frame data.
*   `POST /start-analysis`: Accepts analysis parameters (`rtsp_address`, `polygon_points`, `crossing_lines`, `zone_type`) and returns a simulated MJPEG stream URL. 
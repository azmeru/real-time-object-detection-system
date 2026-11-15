# Real-Time Object Detection System

YOLOv8 object detection with three inference backends (PyTorch/CUDA, ONNX Runtime, OpenVINO), a FastAPI backend, PostgreSQL history, and a React dashboard.

## Features
- Image upload and live webcam detection
- Switch between PyTorch, ONNX Runtime and OpenVINO
- Benchmark page comparing latency across backends
- Detection history with pagination and statistics

## Quick start (Docker)
```bash
docker compose up --build            # CPU: UI on :3000, API on :8000
docker compose --profile gpu up --build backend-gpu db   # NVIDIA GPU: API on :8001
```
Open http://localhost:3000. API docs: http://localhost:8000/docs.

Set `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` in a `.env` file next to `docker-compose.yml` to override the defaults.

ONNX and OpenVINO need an exported model. Call `POST /api/v1/models/export` once (it runs in the background). The file is written to `backend/models/yolov8n.onnx`. Until then those endpoints return 503.

## Local development
Backend (Python 3.11):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # set DATABASE_URL
uvicorn app.main:app --reload
pytest
```
Frontend (Node 20+):
```bash
cd frontend
npm install
npm run dev      # http://localhost:5173, proxies /api to :8000
npm run build
```

## Configuration
See `backend/.env.example`. Notable settings: `YOLO_MODEL`, `YOLO_CONFIDENCE_THRESHOLD`, `YOLO_IOU_THRESHOLD`, `ONNX_MODEL_PATH`, `OPENVINO_DEVICE`, `MAX_UPLOAD_MB`, `CORS_ORIGINS`.

## API
| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/detect/` | Detect with PyTorch |
| POST | `/api/v1/detect/onnx` | Detect with ONNX Runtime |
| POST | `/api/v1/detect/openvino` | Detect with OpenVINO |
| GET | `/api/v1/detections/` | Paginated history |
| GET | `/api/v1/detections/stats` | Aggregate statistics |
| GET | `/api/v1/benchmark/` | Run the backend benchmark |
| POST | `/api/v1/models/export` | Export YOLOv8 to ONNX |
| GET | `/api/v1/system/health` | Health check |
| GET | `/api/v1/system/device` | Inference device info |

See `DEPLOYMENT.md` for AWS deployment.

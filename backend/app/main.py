from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import (
    ModelNotLoadedError, UnsupportedFileTypeError, InferenceError, DetectionNotFoundError,
    model_not_loaded_handler, unsupported_file_handler, inference_error_handler, detection_not_found_handler,
)
from app.core.logging import setup_logging, get_logger
from app.database import init_db

settings = get_settings()
setup_logging(debug=settings.debug)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initializing database and loading models...")
    await init_db()

    from app.services.yolo_service import YOLOService
    from app.services.onnx_service import ONNXService
    from app.services.openvino_service import OpenVINOService

    YOLOService.get_instance().load()
    ONNXService.get_instance().load()
    OpenVINOService.get_instance().load()

    logger.info("All services ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Real-Time Object Detection Platform — YOLOv8 · CUDA · ONNX · OpenVINO",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ModelNotLoadedError, model_not_loaded_handler)
app.add_exception_handler(UnsupportedFileTypeError, unsupported_file_handler)
app.add_exception_handler(InferenceError, inference_error_handler)
app.add_exception_handler(DetectionNotFoundError, detection_not_found_handler)

app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():
    return {"message": f"Welcome to {settings.app_name} v{settings.app_version}"}

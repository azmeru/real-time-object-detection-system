from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.database import get_db_session
from app.repositories.detection_repository import DetectionRepository
from app.services.yolo_service import YOLOService
from app.services.onnx_service import ONNXService
from app.services.openvino_service import OpenVINOService
from app.services.benchmark_service import BenchmarkService


def get_detection_repository(db: AsyncSession = Depends(get_db_session)) -> DetectionRepository:
    return DetectionRepository(db)


def get_yolo_service(settings: Settings = Depends(get_settings)) -> YOLOService:
    return YOLOService.get_instance()


def get_onnx_service(settings: Settings = Depends(get_settings)) -> ONNXService:
    return ONNXService.get_instance()


def get_openvino_service(settings: Settings = Depends(get_settings)) -> OpenVINOService:
    return OpenVINOService.get_instance()


def get_benchmark_service(
    yolo_service: YOLOService = Depends(get_yolo_service),
    onnx_service: ONNXService = Depends(get_onnx_service),
    openvino_service: OpenVINOService = Depends(get_openvino_service),
) -> BenchmarkService:
    return BenchmarkService(yolo_service, onnx_service, openvino_service)

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Real-Time Object Detection Platform"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/detection_db"

    # YOLO
    yolo_model: str = "yolov8n.pt"
    yolo_confidence_threshold: float = 0.25
    yolo_iou_threshold: float = 0.45

    # ONNX
    onnx_model_path: str = "models/yolov8n.onnx"

    # OpenVINO
    openvino_model_path: str = "models/yolov8n_openvino_model"
    openvino_device: str = "CPU"

    # Uploads / CORS
    max_upload_mb: int = 10
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

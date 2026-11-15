from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class DetectionResult(BaseModel):
    detected_class: str = Field(alias="class")
    confidence: float
    bbox: List[float]

    model_config = {"populate_by_name": True}


class DetectionResponse(BaseModel):
    filename: str
    detections: List[DetectionResult]
    inference_device: str
    inference_latency_ms: float
    annotated_image_base64: Optional[str] = None


class DetectionRecord(BaseModel):
    id: int
    filename: str
    detected_class: str
    confidence: float
    bbox_x1: float
    bbox_y1: float
    bbox_x2: float
    bbox_y2: float
    inference_device: str
    inference_latency_ms: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedDetections(BaseModel):
    items: List[DetectionRecord]
    total: int
    page: int
    page_size: int
    total_pages: int

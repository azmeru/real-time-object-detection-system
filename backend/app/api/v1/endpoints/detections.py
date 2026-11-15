from fastapi import APIRouter, Depends, Query

from app.core.config import get_settings, Settings
from app.core.dependencies import get_detection_repository
from app.repositories.detection_repository import DetectionRepository
from app.schemas.detection import PaginatedDetections

router = APIRouter(prefix="/detections", tags=["History"])


@router.get("/", response_model=PaginatedDetections, summary="Get paginated detection history")
async def list_detections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    repo: DetectionRepository = Depends(get_detection_repository),
    settings: Settings = Depends(get_settings),
):
    return await repo.get_all_paginated(page=page, page_size=page_size)


@router.get("/stats", summary="Detection statistics")
async def detection_stats(repo: DetectionRepository = Depends(get_detection_repository)):
    return await repo.get_stats()

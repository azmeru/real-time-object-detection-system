from fastapi import APIRouter

from app.api.v1.endpoints import detect, system, detections, benchmark, models

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(system.router)
api_router.include_router(detect.router)
api_router.include_router(detections.router)
api_router.include_router(benchmark.router)
api_router.include_router(models.router)

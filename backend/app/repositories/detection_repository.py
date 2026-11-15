import math
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.detection import Detection
from app.schemas.detection import DetectionRecord, PaginatedDetections


class DetectionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def save(self, detection: Detection) -> Detection:
        self._db.add(detection)
        await self._db.flush()
        await self._db.refresh(detection)
        return detection

    async def get_all_paginated(self, page: int, page_size: int) -> PaginatedDetections:
        offset = (page - 1) * page_size

        count_result = await self._db.execute(select(func.count()).select_from(Detection))
        total = count_result.scalar_one()

        result = await self._db.execute(
            select(Detection).order_by(Detection.created_at.desc()).offset(offset).limit(page_size)
        )
        items = result.scalars().all()

        return PaginatedDetections(
            items=[DetectionRecord.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 1,
        )

    async def get_stats(self) -> dict:
        total_result = await self._db.execute(select(func.count()).select_from(Detection))
        total = total_result.scalar_one()

        avg_conf_result = await self._db.execute(select(func.avg(Detection.confidence)))
        avg_confidence = avg_conf_result.scalar_one() or 0.0

        top_classes_result = await self._db.execute(
            select(Detection.detected_class, func.count(Detection.detected_class).label("count"))
            .group_by(Detection.detected_class)
            .order_by(func.count(Detection.detected_class).desc())
            .limit(5)
        )
        top_classes = [{"class": row[0], "count": row[1]} for row in top_classes_result.all()]

        return {
            "total_detections": total,
            "average_confidence": round(avg_confidence, 4),
            "top_classes": top_classes,
        }

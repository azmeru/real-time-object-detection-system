import base64
import io
import time
from typing import List, Optional

import numpy as np
from PIL import Image

from app.core.config import get_settings
from app.core.exceptions import ModelNotLoadedError, InferenceError
from app.core.logging import get_logger
from app.schemas.detection import DetectionResult, DetectionResponse

logger = get_logger(__name__)
settings = get_settings()


class YOLOService:
    _instance: Optional["YOLOService"] = None

    def __init__(self) -> None:
        self._model = None
        self._device: Optional[str] = None

    @classmethod
    def get_instance(cls) -> "YOLOService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self) -> None:
        try:
            import torch
            from ultralytics import YOLO

            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading YOLOv8 model on device: {self._device}")
            self._model = YOLO(settings.yolo_model)
            self._model.to(self._device)
            logger.info("YOLOv8 model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def device(self) -> Optional[str]:
        return self._device

    def detect(self, image: Image.Image, filename: str = "image.jpg") -> DetectionResponse:
        if not self.is_loaded:
            raise ModelNotLoadedError()

        try:
            start = time.perf_counter()
            results = self._model.predict(
                image,
                conf=settings.yolo_confidence_threshold,
                iou=settings.yolo_iou_threshold,
                device=self._device,
                verbose=False,
            )
            latency_ms = (time.perf_counter() - start) * 1000

            detections: List[DetectionResult] = []
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    cls_name = result.names[cls_id]
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
                    detections.append(
                        DetectionResult(**{"class": cls_name, "confidence": conf, "bbox": [x1, y1, x2, y2]})
                    )

            annotated = results[0].plot() if results else np.array(image)
            annotated_b64 = self._encode_image(annotated)

            return DetectionResponse(
                filename=filename,
                detections=detections,
                inference_device=self._device or "cpu",
                inference_latency_ms=round(latency_ms, 2),
                annotated_image_base64=annotated_b64,
            )
        except Exception as e:
            raise InferenceError(str(e)) from e

    def _encode_image(self, arr: np.ndarray) -> str:
        img = Image.fromarray(arr[..., ::-1])
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

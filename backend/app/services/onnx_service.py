import base64
import io
import time
from pathlib import Path
from typing import List, Optional

import numpy as np
from PIL import Image

from app.core.config import get_settings
from app.core.exceptions import ModelNotLoadedError, InferenceError
from app.core.logging import get_logger
from app.schemas.detection import DetectionResponse
from app.services.postprocess import decode_yolov8

logger = get_logger(__name__)
settings = get_settings()



class ONNXService:
    _instance: Optional["ONNXService"] = None

    def __init__(self) -> None:
        self._session = None
        self._input_name: Optional[str] = None

    @classmethod
    def get_instance(cls) -> "ONNXService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self) -> None:
        model_path = Path(settings.onnx_model_path)
        if not model_path.exists():
            logger.warning(f"ONNX model not found at {model_path}. Export it first via /models/export.")
            return
        try:
            import onnxruntime as ort

            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            self._session = ort.InferenceSession(str(model_path), providers=providers)
            self._input_name = self._session.get_inputs()[0].name
            logger.info(f"ONNX model loaded. Active provider: {self._session.get_providers()}")
        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")

    @property
    def is_loaded(self) -> bool:
        return self._session is not None

    def detect(self, image: Image.Image, filename: str = "image.jpg") -> DetectionResponse:
        if not self.is_loaded:
            raise ModelNotLoadedError()

        try:
            input_tensor = self._preprocess(image)
            start = time.perf_counter()
            outputs = self._session.run(None, {self._input_name: input_tensor})
            latency_ms = (time.perf_counter() - start) * 1000

            detections = decode_yolov8(outputs[0], image.size, settings.yolo_confidence_threshold, settings.yolo_iou_threshold)

            return DetectionResponse(
                filename=filename,
                detections=detections,
                inference_device="onnx",
                inference_latency_ms=round(latency_ms, 2),
            )
        except Exception as e:
            raise InferenceError(str(e)) from e

    def _preprocess(self, image: Image.Image, size: int = 640) -> np.ndarray:
        img = image.convert("RGB").resize((size, size))
        arr = np.array(img, dtype=np.float32) / 255.0
        arr = arr.transpose(2, 0, 1)[np.newaxis, ...]
        return arr

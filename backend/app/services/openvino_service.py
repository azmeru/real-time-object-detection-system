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


class OpenVINOService:
    _instance: Optional["OpenVINOService"] = None

    def __init__(self) -> None:
        self._compiled_model = None
        self._output_layer = None

    @classmethod
    def get_instance(cls) -> "OpenVINOService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self) -> None:
        model_path = Path(settings.onnx_model_path)
        if not model_path.exists():
            logger.warning("ONNX model not found. Export it first before loading OpenVINO.")
            return
        try:
            from openvino.runtime import Core

            ie = Core()
            model = ie.read_model(str(model_path))
            self._compiled_model = ie.compile_model(model, settings.openvino_device)
            self._output_layer = self._compiled_model.output(0)
            logger.info(f"OpenVINO model compiled on device: {settings.openvino_device}")
        except ImportError:
            logger.warning("OpenVINO not installed. Skipping.")
        except Exception as e:
            logger.error(f"Failed to load OpenVINO model: {e}")

    @property
    def is_loaded(self) -> bool:
        return self._compiled_model is not None

    def detect(self, image: Image.Image, filename: str = "image.jpg") -> DetectionResponse:
        if not self.is_loaded:
            raise ModelNotLoadedError()

        try:
            input_tensor = self._preprocess(image)
            start = time.perf_counter()
            outputs = self._compiled_model({0: input_tensor})
            latency_ms = (time.perf_counter() - start) * 1000

            raw = outputs[self._output_layer]
            detections = decode_yolov8(raw, image.size, settings.yolo_confidence_threshold, settings.yolo_iou_threshold)

            return DetectionResponse(
                filename=filename,
                detections=detections,
                inference_device=f"openvino:{settings.openvino_device}",
                inference_latency_ms=round(latency_ms, 2),
            )
        except Exception as e:
            raise InferenceError(str(e)) from e

    def _preprocess(self, image: Image.Image, size: int = 640) -> np.ndarray:
        img = image.convert("RGB").resize((size, size))
        arr = np.array(img, dtype=np.float32) / 255.0
        return arr.transpose(2, 0, 1)[np.newaxis, ...]

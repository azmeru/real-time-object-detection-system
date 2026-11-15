import time
from typing import Optional

import numpy as np
from PIL import Image

from app.core.logging import get_logger
from app.schemas.benchmark import BenchmarkResult

logger = get_logger(__name__)


def _synthetic_image(width: int = 640, height: int = 640) -> Image.Image:
    arr = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    return Image.fromarray(arr)


def _measure_latency(fn, image: Image.Image, iterations: int) -> tuple[float, float]:
    latencies = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn(image)
        latencies.append((time.perf_counter() - start) * 1000)
    avg_latency = float(np.mean(latencies))
    fps = 1000.0 / avg_latency if avg_latency > 0 else 0.0
    return round(avg_latency, 2), round(fps, 2)


class BenchmarkService:
    def __init__(self, yolo_service, onnx_service, openvino_service) -> None:
        self._yolo = yolo_service
        self._onnx = onnx_service
        self._openvino = openvino_service

    def run(self, iterations: int = 10) -> BenchmarkResult:
        image = _synthetic_image()

        import torch

        cpu_latency, cpu_fps = self._bench_cpu(image, iterations)
        gpu_latency, gpu_fps = self._bench_gpu(image, iterations, torch.cuda.is_available())
        onnx_latency, onnx_fps = self._bench_onnx(image, iterations)
        openvino_latency, openvino_fps = self._bench_openvino(image, iterations)

        gpu_speedup = round(cpu_latency / gpu_latency, 2) if gpu_latency else None
        onnx_speedup = round(cpu_latency / onnx_latency, 2) if onnx_latency else None
        openvino_speedup = round(cpu_latency / openvino_latency, 2) if openvino_latency else None

        return BenchmarkResult(
            cpu_latency_ms=cpu_latency,
            cpu_fps=cpu_fps,
            gpu_latency_ms=gpu_latency,
            gpu_fps=gpu_fps,
            onnx_latency_ms=onnx_latency,
            onnx_fps=onnx_fps,
            openvino_latency_ms=openvino_latency,
            openvino_fps=openvino_fps,
            gpu_speedup=gpu_speedup,
            onnx_speedup=onnx_speedup,
            openvino_speedup=openvino_speedup,
            num_iterations=iterations,
        )

    def _bench_cpu(self, image: Image.Image, iterations: int) -> tuple[float, float]:
        if not self._yolo.is_loaded:
            return 0.0, 0.0
        original_device = self._yolo.device
        try:
            self._yolo._model.to("cpu")
            self._yolo._device = "cpu"
            return _measure_latency(lambda img: self._yolo.detect(img), image, iterations)
        finally:
            self._yolo._model.to(original_device)
            self._yolo._device = original_device

    def _bench_gpu(self, image: Image.Image, iterations: int, cuda_available: bool) -> tuple[Optional[float], Optional[float]]:
        if not cuda_available or not self._yolo.is_loaded:
            return None, None
        original_device = self._yolo.device
        try:
            self._yolo._model.to("cuda")
            self._yolo._device = "cuda"
            return _measure_latency(lambda img: self._yolo.detect(img), image, iterations)
        finally:
            self._yolo._model.to(original_device)
            self._yolo._device = original_device

    def _bench_onnx(self, image: Image.Image, iterations: int) -> tuple[Optional[float], Optional[float]]:
        if not self._onnx.is_loaded:
            return None, None
        return _measure_latency(lambda img: self._onnx.detect(img), image, iterations)

    def _bench_openvino(self, image: Image.Image, iterations: int) -> tuple[Optional[float], Optional[float]]:
        if not self._openvino.is_loaded:
            return None, None
        return _measure_latency(lambda img: self._openvino.detect(img), image, iterations)

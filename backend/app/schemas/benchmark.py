from typing import Optional
from pydantic import BaseModel


class BenchmarkResult(BaseModel):
    cpu_latency_ms: float
    cpu_fps: float
    gpu_latency_ms: Optional[float] = None
    gpu_fps: Optional[float] = None
    onnx_latency_ms: Optional[float] = None
    onnx_fps: Optional[float] = None
    openvino_latency_ms: Optional[float] = None
    openvino_fps: Optional[float] = None
    gpu_speedup: Optional[float] = None
    onnx_speedup: Optional[float] = None
    openvino_speedup: Optional[float] = None
    num_iterations: int = 10


class DeviceInfo(BaseModel):
    device: str
    gpu_name: Optional[str] = None
    cuda_available: bool
    cuda_version: Optional[str] = None
    openvino_available: bool

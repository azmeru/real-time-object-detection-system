from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_benchmark_service
from app.schemas.benchmark import BenchmarkResult
from app.services.benchmark_service import BenchmarkService

router = APIRouter(prefix="/benchmark", tags=["Benchmark"])


@router.get("/", response_model=BenchmarkResult, summary="Run CPU vs GPU vs ONNX vs OpenVINO benchmark")
async def run_benchmark(
    iterations: int = Query(10, ge=1, le=100, description="Number of inference iterations per backend"),
    benchmark: BenchmarkService = Depends(get_benchmark_service),
):
    return benchmark.run(iterations=iterations)

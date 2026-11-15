from fastapi import APIRouter

from app.schemas.benchmark import DeviceInfo

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health", summary="Health check")
async def health():
    return {"status": "ok"}


@router.get("/device", response_model=DeviceInfo, summary="Current inference device info")
async def device_info():
    import torch

    cuda_available = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if cuda_available else None
    cuda_version = torch.version.cuda if cuda_available else None

    try:
        from openvino.runtime import Core
        ie = Core()
        _ = ie.available_devices
        openvino_available = True
    except Exception:
        openvino_available = False

    return DeviceInfo(
        device="cuda" if cuda_available else "cpu",
        gpu_name=gpu_name,
        cuda_available=cuda_available,
        cuda_version=cuda_version,
        openvino_available=openvino_available,
    )

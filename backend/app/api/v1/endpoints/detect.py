from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from PIL import Image
import io

from app.core.config import get_settings
from app.core.dependencies import get_yolo_service, get_onnx_service, get_openvino_service, get_detection_repository
from app.core.exceptions import ModelNotLoadedError, UnsupportedFileTypeError, InferenceError
from app.models.detection import Detection
from app.schemas.detection import DetectionResponse
from app.services.yolo_service import YOLOService
from app.services.onnx_service import ONNXService
from app.services.openvino_service import OpenVINOService
from app.repositories.detection_repository import DetectionRepository

router = APIRouter(prefix="/detect", tags=["Detection"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}


async def _load_image(file: UploadFile) -> Image.Image:
    if file.content_type not in ALLOWED_TYPES:
        raise UnsupportedFileTypeError(f"Unsupported file type: {file.content_type}. Allowed: {ALLOWED_TYPES}")
    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise UnsupportedFileTypeError(f"File too large. Maximum size is {get_settings().max_upload_mb} MB.")
    try:
        return Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:
        raise UnsupportedFileTypeError("Could not decode the uploaded image.") from e


async def _persist(response: DetectionResponse, repo: DetectionRepository) -> None:
    for det in response.detections:
        record = Detection(
            filename=response.filename,
            detected_class=det.detected_class,
            confidence=det.confidence,
            bbox_x1=det.bbox[0],
            bbox_y1=det.bbox[1],
            bbox_x2=det.bbox[2],
            bbox_y2=det.bbox[3],
            inference_device=response.inference_device,
            inference_latency_ms=response.inference_latency_ms,
        )
        await repo.save(record)


@router.post("/", response_model=DetectionResponse, summary="Detect objects with YOLOv8 (PyTorch)")
async def detect(
    file: UploadFile = File(...),
    yolo: YOLOService = Depends(get_yolo_service),
    repo: DetectionRepository = Depends(get_detection_repository),
):
    image = await _load_image(file)
    response = yolo.detect(image, filename=file.filename or "upload.jpg")
    await _persist(response, repo)
    return response


@router.post("/onnx", response_model=DetectionResponse, summary="Detect objects with ONNX Runtime")
async def detect_onnx(
    file: UploadFile = File(...),
    onnx: ONNXService = Depends(get_onnx_service),
    repo: DetectionRepository = Depends(get_detection_repository),
):
    image = await _load_image(file)
    response = onnx.detect(image, filename=file.filename or "upload.jpg")
    await _persist(response, repo)
    return response


@router.post("/openvino", response_model=DetectionResponse, summary="Detect objects with OpenVINO")
async def detect_openvino(
    file: UploadFile = File(...),
    openvino: OpenVINOService = Depends(get_openvino_service),
    repo: DetectionRepository = Depends(get_detection_repository),
):
    image = await _load_image(file)
    response = openvino.detect(image, filename=file.filename or "upload.jpg")
    await _persist(response, repo)
    return response

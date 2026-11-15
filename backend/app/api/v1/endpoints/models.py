from fastapi import APIRouter, BackgroundTasks

from app.services.model_export_service import export_to_onnx
from app.services.onnx_service import ONNXService
from app.services.openvino_service import OpenVINOService

router = APIRouter(prefix="/models", tags=["Models"])


@router.post("/export", summary="Export YOLOv8 to ONNX and reload inference services")
async def export_model(background_tasks: BackgroundTasks):
    def _export_and_reload():
        export_to_onnx()
        ONNXService.get_instance().load()
        OpenVINOService.get_instance().load()

    background_tasks.add_task(_export_and_reload)
    return {"message": "Export started in background. ONNX and OpenVINO services will reload when done."}

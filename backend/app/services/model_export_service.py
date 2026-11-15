import shutil
from pathlib import Path

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


def export_to_onnx() -> str:
    from ultralytics import YOLO

    model = YOLO(settings.yolo_model)
    output_path = Path(settings.onnx_model_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Ultralytics writes the .onnx next to the source weights; move it to the configured path.
    exported = Path(model.export(format="onnx", imgsz=640, opset=17, simplify=True))
    if exported.resolve() != output_path.resolve():
        shutil.move(str(exported), str(output_path))
    logger.info(f"ONNX model exported to: {output_path}")
    return str(output_path)

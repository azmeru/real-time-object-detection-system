#!/usr/bin/env python3
"""Export YOLOv8 model to ONNX format."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


def main():
    parser = argparse.ArgumentParser(description="Export YOLOv8 to ONNX")
    parser.add_argument("--model", default="yolov8n.pt", help="YOLO model name or path")
    parser.add_argument("--output", default="backend/models/yolov8n.onnx", help="Output ONNX path")
    parser.add_argument("--imgsz", type=int, default=640)
    args = parser.parse_args()

    from ultralytics import YOLO

    print(f"Loading model: {args.model}")
    model = YOLO(args.model)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("Exporting to ONNX...")
    exported = model.export(format="onnx", imgsz=args.imgsz, opset=17, simplify=True)
    print(f"Exported: {exported}")


if __name__ == "__main__":
    main()

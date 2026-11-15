from typing import List

import numpy as np

from app.schemas.detection import DetectionResult

COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
    "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush",
]


def nms(boxes: np.ndarray, scores: np.ndarray, iou_thresh: float) -> List[int]:
    """Greedy non-maximum suppression. boxes are (N, 4) as x1, y1, x2, y2."""
    order = scores.argsort()[::-1]
    keep: List[int] = []
    while order.size > 0:
        i = int(order[0])
        keep.append(i)
        if order.size == 1:
            break
        rest = order[1:]
        xx1 = np.maximum(boxes[i, 0], boxes[rest, 0])
        yy1 = np.maximum(boxes[i, 1], boxes[rest, 1])
        xx2 = np.minimum(boxes[i, 2], boxes[rest, 2])
        yy2 = np.minimum(boxes[i, 3], boxes[rest, 3])
        inter = np.maximum(0.0, xx2 - xx1) * np.maximum(0.0, yy2 - yy1)
        area_i = (boxes[i, 2] - boxes[i, 0]) * (boxes[i, 3] - boxes[i, 1])
        area_r = (boxes[rest, 2] - boxes[rest, 0]) * (boxes[rest, 3] - boxes[rest, 1])
        iou = inter / np.maximum(area_i + area_r - inter, 1e-9)
        order = rest[iou <= iou_thresh]
    return keep


def decode_yolov8(
    output: np.ndarray,
    orig_size: tuple,
    conf_thresh: float,
    iou_thresh: float,
    input_size: int = 640,
) -> List[DetectionResult]:
    """Decode a YOLOv8 head output of shape (1, 4+C, N) or (4+C, N) into detections."""
    pred = output[0] if output.ndim == 3 else output
    pred = pred.T  # (N, 4+C)
    scores_all = pred[:, 4:]
    cls_ids = scores_all.argmax(axis=1)
    confs = scores_all[np.arange(len(pred)), cls_ids]
    mask = confs >= conf_thresh
    if not mask.any():
        return []
    pred, cls_ids, confs = pred[mask], cls_ids[mask], confs[mask]

    orig_w, orig_h = orig_size
    sx, sy = orig_w / input_size, orig_h / input_size
    x_c, y_c, w, h = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
    boxes = np.stack(
        [(x_c - w / 2) * sx, (y_c - h / 2) * sy, (x_c + w / 2) * sx, (y_c + h / 2) * sy], axis=1
    )

    # Class-aware NMS: offset boxes by class so different classes never suppress each other.
    offset = cls_ids[:, None].astype(np.float32) * (max(orig_w, orig_h) + 1)
    keep = nms(boxes + offset, confs, iou_thresh)

    results: List[DetectionResult] = []
    for i in keep:
        cid = int(cls_ids[i])
        name = COCO_CLASSES[cid] if cid < len(COCO_CLASSES) else str(cid)
        results.append(
            DetectionResult(**{"class": name, "confidence": float(confs[i]), "bbox": [float(v) for v in boxes[i]]})
        )
    return results

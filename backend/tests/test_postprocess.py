import numpy as np

from app.services.postprocess import decode_yolov8, nms


def _head(rows, num_classes=80):
    """Build a (1, 4+C, N) YOLOv8 output from (xc, yc, w, h, cls, score) rows."""
    out = np.zeros((1, 4 + num_classes, len(rows)), dtype=np.float32)
    for i, (xc, yc, w, h, cls, score) in enumerate(rows):
        out[0, :4, i] = [xc, yc, w, h]
        out[0, 4 + cls, i] = score
    return out


def test_nms_suppresses_overlap():
    boxes = np.array([[0, 0, 10, 10], [1, 1, 11, 11], [50, 50, 60, 60]], dtype=np.float32)
    scores = np.array([0.9, 0.8, 0.7], dtype=np.float32)
    assert nms(boxes, scores, 0.5) == [0, 2]


def test_decode_filters_low_confidence_and_scales_boxes():
    out = _head([(320, 320, 100, 200, 0, 0.9), (100, 100, 10, 10, 1, 0.1)])
    dets = decode_yolov8(out, (1280, 640), conf_thresh=0.25, iou_thresh=0.45)
    assert len(dets) == 1
    d = dets[0]
    assert d.detected_class == "person"
    assert d.bbox == [540.0, 220.0, 740.0, 420.0]


def test_decode_removes_duplicates_but_keeps_different_classes():
    out = _head([
        (300, 300, 100, 100, 0, 0.9),
        (302, 302, 100, 100, 0, 0.8),
        (300, 300, 100, 100, 2, 0.7),
    ])
    dets = decode_yolov8(out, (640, 640), 0.25, 0.45)
    assert sorted(d.detected_class for d in dets) == ["car", "person"]


def test_decode_empty():
    assert decode_yolov8(_head([(1, 1, 1, 1, 0, 0.01)]), (640, 640), 0.25, 0.45) == []

import io

import pytest
from PIL import Image

from app.main import app
from app.core.dependencies import get_yolo_service
from app.core.exceptions import ModelNotLoadedError
from app.schemas.detection import DetectionResponse, DetectionResult


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), "red").save(buf, format="PNG")
    return buf.getvalue()


class FakeYolo:
    def detect(self, image, filename="image.jpg"):
        return DetectionResponse(
            filename=filename,
            detections=[DetectionResult(**{"class": "cat", "confidence": 0.9, "bbox": [1, 2, 3, 4]})],
            inference_device="cpu",
            inference_latency_ms=1.5,
        )


class UnloadedYolo:
    def detect(self, image, filename="image.jpg"):
        raise ModelNotLoadedError()


@pytest.fixture
def fake_yolo():
    app.dependency_overrides[get_yolo_service] = lambda: FakeYolo()
    yield
    app.dependency_overrides.pop(get_yolo_service, None)


@pytest.mark.anyio
async def test_detect_persists_and_shows_in_history(client, fake_yolo):
    r = await client.post("/api/v1/detect/", files={"file": ("a.png", _png(), "image/png")})
    assert r.status_code == 200
    body = r.json()
    assert body["detections"][0]["class"] == "cat"

    history = (await client.get("/api/v1/detections/")).json()
    assert history["total"] >= 1
    stats = (await client.get("/api/v1/detections/stats")).json()
    assert stats["total_detections"] >= 1
    assert stats["top_classes"][0]["class"] == "cat"


@pytest.mark.anyio
async def test_rejects_unsupported_type(client, fake_yolo):
    r = await client.post("/api/v1/detect/", files={"file": ("a.txt", b"hi", "text/plain")})
    assert r.status_code == 400


@pytest.mark.anyio
async def test_rejects_corrupt_image(client, fake_yolo):
    r = await client.post("/api/v1/detect/", files={"file": ("a.png", b"not an image", "image/png")})
    assert r.status_code == 400


@pytest.mark.anyio
async def test_rejects_oversized_upload(client, fake_yolo, monkeypatch):
    from app.api.v1.endpoints import detect

    monkeypatch.setattr(detect.get_settings(), "max_upload_mb", 0)
    r = await client.post("/api/v1/detect/", files={"file": ("a.png", _png(), "image/png")})
    assert r.status_code == 400


@pytest.mark.anyio
async def test_model_not_loaded_returns_503(client):
    app.dependency_overrides[get_yolo_service] = lambda: UnloadedYolo()
    try:
        r = await client.post("/api/v1/detect/", files={"file": ("a.png", _png(), "image/png")})
    finally:
        app.dependency_overrides.pop(get_yolo_service, None)
    assert r.status_code == 503


@pytest.mark.anyio
async def test_onnx_endpoint_503_when_not_loaded(client):
    r = await client.post("/api/v1/detect/onnx", files={"file": ("a.png", _png(), "image/png")})
    assert r.status_code == 503

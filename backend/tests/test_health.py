import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.anyio
async def test_health(client: AsyncClient):
    response = await client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_detections_empty(client: AsyncClient):
    response = await client.get("/api/v1/detections/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []

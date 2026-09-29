from __future__ import annotations
import io, sys
sys.path.insert(0, "backend")
import numpy as np
import pytest
import cv2
from httpx import AsyncClient

def _fake_image_bytes() -> bytes:
    img = np.zeros((480,640,3), dtype=np.uint8)
    img[:] = (60,60,60)
    cv2.line(img, (100,200), (400,220), (200,200,200), 2)
    ok, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()

@pytest.mark.asyncio
async def test_health(async_client: AsyncClient):
    resp = await async_client.get("/api/health")
    assert resp.status_code == 200 and resp.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_predict_requires_auth(async_client: AsyncClient):
    resp = await async_client.post("/api/predict", data={"vehicle_number":"MH01AB1234"})
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_predict_success(async_client: AsyncClient, auth_headers):
    img_bytes = _fake_image_bytes()
    resp = await async_client.post("/api/predict", headers=auth_headers,
        data={"vehicle_number":"MH01AB1234","vehicle_model":"Swift","owner_name":"Test Owner"},
        files={"image": ("test_car.jpg", io.BytesIO(img_bytes), "image/jpeg")})
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data and "severity_label" in data

@pytest.mark.asyncio
async def test_list_inspections(async_client: AsyncClient, auth_headers):
    resp = await async_client.get("/api/inspections", headers=auth_headers)
    assert resp.status_code == 200
    assert "items" in resp.json()

@pytest.mark.asyncio
async def test_dashboard(async_client: AsyncClient, auth_headers):
    resp = await async_client.get("/api/dashboard", headers=auth_headers)
    assert resp.status_code == 200
    assert "total_inspections" in resp.json()

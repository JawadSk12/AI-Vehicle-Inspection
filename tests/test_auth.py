from __future__ import annotations
import uuid
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    email = f"reg_{uuid.uuid4().hex[:6]}@capvia.ai"
    resp = await async_client.post("/api/auth/register", json={"name":"Jane Doe","email":email,"password":"SecurePass123!"})
    assert resp.status_code == 201
    assert resp.json()["email"] == email

@pytest.mark.asyncio
async def test_register_duplicate(async_client: AsyncClient):
    email = f"dup_{uuid.uuid4().hex[:6]}@capvia.ai"
    p = {"name":"Dup","email":email,"password":"SecurePass123!"}
    await async_client.post("/api/auth/register", json=p)
    resp = await async_client.post("/api/auth/register", json=p)
    assert resp.status_code == 400

@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    email = f"login_{uuid.uuid4().hex[:6]}@capvia.ai"
    await async_client.post("/api/auth/register", json={"name":"Login User","email":email,"password":"LoginPass123!"})
    resp = await async_client.post("/api/auth/login", json={"email":email,"password":"LoginPass123!"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient):
    email = f"badpass_{uuid.uuid4().hex[:6]}@capvia.ai"
    await async_client.post("/api/auth/register", json={"name":"X","email":email,"password":"CorrectPass1!"})
    resp = await async_client.post("/api/auth/login", json={"email":email,"password":"WrongPass1!"})
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_profile_with_auth(async_client: AsyncClient, auth_headers):
    resp = await async_client.get("/api/auth/profile", headers=auth_headers)
    assert resp.status_code == 200
    assert "email" in resp.json()

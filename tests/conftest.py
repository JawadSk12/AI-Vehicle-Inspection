from __future__ import annotations
import asyncio, os, uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_capvia.db")
os.environ.setdefault("JWT_SECRET", "test-secret-key-at-least-32-characters-long")
os.environ.setdefault("UPLOAD_DIR", "storage/test_uploads")
os.environ.setdefault("RESULT_DIR", "storage/test_results")
os.environ.setdefault("REPORT_DIR", "storage/test_reports")
os.environ.setdefault("MASK_DIR", "storage/test_masks")
os.environ.setdefault("MODEL_PATH", "nonexistent/model.pt")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_app():
    import sys
    if "." not in sys.path:
        sys.path.insert(0, ".")
    if "backend" not in sys.path:
        sys.path.insert(0, "backend")
    from app.models.user import User  # noqa: F401
    from app.models.inspection import Inspection  # noqa: F401
    from app.database import Base, engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    from app.main import app
    yield app
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="session")
async def async_client(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def auth_headers(async_client):
    email = f"test_{uuid.uuid4().hex[:6]}@capvia.ai"
    await async_client.post("/api/auth/register", json={"name":"Test User","email":email,"password":"TestPass123!"})
    resp = await async_client.post("/api/auth/login", json={"email":email,"password":"TestPass123!"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

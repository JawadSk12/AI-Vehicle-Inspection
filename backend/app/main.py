from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import create_tables
from app.routes import auth, dashboard, inspections, predict, reports

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CAPVIA AI backend...")
    settings.ensure_directories()
    await create_tables()
    logger.info("Database tables ready.")
    try:
        from app.database import async_session_factory
        from app.models.user import User
        from app.services.auth_service import hash_password
        from sqlalchemy import select
        async with async_session_factory() as db:
            res = await db.execute(select(User).where(User.email == "demo@capvia.ai"))
            if not res.scalar_one_or_none():
                demo_user = User(
                    name="Demo Inspector",
                    email="demo@capvia.ai",
                    hashed_password=hash_password("DemoPass123!"),
                    role="admin",
                    is_active=True,
                )
                db.add(demo_user)
                await db.commit()
                logger.info("Created default demo user: demo@capvia.ai / DemoPass123!")
    except Exception as exc:
        logger.warning(f"Could not seed demo user: {exc}")
    yield
    logger.info("Shutting down CAPVIA AI backend...")

app = FastAPI(title="CAPVIA AI", description="Automated Vehicle Paint Defect Detection & Assessment Platform", version="1.0.0", docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for d in [settings.upload_dir, settings.result_dir, settings.report_dir, settings.mask_dir]:
    Path(d).mkdir(parents=True, exist_ok=True)

app.mount("/storage", StaticFiles(directory="storage"), name="storage")

PREFIX = "/api"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(predict.router, prefix=PREFIX)
app.include_router(inspections.router, prefix=PREFIX)
app.include_router(reports.router, prefix=PREFIX)
app.include_router(dashboard.router, prefix=PREFIX)

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

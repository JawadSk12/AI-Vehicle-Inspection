"""
CAPVIA AI - Application Entry Point
Exports FastAPI application instance for ASGI servers (Uvicorn / Gunicorn).
Usage:
    uvicorn backend.app:app --reload --port 8000
    uvicorn app:app --reload --port 8000 (from backend/ directory)
"""
from __future__ import annotations
import sys
from pathlib import Path

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import main FastAPI application instance
from app.main import app

__all__ = ["app"]

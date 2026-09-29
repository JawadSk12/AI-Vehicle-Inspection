"""
CAPVIA AI - Centralized Backend Configuration
Single source of truth for all application and model parameters.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import settings, Settings

# Central AI Model Path configuration
# Every AI endpoint must read this variable
MODEL_PATH: str = os.getenv("MODEL_PATH", getattr(settings, "model_path", "ai_model/weights/best.pt"))

__all__ = ["MODEL_PATH", "settings", "Settings"]

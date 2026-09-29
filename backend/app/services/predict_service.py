"""
CAPVIA AI - Prediction Service
Delegates inference solely to ai_model.src.predict.
No model training code resides in the backend.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List
from app.config import settings
from ai_model.src.predict import predict_image

logger = logging.getLogger(__name__)


def run_inference(image_path: str) -> List[Dict[str, Any]]:
    """
    Run Faster R-CNN inference by calling ONLY ai_model.src.predict.predict_image.
    """
    logger.info(f"Running inference on {image_path}")
    return predict_image(
        image_path=image_path,
        conf=settings.model_confidence,
    )

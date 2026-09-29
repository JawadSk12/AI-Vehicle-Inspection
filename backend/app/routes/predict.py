from __future__ import annotations
import logging, os, uuid
from pathlib import Path
import aiofiles, cv2
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
from app.models.inspection import Inspection
from app.models.user import User
from app.schemas.inspection import InspectionOut
from app.services.cost_service import estimate_cost
from app.services.predict_service import run_inference
from app.services.severity_service import compute_severity
from app.utils.calibration import get_scale_factor
from app.utils.dependencies import get_current_user
from app.utils.file_utils import ensure_dir
from app.utils.glare_filter import filter_glare_detections
from app.utils.image_utils import draw_detections
from app.utils.measurement import enrich_detections

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["Prediction"])
ALLOWED = {".jpg",".jpeg",".png",".webp",".bmp"}

@router.post("", response_model=InspectionOut, status_code=201)
async def predict(
    vehicle_number: str = Form(...), vehicle_model: str = Form(""),
    owner_name: str = Form(""), inspector_name: str = Form(""),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    suffix = Path(image.filename or "image.jpg").suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(400, f"Unsupported file type: {suffix}")
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    file_id = uuid.uuid4().hex
    upload_dir = ensure_dir(settings.upload_dir)
    orig_path = str(upload_dir / f"{file_id}_original{suffix}")
    async with aiofiles.open(orig_path, "wb") as f:
        total = 0
        while chunk := await image.read(8192):
            total += len(chunk)
            if total > max_bytes:
                os.remove(orig_path)
                raise HTTPException(413, "File too large.")
            await f.write(chunk)
    try:
        detections = run_inference(orig_path)
    except Exception as exc:
        logger.error(f"Inference failed: {exc}", exc_info=True)
        raise HTTPException(500, "Model inference failed.")
    img_bgr = cv2.imread(orig_path)
    img_h, img_w = img_bgr.shape[:2]
    detections = filter_glare_detections(img_bgr, detections)
    scale = get_scale_factor()
    detections = enrich_detections(detections, scale)
    real_dets = [d for d in detections if not d.get("is_glare", False)]
    severity_score, severity_label = compute_severity(real_dets, img_w, img_h)
    cost_info = estimate_cost(severity_score, severity_label, len(real_dets))
    result_dir = ensure_dir(settings.result_dir)
    result_path = str(result_dir / f"{file_id}_result{suffix}")
    draw_detections(orig_path, real_dets, result_path)
    avg_conf = sum(d["confidence"] for d in real_dets) / len(real_dets) if real_dets else 0.0
    total_area = sum(d.get("area_mm2", 0.0) for d in real_dets)
    inspection = Inspection(
        user_id=current_user.id, vehicle_number=vehicle_number,
        vehicle_model=vehicle_model or None, owner_name=owner_name or None,
        inspector_name=inspector_name or None, image_path=orig_path, result_path=result_path,
        defects=[{k: v for k, v in d.items()} for d in real_dets],
        severity_score=severity_score, severity_label=severity_label,
        confidence=round(avg_conf, 4), total_area_mm2=round(total_area, 3),
        defect_count=len(real_dets), **cost_info,
    )
    db.add(inspection)
    await db.flush()
    await db.refresh(inspection)
    out = InspectionOut.model_validate(inspection)
    out.has_report = False
    return out

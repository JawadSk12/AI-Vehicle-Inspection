from __future__ import annotations
import csv, io, logging, os, uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.inspection import Inspection
from app.models.report import Report
from app.models.user import User
from app.schemas.inspection import InspectionListOut, InspectionOut
from app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/inspections", tags=["Inspections"])

@router.get("", response_model=InspectionListOut)
async def list_inspections(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None), severity: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    stmt = select(Inspection).where(Inspection.user_id == current_user.id).order_by(desc(Inspection.created_at))
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(or_(Inspection.vehicle_number.ilike(pattern), Inspection.owner_name.ilike(pattern), Inspection.vehicle_model.ilike(pattern)))
    if severity:
        stmt = stmt.where(Inspection.severity_label == severity)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    rows = (await db.execute(stmt)).scalars().all()
    items = []
    for row in rows:
        rep = (await db.execute(select(Report).where(Report.inspection_id == row.id))).scalar_one_or_none()
        out = InspectionOut.model_validate(row)
        out.has_report = rep is not None
        items.append(out)
    return InspectionListOut(total=total, page=page, limit=limit, items=items)

@router.get("/{inspection_id}", response_model=InspectionOut)
async def get_inspection(inspection_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id, Inspection.user_id == current_user.id))
    insp = result.scalar_one_or_none()
    if not insp:
        raise HTTPException(404, "Inspection not found.")
    rep = (await db.execute(select(Report).where(Report.inspection_id == insp.id))).scalar_one_or_none()
    out = InspectionOut.model_validate(insp)
    out.has_report = rep is not None
    return out

@router.delete("/{inspection_id}", status_code=204)
async def delete_inspection(inspection_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id, Inspection.user_id == current_user.id))
    insp = result.scalar_one_or_none()
    if not insp:
        raise HTTPException(404, "Inspection not found.")
    for path in [insp.image_path, insp.result_path, insp.mask_path]:
        if path and os.path.exists(path):
            try: os.remove(path)
            except OSError: pass
    await db.delete(insp)

@router.get("/{inspection_id}/csv")
async def export_csv(inspection_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id, Inspection.user_id == current_user.id))
    insp = result.scalar_one_or_none()
    if not insp:
        raise HTTPException(404, "Inspection not found.")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID","Vehicle Number","Vehicle Model","Owner","Inspector","Severity Score","Severity Label","Defect Count","Total Area mm2","Confidence","Repair Cost INR","Time Required","Priority","Created At"])
    writer.writerow([str(insp.id),insp.vehicle_number,insp.vehicle_model,insp.owner_name,insp.inspector_name,insp.severity_score,insp.severity_label,insp.defect_count,insp.total_area_mm2,insp.confidence,insp.repair_cost_estimated,insp.time_required,insp.priority,insp.created_at.isoformat()])
    output.seek(0)
    return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=inspection_{inspection_id}.csv"})

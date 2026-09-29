from __future__ import annotations
import logging, os, uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.inspection import Inspection
from app.models.report import Report
from app.models.user import User
from app.reports.pdf_generator import generate_pdf
from app.schemas.report import ReportOut
from app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/{inspection_id}/generate", response_model=ReportOut)
async def generate_report(inspection_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id, Inspection.user_id == current_user.id))
    insp = result.scalar_one_or_none()
    if not insp:
        raise HTTPException(404, "Inspection not found.")
    existing = (await db.execute(select(Report).where(Report.inspection_id == insp.id))).scalar_one_or_none()
    if existing:
        return existing
    try:
        pdf_path = generate_pdf(insp, current_user)
    except Exception as exc:
        logger.error(f"PDF generation failed: {exc}", exc_info=True)
        raise HTTPException(500, "PDF generation failed.")
    report = Report(inspection_id=insp.id, pdf_path=pdf_path)
    db.add(report)
    await db.flush()
    await db.refresh(report)
    return report

@router.get("/{inspection_id}", response_class=FileResponse)
async def download_report(inspection_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id, Inspection.user_id == current_user.id))
    insp = result.scalar_one_or_none()
    if not insp:
        raise HTTPException(404, "Inspection not found.")
    rep_res = (await db.execute(select(Report).where(Report.inspection_id == insp.id))).scalar_one_or_none()
    if not rep_res:
        raise HTTPException(404, "Report not yet generated. Call POST /reports/{id}/generate first.")
    if not os.path.exists(rep_res.pdf_path):
        raise HTTPException(410, "PDF file missing from storage.")
    return FileResponse(path=rep_res.pdf_path, media_type="application/pdf", filename=f"CAPVIA_Inspection_{inspection_id}.pdf")

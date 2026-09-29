from __future__ import annotations
import logging
from collections import defaultdict
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.inspection import Inspection
from app.models.user import User
from app.schemas.dashboard import DashboardOut, MonthlyCount, SeverityCount
from app.schemas.inspection import InspectionOut
from app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardOut)
async def dashboard(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Inspection).where(Inspection.user_id == current_user.id))
    all_insp = result.scalars().all()
    total = len(all_insp)
    critical = sum(1 for i in all_insp if i.severity_label == "Critical")
    avg_sev = sum(i.severity_score or 0 for i in all_insp) / total if total else 0.0
    avg_cost = sum(i.repair_cost_estimated or 0 for i in all_insp) / total if total else 0.0
    monthly: dict = defaultdict(lambda: {"count":0,"total_cost":0.0})
    for insp in all_insp:
        key = insp.created_at.strftime("%b %Y")
        monthly[key]["count"] += 1
        monthly[key]["total_cost"] += insp.repair_cost_estimated or 0.0
    monthly_data = [MonthlyCount(month=k, count=v["count"], avg_cost=round(v["total_cost"]/v["count"],2) if v["count"] else 0.0) for k, v in sorted(monthly.items(), key=lambda x: datetime.strptime(x[0], "%b %Y"))][-12:]
    sev_counts: dict = defaultdict(int)
    for insp in all_insp:
        if insp.severity_label:
            sev_counts[insp.severity_label] += 1
    severity_dist = [SeverityCount(label=lbl, count=cnt, percentage=round(cnt/total*100,1) if total else 0.0) for lbl, cnt in sev_counts.items()]
    recent = sorted(all_insp, key=lambda x: x.created_at, reverse=True)[:5]
    return DashboardOut(total_inspections=total, critical_defects=critical, avg_severity=round(avg_sev,2), avg_repair_cost=round(avg_cost,2), monthly_inspections=monthly_data, severity_distribution=severity_dist, recent_inspections=[InspectionOut.model_validate(i).model_dump() for i in recent])

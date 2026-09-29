from __future__ import annotations
from typing import List
from pydantic import BaseModel

class MonthlyCount(BaseModel):
    month: str
    count: int
    avg_cost: float

class SeverityCount(BaseModel):
    label: str
    count: int
    percentage: float

class DashboardOut(BaseModel):
    total_inspections: int
    critical_defects: int
    avg_severity: float
    avg_repair_cost: float
    monthly_inspections: List[MonthlyCount]
    severity_distribution: List[SeverityCount]
    recent_inspections: list

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class DefectItem(BaseModel):
    defect_id: int
    class_name: str
    confidence: float
    bbox: List[float]
    area_px: float
    area_mm2: float
    length_mm: float
    width_mm: float
    perimeter_mm: float
    panel: Optional[str] = None
    is_glare: bool = False
    glare_score: float = 0.0

class InspectionCreate(BaseModel):
    vehicle_number: str = Field(..., min_length=2, max_length=30)
    vehicle_model: Optional[str] = None
    owner_name: Optional[str] = None
    inspector_name: Optional[str] = None

class InspectionOut(BaseModel):
    id: uuid.UUID
    vehicle_number: str
    vehicle_model: Optional[str] = None
    owner_name: Optional[str] = None
    inspector_name: Optional[str] = None
    image_path: str
    result_path: Optional[str] = None
    mask_path: Optional[str] = None
    defects: Optional[List[Dict[str, Any]]] = None
    severity_score: Optional[float] = None
    severity_label: Optional[str] = None
    confidence: Optional[float] = None
    total_area_mm2: Optional[float] = None
    defect_count: Optional[int] = None
    repair_cost_min: Optional[float] = None
    repair_cost_max: Optional[float] = None
    repair_cost_estimated: Optional[float] = None
    time_required: Optional[str] = None
    priority: Optional[str] = None
    recommendation: Optional[str] = None
    created_at: datetime
    has_report: bool = False
    model_config = {"from_attributes": True}

class InspectionListOut(BaseModel):
    total: int
    page: int
    limit: int
    items: List[InspectionOut]

from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel

class ReportOut(BaseModel):
    id: uuid.UUID
    inspection_id: uuid.UUID
    pdf_path: str
    generated_at: datetime
    model_config = {"from_attributes": True}

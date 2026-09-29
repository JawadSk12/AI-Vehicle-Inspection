from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.types import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Inspection(Base):
    __tablename__ = "inspections"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    vehicle_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    vehicle_model: Mapped[str] = mapped_column(String(120), nullable=True)
    owner_name: Mapped[str] = mapped_column(String(120), nullable=True)
    inspector_name: Mapped[str] = mapped_column(String(120), nullable=True)
    image_path: Mapped[str] = mapped_column(String(512), nullable=False)
    result_path: Mapped[str] = mapped_column(String(512), nullable=True)
    mask_path: Mapped[str] = mapped_column(String(512), nullable=True)
    polygon_path: Mapped[str] = mapped_column(String(512), nullable=True)
    defects: Mapped[list] = mapped_column(JSON, nullable=True)
    severity_score: Mapped[float] = mapped_column(Float, nullable=True)
    severity_label: Mapped[str] = mapped_column(String(30), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    total_area_mm2: Mapped[float] = mapped_column(Float, nullable=True)
    defect_count: Mapped[int] = mapped_column(Integer, nullable=True)
    repair_cost_min: Mapped[float] = mapped_column(Float, nullable=True)
    repair_cost_max: Mapped[float] = mapped_column(Float, nullable=True)
    repair_cost_estimated: Mapped[float] = mapped_column(Float, nullable=True)
    time_required: Mapped[str] = mapped_column(String(50), nullable=True)
    priority: Mapped[str] = mapped_column(String(30), nullable=True)
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user: Mapped["User"] = relationship("User", back_populates="inspections")
    report: Mapped["Report"] = relationship("Report", back_populates="inspection", uselist=False, cascade="all, delete-orphan")

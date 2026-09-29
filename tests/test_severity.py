from __future__ import annotations
import sys; sys.path.insert(0, "backend")
from app.services.severity_service import compute_severity

def _det(cls="scratch", conf=0.85, area_px=10000):
    return {"class_name": cls, "confidence": conf, "area_px": area_px}

def test_no_defects():
    score, label = compute_severity([], 1920, 1080)
    assert score == 0.0 and label == "Minor"

def test_single_minor():
    _, label = compute_severity([_det(area_px=500)], 640, 640)
    assert label in ("Minor", "Low")

def test_many_critical():
    dets = [_det("dent", 0.99, 40000) for _ in range(15)]
    score, label = compute_severity(dets, 640, 640)
    assert score > 60

def test_score_clamped():
    dets = [_det("paint_crack", 1.0, 999999) for _ in range(50)]
    score, _ = compute_severity(dets, 640, 640)
    assert 0 <= score <= 100

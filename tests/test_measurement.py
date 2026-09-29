from __future__ import annotations
import sys; sys.path.insert(0, "backend")
import pytest
from app.utils.measurement import bbox_to_measurements, enrich_detections

def test_bbox_area():
    m = bbox_to_measurements([100,100,200,150], 0.05)
    assert abs(m["area_mm2"] - 12.5) < 0.01

def test_bbox_length_width():
    m = bbox_to_measurements([0,0,200,100], 0.1)
    assert m["length_mm"] == pytest.approx(20.0)
    assert m["width_mm"] == pytest.approx(10.0)

def test_enrich_detections():
    dets = [{"bbox":[10,10,60,40],"class_id":0,"class_name":"scratch","confidence":0.9}]
    enriched = enrich_detections(dets, 0.05)
    assert "area_mm2" in enriched[0]

def test_zero_area():
    m = bbox_to_measurements([50,50,50,50], 0.05)
    assert m["area_mm2"] == 0.0

"""
Unit and Integration Tests for ai_model modular pipeline.
"""
from __future__ import annotations
import numpy as np
import pytest
from ai_model.src.calibration import CalibrationEngine, get_scale_factor
from ai_model.src.glare_filter import analyze_patch_glare, filter_glare_detections
from ai_model.src.measure import compute_bbox_geometry, convert_pixels_to_mm, enrich_detections
from ai_model.src.postprocess import apply_nms, filter_by_confidence
from ai_model.src.predict import predict_image
from ai_model.src.preprocess import adjust_gamma, apply_clahe, letterbox_resize
from ai_model.src.severity import compute_severity_score, estimate_repair_cost_inr, generate_recommendation


def test_preprocess_operations():
    dummy = np.full((500, 750, 3), 120, dtype=np.uint8)
    clahe_out = apply_clahe(dummy)
    assert clahe_out.shape == dummy.shape

    gamma_out = adjust_gamma(dummy, gamma=1.2)
    assert gamma_out.shape == dummy.shape

    letterbox_out, scale, pads = letterbox_resize(dummy, target_size=1024)
    assert letterbox_out.shape == (1024, 1024, 3)
    assert scale > 0
    assert len(pads) == 2


def test_postprocess_nms():
    boxes = [[10, 10, 50, 50], [12, 12, 48, 48], [100, 100, 200, 200]]
    scores = [0.95, 0.85, 0.90]
    keep = apply_nms(boxes, scores, iou_threshold=0.45)
    # The first two boxes heavily overlap; only one should be kept, plus the third box
    assert len(keep) == 2
    assert 0 in keep
    assert 2 in keep


def test_measure_and_conversion():
    bbox = [50, 100, 250, 300]
    geom = compute_bbox_geometry(bbox)
    assert geom["pixel_width"] == 200.0
    assert geom["pixel_length"] > 200.0
    assert geom["centroid_x"] == 150.0
    assert geom["centroid_y"] == 200.0

    metric = convert_pixels_to_mm(geom, scale_factor_mm_per_pixel=0.05)
    assert metric["length_mm"] > 0
    assert metric["area_mm2"] == round(geom["pixel_area"] * 0.05 * 0.05, 2)


def test_glare_filtering():
    white_glare = np.full((100, 100, 3), 255, dtype=np.uint8)
    is_glare, score = analyze_patch_glare(white_glare)
    assert is_glare is True
    assert score >= 0.48

    normal_paint = np.full((100, 100, 3), (120, 50, 40), dtype=np.uint8)
    is_glare2, score2 = analyze_patch_glare(normal_paint)
    assert is_glare2 is False


def test_severity_and_cost_inr():
    defects = [
        {"class_name": "scratch", "pixel_area": 450.0, "confidence": 0.88, "is_glare": False},
        {"class_name": "deep_scratch", "pixel_area": 1200.0, "confidence": 0.92, "is_glare": False},
    ]
    score, label = compute_severity_score(defects, img_width=1920, img_height=1080)
    assert 1 <= score <= 100
    assert label in ["Minor", "Low", "Moderate", "High", "Critical"]

    rec = generate_recommendation(label, len(defects))
    assert len(rec) > 10

    cost = estimate_repair_cost_inr(score, label, len(defects))
    assert cost["currency"] == "INR"
    assert cost["currency_symbol"] == "₹"
    assert cost["cost_range_min_inr"] <= cost["estimated_cost_inr"] <= cost["cost_range_max_inr"]


def test_calibration_modes():
    engine = CalibrationEngine(default_scale=0.05)
    scale_dpi = engine.from_dpi(300.0)
    assert round(scale_dpi, 4) == round(25.4 / 300.0, 4)

    scale_marker = engine.from_reference_marker(marker_pixel_dimension=500.0, real_world_marker_mm=25.0)
    assert scale_marker == 0.05

    scale_dist = engine.from_camera_distance(distance_cm=50.0, sensor_focal_length_mm=4.0, sensor_width_mm=6.0, image_width_px=1920)
    assert scale_dist > 0


def test_predict_fallback(tmp_path):
    # Create temporary dummy image
    import cv2
    img_path = str(tmp_path / "test_car.jpg")
    cv2.imwrite(img_path, np.full((400, 600, 3), 100, dtype=np.uint8))

    # Test predict_image with non-existent weights -> graceful fallback
    dets = predict_image(img_path, weights_path="nonexistent_weights.pt")
    assert isinstance(dets, list)
    assert len(dets) > 0
    assert "bbox" in dets[0]
    assert "class_name" in dets[0]

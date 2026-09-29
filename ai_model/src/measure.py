"""
CAPVIA AI - Defect Measurement Engine
Calculates Pixel Area, Length, Width, Centroid, Aspect Ratio,
and converts to real-world millimeters (mm and mm²) using dynamic calibration.
"""
from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


def compute_bbox_geometry(
    bbox: List[int],
) -> Dict[str, float]:
    """
    Extract geometric metrics from a bounding box [x1, y1, x2, y2].
    """
    x1, y1, x2, y2 = [float(v) for v in bbox]
    w = max(1.0, x2 - x1)
    h = max(1.0, y2 - y1)
    cx = round(x1 + w / 2.0, 2)
    cy = round(y1 + h / 2.0, 2)

    # For elongated scratches, length is the diagonal or maximum axis
    length_px = round(math.sqrt(w * w + h * h), 2)
    width_px = round(min(w, h), 2)
    area_px = round(w * h, 2)
    perimeter_px = round(2 * (w + h), 2)
    aspect_ratio = round(max(w, h) / max(min(w, h), 1e-4), 2)
    orientation_deg = round(math.degrees(math.atan2(h, w)), 1)

    return {
        "pixel_length": length_px,
        "pixel_width": width_px,
        "pixel_area": area_px,
        "pixel_perimeter": perimeter_px,
        "centroid_x": cx,
        "centroid_y": cy,
        "aspect_ratio": aspect_ratio,
        "orientation_deg": orientation_deg,
    }


def compute_mask_geometry(
    mask: np.ndarray,
) -> Dict[str, float]:
    """
    Extract high-precision pixel metrics from a binary segmentation mask.
    """
    contours, _ = cv2_find_contours(mask)
    if not contours:
        return {}

    # Get largest contour for primary defect
    largest = max(contours, key=len)
    area_px = float(len(np.where(mask > 0)[0]))
    perimeter_px = float(len(largest))

    # Minimum area bounding rectangle for exact length and width
    if len(largest) >= 5:
        # Fit ellipse or min area rect
        rect = cv2_min_area_rect(largest)
        (cx, cy), (rw, rh), angle = rect
        length_px = max(rw, rh)
        width_px = min(rw, rh)
    else:
        cx, cy = float(np.mean(largest[:, 0])), float(np.mean(largest[:, 1]))
        length_px = math.sqrt(area_px)
        width_px = math.sqrt(area_px)
        angle = 0.0

    return {
        "pixel_length": round(length_px, 2),
        "pixel_width": round(width_px, 2),
        "pixel_area": round(area_px, 2),
        "pixel_perimeter": round(perimeter_px, 2),
        "centroid_x": round(cx, 2),
        "centroid_y": round(cy, 2),
        "aspect_ratio": round(length_px / max(width_px, 1e-4), 2),
        "orientation_deg": round(angle, 1),
    }


def cv2_find_contours(mask: np.ndarray):
    """Safe wrapper around cv2.findContours."""
    try:
        import cv2
        contours, hierarchy = cv2.findContours(
            mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contours, hierarchy
    except ImportError:
        return [], None


def cv2_min_area_rect(contour: np.ndarray):
    """Safe wrapper around cv2.minAreaRect."""
    try:
        import cv2
        return cv2.minAreaRect(contour)
    except ImportError:
        return (0.0, 0.0), (1.0, 1.0), 0.0


def convert_pixels_to_mm(
    pixel_metrics: Dict[str, float],
    scale_factor_mm_per_pixel: float,
) -> Dict[str, float]:
    """
    Convert pixel metrics to real-world millimeters.
    scale_factor: millimeters per pixel (e.g. 0.05 mm/px means 1 px = 0.05 mm).
    Area scales quadratically: mm² = px * (scale_factor ** 2).
    """
    scale = max(scale_factor_mm_per_pixel, 1e-6)
    scale_sq = scale * scale

    length_mm = round(pixel_metrics.get("pixel_length", 0.0) * scale, 2)
    width_mm = round(pixel_metrics.get("pixel_width", 0.0) * scale, 2)
    area_mm2 = round(pixel_metrics.get("pixel_area", 0.0) * scale_sq, 2)
    perimeter_mm = round(pixel_metrics.get("pixel_perimeter", 0.0) * scale, 2)

    return {
        "length_mm": length_mm,
        "width_mm": width_mm,
        "area_mm2": area_mm2,
        "perimeter_mm": perimeter_mm,
        "scale_factor_used": scale,
    }


def enrich_detections(
    detections: List[Dict[str, Any]],
    scale_factor: float = 0.05,
    mask: Optional[np.ndarray] = None,
) -> List[Dict[str, Any]]:
    """
    Enrich raw detection dictionaries with physical measurement attributes.
    """
    enriched = []
    for det in detections:
        d = dict(det)
        bbox = d.get("bbox", [0, 0, 0, 0])
        px_geo = compute_bbox_geometry(bbox)
        mm_geo = convert_pixels_to_mm(px_geo, scale_factor)

        d.update(px_geo)
        d.update(mm_geo)
        enriched.append(d)
    return enriched

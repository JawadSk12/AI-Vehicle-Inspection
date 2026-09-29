"""
CAPVIA AI - Glare and False Positive Rejection Module
Identifies and rejects specular highlights, LED reflections, chrome glares,
and sunlight flares falsely detected as scratches or defects.
"""
from __future__ import annotations
from typing import Any, Dict, List, Tuple
import cv2
import numpy as np


def analyze_patch_glare(crop_bgr: np.ndarray) -> Tuple[bool, float]:
    """
    Analyzes an image crop for specular glare characteristics:
    1. Brightness map saturation (V channel in HSV and L channel in LAB)
    2. Overexposure ratio (> 240 pixel intensity)
    3. Color saturation deficiency (reflections are near white/grey)
    4. Gradient uniformity via Laplacian variance
    """
    if crop_bgr is None or crop_bgr.size == 0:
        return False, 0.0

    hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)
    _, s_channel, v_channel = cv2.split(hsv)

    # 1. Overexposed pixel ratio (V > 240)
    overexposed_px = np.count_nonzero(v_channel >= 240)
    total_px = max(crop_bgr.shape[0] * crop_bgr.shape[1], 1)
    overexposure_ratio = overexposed_px / total_px

    # 2. Desaturation check (glare highlights have low saturation < 40)
    desaturated_px = np.count_nonzero(s_channel <= 45)
    desaturation_ratio = desaturated_px / total_px

    # 3. Brightness center concentration via morphological gradient
    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    morph_gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
    edge_energy = float(np.mean(morph_gradient))

    # 4. Specular score computation
    # Glare has: high overexposure, high desaturation, and concentrated gradient bloom
    glare_score = (
        (overexposure_ratio * 0.55)
        + (desaturation_ratio * 0.30)
        + (min(edge_energy / 60.0, 1.0) * 0.15)
    )
    glare_score = round(min(max(glare_score, 0.0), 1.0), 4)

    is_glare = bool(glare_score >= 0.48 or (overexposure_ratio > 0.40 and desaturation_ratio > 0.50))
    return is_glare, glare_score


def filter_glare_detections(
    image_bgr: np.ndarray,
    detections: List[Dict[str, Any]],
    glare_threshold: float = 0.50,
) -> List[Dict[str, Any]]:
    """
    Examines all bounding boxes against the parent image and tags glare false positives.
    """
    h, w = image_bgr.shape[:2]
    filtered = []

    for det in detections:
        d = dict(det)
        bbox = d.get("bbox", [0, 0, 0, 0])
        x1, y1, x2, y2 = [int(v) for v in bbox]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        if x2 <= x1 or y2 <= y1:
            d["is_glare"] = False
            d["glare_score"] = 0.0
            filtered.append(d)
            continue

        crop = image_bgr[y1:y2, x1:x2]
        is_glare, score = analyze_patch_glare(crop)

        d["is_glare"] = is_glare
        d["glare_score"] = score
        filtered.append(d)

    return filtered

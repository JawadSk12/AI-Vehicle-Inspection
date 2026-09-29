from __future__ import annotations
from typing import Any, Dict, List
import cv2
import numpy as np

def compute_glare_score(img_bgr: np.ndarray, bbox: List[float]) -> Dict[str, Any]:
    x1, y1, x2, y2 = [int(v) for v in bbox]
    roi = img_bgr[y1:y2, x1:x2]
    if roi.size == 0:
        return {"is_glare": False, "glare_score": 0.0}
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    bright_ratio = float((gray > 230).mean())
    mean_s = float(hsv[:, :, 1].mean())
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    texture_score = float(thresh.std()) / 128.0
    contours, _ = cv2.findContours((gray > 200).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    circularity = 0.0
    if contours:
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter ** 2)
    score = round(min(bright_ratio*0.35 + (1-min(mean_s/80.0,1.0))*0.25 + (1-min(texture_score,1.0))*0.20 + min(circularity,1.0)*0.20, 1.0), 4)
    return {"is_glare": score > 0.60, "glare_score": score}

def filter_glare_detections(img_bgr: np.ndarray, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for det in detections:
        result = compute_glare_score(img_bgr, det["bbox"])
        det["is_glare"] = result["is_glare"]
        det["glare_score"] = result["glare_score"]
    return detections

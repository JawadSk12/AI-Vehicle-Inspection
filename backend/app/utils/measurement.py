from __future__ import annotations
from typing import Any, Dict, List
import numpy as np

def bbox_to_measurements(bbox: List[float], scale_mm_per_px: float) -> Dict[str, float]:
    x1, y1, x2, y2 = bbox
    pw = abs(x2 - x1)
    ph = abs(y2 - y1)
    pa = pw * ph
    return {
        "area_px": round(pa, 2),
        "length_mm": round(max(pw, ph) * scale_mm_per_px, 3),
        "width_mm": round(min(pw, ph) * scale_mm_per_px, 3),
        "area_mm2": round(pa * (scale_mm_per_px ** 2), 3),
        "perimeter_mm": round(2*(pw+ph)*scale_mm_per_px, 3),
        "centroid_x": round((x1+x2)/2, 1),
        "centroid_y": round((y1+y2)/2, 1),
    }

def enrich_detections(detections: List[Dict[str, Any]], scale_mm_per_px: float) -> List[Dict[str, Any]]:
    for i, det in enumerate(detections):
        m = bbox_to_measurements(det["bbox"], scale_mm_per_px)
        det.update(m)
        det["defect_id"] = i
    return detections

from __future__ import annotations
from typing import Any, Dict, List, Tuple

CLASS_PENALTY: Dict[str, float] = {
    "scratch": 0.5, "paint_crack": 0.8, "paint_peel": 0.7,
    "dent": 0.9, "surface_damage": 0.6, "dirt_nib": 0.3,
    "orange_peel": 0.4, "paint_run": 0.5, "fisheye": 0.6,
}
SEVERITY_LEVELS = [(0,20,"Minor"),(21,40,"Low"),(41,60,"Moderate"),(61,80,"High"),(81,100,"Critical")]

def compute_severity(defects: List[Dict[str, Any]], image_width: int, image_height: int) -> Tuple[float, str]:
    if not defects:
        return 0.0, "Minor"
    image_area = image_width * image_height
    total_area_px = sum(d.get("area_px", 0.0) for d in defects)
    area_ratio = min(total_area_px / image_area, 1.0)
    area_factor = area_ratio * 45.0
    n = len(defects)
    count_factor = min(n / 10.0, 1.0) * 25.0
    avg_conf = sum(d.get("confidence", 0.5) for d in defects) / n
    conf_factor = avg_conf * 15.0
    max_penalty = max(CLASS_PENALTY.get(d.get("class_name", "scratch"), 0.5) for d in defects)
    class_factor = max_penalty * 15.0
    score = round(min(area_factor + count_factor + conf_factor + class_factor, 100.0), 2)
    label = next((lbl for lo, hi, lbl in SEVERITY_LEVELS if lo <= score <= hi), "Critical")
    return score, label

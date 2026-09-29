"""
CAPVIA AI - Defect Severity & Assessment Engine
Computes 0-100 severity index based on defect counts, surface area ratio,
depth/class weights, and panel importance. Generates repair recommendations.
"""
from __future__ import annotations
from typing import Any, Dict, List, Tuple

PANEL_WEIGHTS = {
    "hood": 1.3,
    "front_door": 1.2,
    "rear_door": 1.1,
    "fender": 1.15,
    "bumper": 1.0,
    "roof": 0.9,
    "trunk": 1.05,
    "quarter_panel": 1.15,
}

DEFECT_TYPE_WEIGHTS = {
    "paint_peel": 1.8,
    "paint_crack": 1.6,
    "deep_scratch": 1.5,
    "orange_peel": 1.3,
    "paint_run": 1.2,
    "fisheye": 1.2,
    "dirt_nib": 1.1,
    "scratch": 1.0,
    "hairline_scratch": 0.8,
}


def compute_severity_score(
    defects: List[Dict[str, Any]],
    img_width: int,
    img_height: int,
    panel_name: str = "hood",
) -> Tuple[int, str]:
    """
    Calculate 0-100 severity score and label.
    """
    if not defects:
        return 0, "None"

    total_px = max(img_width * img_height, 1)
    total_defect_px = sum(
        d.get("pixel_area", 0.0) for d in defects if not d.get("is_glare", False)
    )
    count = len([d for d in defects if not d.get("is_glare", False)])

    if count == 0:
        return 0, "None"

    # Area factor: defect area relative to image
    area_ratio = total_defect_px / total_px
    area_score = min(area_ratio * 2500, 35.0)

    # Count factor
    count_score = min(count * 6.5, 30.0)

    # Defect severity weight factor
    type_factors = [
        DEFECT_TYPE_WEIGHTS.get(d.get("class_name", "scratch").lower(), 1.0)
        for d in defects
    ]
    avg_type_factor = sum(type_factors) / max(len(type_factors), 1)

    # Confidence factor
    avg_conf = sum(d.get("confidence", 0.8) for d in defects) / max(len(defects), 1)

    # Panel weight factor
    panel_weight = PANEL_WEIGHTS.get(panel_name.lower(), 1.1)

    # Base formula combining dimensions
    raw_score = (area_score + count_score) * avg_type_factor * (0.8 + 0.2 * avg_conf) * panel_weight
    final_score = int(min(max(round(raw_score), 1), 100))

    if final_score <= 20:
        label = "Minor"
    elif final_score <= 40:
        label = "Low"
    elif final_score <= 60:
        label = "Moderate"
    elif final_score <= 80:
        label = "High"
    else:
        label = "Critical"

    return final_score, label


def generate_recommendation(severity_label: str, defect_count: int) -> str:
    """
    Generate professional inspection recommendations based on severity level.
    """
    recommendations = {
        "None": "No visible paint defects detected. Panel finish is in pristine factory condition.",
        "Minor": f"{defect_count} minor surface blemish(es) detected. Light compounding and rotary polishing recommended. Clearcoat remains intact.",
        "Low": f"{defect_count} defect(s) detected. High-grit wet-sanding (2500-3000 grit) followed by two-stage paint correction recommended.",
        "Moderate": f"{defect_count} moderate defect(s) detected with localized clearcoat breach. Spot touch-up, micro-fill, and spot clearcoat blend recommended.",
        "High": f"{defect_count} severe defect(s) detected with primer/basecoat exposure. Requires surface feathering, epoxy primer fill, and spot panel re-spray.",
        "Critical": f"{defect_count} critical defect(s) with structural substrate exposure. Full panel stripping, multi-stage priming, basecoat application, and complete clearcoat re-bake required.",
    }
    return recommendations.get(severity_label, recommendations["Moderate"])


def estimate_repair_cost_inr(
    severity_score: int,
    severity_label: str,
    defect_count: int,
) -> Dict[str, Any]:
    """
    Calculate repair cost estimate in Indian Rupees (INR - ₹).
    """
    ranges = {
        "None": {"min": 0, "max": 0, "time_hours": 0.0, "priority": "None"},
        "Minor": {"min": 500, "max": 1500, "time_hours": 1.5, "priority": "Low"},
        "Low": {"min": 1500, "max": 3000, "time_hours": 3.0, "priority": "Normal"},
        "Moderate": {"min": 3000, "max": 6000, "time_hours": 6.0, "priority": "Medium"},
        "High": {"min": 6000, "max": 10000, "time_hours": 12.0, "priority": "High"},
        "Critical": {"min": 10000, "max": 18000, "time_hours": 24.0, "priority": "Urgent"},
    }
    r = ranges.get(severity_label, ranges["Moderate"])
    # Dynamic interpolation
    min_cost = r["min"]
    max_cost = r["max"]
    estimated = min_cost + int((max_cost - min_cost) * (severity_score % 20) / 20.0)
    estimated = max(min_cost, min(estimated, max_cost))

    return {
        "estimated_cost_inr": estimated,
        "cost_range_min_inr": min_cost,
        "cost_range_max_inr": max_cost,
        "time_required_hours": r["time_hours"],
        "priority": r["priority"],
        "currency": "INR",
        "currency_symbol": "₹",
    }

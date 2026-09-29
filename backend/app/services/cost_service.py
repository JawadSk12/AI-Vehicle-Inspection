from __future__ import annotations
from typing import Dict, Tuple

COST_RANGES: Dict[str, Tuple[float, float]] = {
    "Minor": (500.0, 1500.0), "Low": (1500.0, 3000.0),
    "Moderate": (3000.0, 6000.0), "High": (6000.0, 10000.0), "Critical": (10000.0, 18000.0),
}
TIME_REQUIRED = {"Minor":"2-4 hours","Low":"4-8 hours","Moderate":"1-2 days","High":"2-4 days","Critical":"5-7 days"}
PRIORITY = {"Minor":"Low","Low":"Medium","Moderate":"Medium","High":"High","Critical":"Urgent"}
RECOMMENDATIONS = {
    "Minor": "Minor surface scratches detected. Light polishing and waxing recommended. A professional detailer can restore the finish within a few hours.",
    "Low": "Low severity paint damage found. Touch-up paint and buffing recommended. Schedule a service appointment within the next 2-4 weeks.",
    "Moderate": "Moderate paint damage detected. Panel repainting may be required. Consult an auto body shop for a detailed quote.",
    "High": "High severity damage found. Multiple panels may require full repainting. Immediate inspection by a certified technician is strongly recommended.",
    "Critical": "Critical paint and structural damage detected. Immediate professional repair required. Do not delay - further exposure may accelerate corrosion.",
}
SCORE_RANGES = {"Minor":(0,20),"Low":(21,40),"Moderate":(41,60),"High":(61,80),"Critical":(81,100)}

def estimate_cost(severity_score: float, severity_label: str, defect_count: int) -> dict:
    label = severity_label if severity_label in COST_RANGES else "Moderate"
    cost_min, cost_max = COST_RANGES[label]
    low, high = SCORE_RANGES.get(label, (41, 60))
    ratio = (severity_score - low) / max(high - low, 1)
    estimated = cost_min + ratio * (cost_max - cost_min)
    estimated = min(estimated + defect_count * 150.0, cost_max * 1.1)
    return {
        "repair_cost_min": cost_min, "repair_cost_max": cost_max,
        "repair_cost_estimated": round(estimated, 2),
        "time_required": TIME_REQUIRED[label], "priority": PRIORITY[label],
        "recommendation": RECOMMENDATIONS[label],
    }

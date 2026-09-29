from __future__ import annotations
import os
from typing import Any, Dict, List
import cv2
import numpy as np

COLOURS = [(0,0,255),(0,165,255),(0,255,255),(255,0,0),(128,0,128),(0,255,0),(255,0,255),(0,128,255),(128,128,0)]

def draw_detections(image_path: str, detections: List[Dict[str, Any]], output_path: str) -> str:
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    for i, det in enumerate(detections):
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        cls_id = det.get("class_id", 0)
        colour = COLOURS[cls_id % len(COLOURS)]
        conf = det.get("confidence", 0.0)
        label = det.get("class_name", "defect").replace("_", " ").title()
        area_mm2 = det.get("area_mm2", 0.0)
        cv2.rectangle(img, (x1, y1), (x2, y2), colour, 2)
        text = f"#{i+1} {label} {conf:.0%} | {area_mm2:.1f}mm2"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        ly = max(y1 - 8, th + 4)
        cv2.rectangle(img, (x1, ly - th - 4), (x1 + tw + 4, ly + 2), colour, -1)
        cv2.putText(img, text, (x1 + 2, ly - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 1, cv2.LINE_AA)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img)
    return output_path

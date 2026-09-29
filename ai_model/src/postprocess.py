"""
CAPVIA AI - Post-Processing Pipeline
Provides Non-Maximum Suppression (NMS), confidence filtering,
bounding box visualization, and defect mask overlays.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional
import cv2
import numpy as np

COLOR_PALETTE = {
    "scratch": (0, 102, 255),         # Vibrant Orange-Red
    "hairline_scratch": (0, 165, 255),# Orange
    "deep_scratch": (0, 0, 255),      # Bright Red
    "paint_crack": (255, 51, 153),    # Magenta
    "paint_peel": (204, 0, 204),      # Purple
    "dirt_nib": (0, 204, 255),        # Yellow
    "orange_peel": (51, 204, 51),     # Bright Green
    "paint_run": (255, 153, 0),       # Cyan
    "fisheye": (0, 255, 255),         # Amber
    "dent": (255, 0, 102),            # Deep Rose
    "surface_damage": (128, 0, 255),  # Violet
}
DEFAULT_COLOR = (0, 140, 255)


def calculate_iou(box1: List[float], box2: List[float]) -> float:
    """Calculate Intersection over Union (IoU) between two xyxy boxes."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = area1 + area2 - inter_area
    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def apply_nms(
    boxes: List[List[int]],
    scores: List[float],
    iou_threshold: float = 0.45,
) -> List[int]:
    """
    Perform pure Python / NumPy Non-Maximum Suppression (NMS).
    Returns list of indices to keep.
    """
    if not boxes or not scores:
        return []

    indices = np.argsort(scores)[::-1]
    keep = []

    while len(indices) > 0:
        current = indices[0]
        keep.append(int(current))
        if len(indices) == 1:
            break

        current_box = boxes[current]
        remaining = indices[1:]
        ious = np.array([calculate_iou(current_box, boxes[idx]) for idx in remaining])
        indices = remaining[ious < iou_threshold]

    return keep


def filter_by_confidence(
    detections: List[Dict[str, Any]],
    min_confidence: float = 0.25,
) -> List[Dict[str, Any]]:
    """Filter detections that meet the minimum confidence threshold."""
    return [d for d in detections if d.get("confidence", 0.0) >= min_confidence]


def draw_bounding_boxes(
    image: np.ndarray,
    detections: List[Dict[str, Any]],
    output_path: Optional[str] = None,
) -> np.ndarray:
    """
    Render enterprise-grade bounding boxes, labels, and confidence badges on image.
    """
    annotated = image.copy()
    h, w = annotated.shape[:2]

    for det in detections:
        if det.get("is_glare", False):
            continue
        bbox = det.get("bbox", [0, 0, 0, 0])
        x1, y1, x2, y2 = [int(v) for v in bbox]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        cls_name = det.get("class_name", "defect").lower()
        conf = det.get("confidence", 0.0)
        color = COLOR_PALETTE.get(cls_name, DEFAULT_COLOR)

        # Draw main rectangle with thickness 2
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)

        # Draw corner accents for premium look
        corner_len = max(8, min(int((x2 - x1) * 0.15), 24))
        # Top-left
        cv2.line(annotated, (x1, y1), (x1 + corner_len, y1), color, 3, cv2.LINE_AA)
        cv2.line(annotated, (x1, y1), (x1, y1 + corner_len), color, 3, cv2.LINE_AA)
        # Top-right
        cv2.line(annotated, (x2, y1), (x2 - corner_len, y1), color, 3, cv2.LINE_AA)
        cv2.line(annotated, (x2, y1), (x2, y1 + corner_len), color, 3, cv2.LINE_AA)
        # Bottom-left
        cv2.line(annotated, (x1, y2), (x1 + corner_len, y2), color, 3, cv2.LINE_AA)
        cv2.line(annotated, (x1, y2), (x1, y2 - corner_len), color, 3, cv2.LINE_AA)
        # Bottom-right
        cv2.line(annotated, (x2, y2), (x2 - corner_len, y2), color, 3, cv2.LINE_AA)
        cv2.line(annotated, (x2, y2), (x2, y2 - corner_len), color, 3, cv2.LINE_AA)

        # Label badge
        label = f"{cls_name.replace('_', ' ').title()} {conf:.0%}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.52
        thickness = 1
        (txt_w, txt_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)

        badge_y1 = max(0, y1 - txt_h - baseline - 6)
        badge_y2 = y1
        badge_x1 = x1
        badge_x2 = min(w, x1 + txt_w + 10)

        # Semi-transparent dark background for badge
        overlay = annotated.copy()
        cv2.rectangle(overlay, (badge_x1, badge_y1), (badge_x2, badge_y2), (18, 18, 24), -1)
        cv2.addWeighted(overlay, 0.85, annotated, 0.15, 0, annotated)

        # Indicator tag
        cv2.rectangle(annotated, (badge_x1, badge_y1), (badge_x1 + 4, badge_y2), color, -1)
        cv2.putText(
            annotated,
            label,
            (badge_x1 + 8, badge_y2 - baseline - 2),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA,
        )

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(output_path, annotated)

    return annotated


def draw_defect_mask(
    image: np.ndarray,
    detections: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    alpha: float = 0.45,
) -> np.ndarray:
    """
    Overlay semi-transparent defect masks and segmentation polygons on the image.
    """
    overlay = image.copy()
    for det in detections:
        if det.get("is_glare", False):
            continue
        cls_name = det.get("class_name", "defect").lower()
        color = COLOR_PALETTE.get(cls_name, DEFAULT_COLOR)

        # If polygon points provided
        polygon = det.get("polygon")
        if polygon and len(polygon) >= 3:
            pts = np.array(polygon, np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(overlay, [pts], color)
            cv2.polylines(overlay, [pts], True, (255, 255, 255), 1, cv2.LINE_AA)
        else:
            # Fallback to filled rounded rect on bbox
            bbox = det.get("bbox", [0, 0, 0, 0])
            x1, y1, x2, y2 = [int(v) for v in bbox]
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)

    result = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(output_path, result)
    return result

from __future__ import annotations
from app.config import settings

def get_scale_factor(image_dpi: float = None, camera_distance_mm: float = None, focal_length_mm: float = None, sensor_width_mm: float = None, image_width_px: int = None) -> float:
    if all(v is not None for v in [camera_distance_mm, focal_length_mm, sensor_width_mm, image_width_px]):
        fov_mm = (sensor_width_mm * camera_distance_mm) / focal_length_mm
        return round(fov_mm / image_width_px, 6)
    if image_dpi and image_dpi > 0:
        return round((1.0 / image_dpi) * 25.4, 6)
    return settings.default_scale_factor

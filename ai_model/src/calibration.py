"""
CAPVIA AI - Dynamic Calibration Module
Converts image pixels to real-world metric dimensions (mm/px) dynamically.
Supports:
1. Calibration Marker (ArUco or checkerboard or reference circle)
2. Camera Distance & Sensor Focal Length
3. Image DPI / Metadata EXIF
4. Manual Calibration input
"""
from __future__ import annotations
from typing import Optional, Tuple
import math


class CalibrationEngine:
    """
    Computes scale factor (millimeters per pixel) for high-precision vehicle defect measurement.
    """

    def __init__(self, default_scale: float = 0.05):
        self.default_scale = default_scale  # 1 px = 0.05 mm (20 px = 1 mm)

    def from_dpi(self, dpi: float) -> float:
        """
        Convert DPI (dots per inch) to mm/pixel.
        1 inch = 25.4 mm.
        scale_factor = 25.4 / DPI.
        """
        if dpi <= 0:
            return self.default_scale
        return round(25.4 / dpi, 6)

    def from_camera_distance(
        self,
        distance_cm: float,
        sensor_focal_length_mm: float = 4.25,
        sensor_width_mm: float = 5.76,
        image_width_px: int = 1920,
    ) -> float:
        """
        Compute mm per pixel using pinhole camera projection:
        Field of View (width in mm) = (distance_mm * sensor_width_mm) / focal_length_mm
        mm_per_pixel = FOV_width_mm / image_width_px
        """
        if distance_cm <= 0 or sensor_focal_length_mm <= 0 or image_width_px <= 0:
            return self.default_scale

        distance_mm = distance_cm * 10.0
        fov_width_mm = (distance_mm * sensor_width_mm) / sensor_focal_length_mm
        scale = fov_width_mm / image_width_px
        return round(scale, 6)

    def from_reference_marker(
        self,
        marker_pixel_dimension: float,
        real_world_marker_mm: float = 25.0,
    ) -> float:
        """
        Compute scale from a known fiducial marker (e.g. 25mm adhesive inspection coin/dot).
        """
        if marker_pixel_dimension <= 0 or real_world_marker_mm <= 0:
            return self.default_scale
        return round(real_world_marker_mm / marker_pixel_dimension, 6)

    def from_manual(self, scale_factor_mm_per_pixel: float) -> float:
        """Explicitly set millimeter per pixel scale factor."""
        if scale_factor_mm_per_pixel <= 0:
            return self.default_scale
        return round(scale_factor_mm_per_pixel, 6)


_engine = CalibrationEngine()


def get_scale_factor(
    mode: str = "default",
    value: Optional[float] = None,
    distance_cm: Optional[float] = None,
    image_width_px: int = 1920,
) -> float:
    """
    Helper function to retrieve calibrated scale factor.
    Modes: 'dpi', 'distance', 'marker', 'manual', 'default'
    """
    if mode == "dpi" and value is not None:
        return _engine.from_dpi(value)
    elif mode == "distance" and distance_cm is not None:
        return _engine.from_camera_distance(distance_cm, image_width_px=image_width_px)
    elif mode == "marker" and value is not None:
        return _engine.from_reference_marker(value)
    elif mode == "manual" and value is not None:
        return _engine.from_manual(value)
    return _engine.default_scale

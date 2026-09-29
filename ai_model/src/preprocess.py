"""
CAPVIA AI - Modular Image Preprocessing Pipeline
Provides CLAHE, Gamma Correction, Letterbox Resize, and Normalization for RT-DETR.
"""
from __future__ import annotations
from typing import Any, Dict, Tuple
import cv2
import numpy as np


def apply_clahe(
    image: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8),
) -> np.ndarray:
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE)
    to enhance micro-contrast on metallic and glossy car paint surfaces.
    """
    if len(image.shape) == 3 and image.shape[2] == 3:
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        l_clahe = clahe.apply(l)
        lab_clahe = cv2.merge((l_clahe, a, b))
        return cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)
    elif len(image.shape) == 2:
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(image)
    return image


def adjust_gamma(image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
    """
    Apply gamma correction to handle overexposed highlights or shadowed body panels.
    gamma < 1.0 brightens shadows, gamma > 1.0 compresses bright reflections.
    """
    if gamma == 1.0:
        return image
    inv_gamma = 1.0 / max(gamma, 1e-5)
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(image, table)


def letterbox_resize(
    image: np.ndarray,
    target_size: int = 1024,
    color: Tuple[int, int, int] = (114, 114, 114),
) -> Tuple[np.ndarray, float, Tuple[int, int]]:
    """
    Resize image with padding to maintain aspect ratio for RT-DETR input.
    Returns: (padded_image, scale_ratio, (pad_left, pad_top))
    """
    h, w = image.shape[:2]
    scale = min(target_size / h, target_size / w)
    new_w, new_h = int(round(w * scale)), int(round(h * scale))
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    pad_w = target_size - new_w
    pad_h = target_size - new_h
    top = pad_h // 2
    bottom = pad_h - top
    left = pad_w // 2
    right = pad_w - left

    padded = cv2.copyMakeBorder(
        resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )
    return padded, scale, (left, top)


def normalize_image(
    image: np.ndarray,
    mean: Tuple[float, float, float] = (0.485, 0.456, 0.406),
    std: Tuple[float, float, float] = (0.229, 0.224, 0.225),
) -> np.ndarray:
    """
    Convert BGR uint8 image to float32 RGB normalized tensor array (C, H, W).
    """
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    for i in range(3):
        rgb[:, :, i] = (rgb[:, :, i] - mean[i]) / std[i]
    # Transpose to (C, H, W)
    return np.transpose(rgb, (2, 0, 1))


def preprocess_pipeline(
    image: np.ndarray,
    target_size: int = 1024,
    enable_clahe: bool = True,
    gamma: float = 1.0,
) -> Dict[str, Any]:
    """
    Full preprocessing execution pipeline.
    """
    img_processed = image.copy()
    if gamma != 1.0:
        img_processed = adjust_gamma(img_processed, gamma)
    if enable_clahe:
        img_processed = apply_clahe(img_processed)

    padded, scale, (pad_x, pad_y) = letterbox_resize(img_processed, target_size)
    normalized = normalize_image(padded)

    return {
        "processed_image": padded,
        "normalized_tensor": normalized,
        "scale": scale,
        "pad_offsets": (pad_x, pad_y),
        "original_shape": image.shape[:2],
    }

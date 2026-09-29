from __future__ import annotations
import sys; sys.path.insert(0, "backend")
import numpy as np
from app.utils.glare_filter import compute_glare_score

def test_bright_white_region_is_glare():
    img = np.ones((200,200,3), dtype=np.uint8) * 255
    result = compute_glare_score(img, [0,0,200,200])
    assert result["is_glare"] is True

def test_dark_textured_not_glare():
    np.random.seed(42)
    img = np.random.randint(30, 80, (200,200,3), dtype=np.uint8)
    result = compute_glare_score(img, [0,0,200,200])
    assert result["is_glare"] is False

def test_empty_roi():
    img = np.zeros((100,100,3), dtype=np.uint8)
    result = compute_glare_score(img, [50,50,50,50])
    assert result["is_glare"] is False and result["glare_score"] == 0.0

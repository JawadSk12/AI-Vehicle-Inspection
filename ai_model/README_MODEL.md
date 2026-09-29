# Paint Defect AI - Model Architecture & Inference Specification

## 1. Overview
The Paint Defect AI artificial intelligence pipeline operates on a dual-stage vision architecture engineered specifically for industrial automobile paint defect inspection:

```
Input Vehicle Image
        │
        ▼
   Preprocessing (CLAHE, Letterbox 1024, Gamma Normalization)
        │
        ▼
Model A: Vehicle Panel Detection (Hood, Front Door, Rear Door, Fender, Bumper, Roof, Trunk)
        │
        ▼
Model B: Paint Defect Detection (RT-DETR v2-L Real-Time Detection Transformer)
        │
        ▼
   SAM 2.1 (Segment Anything 2 Prompted Pixel Segmentation)
        │
        ▼
   Glare & False Positive Rejection Filter (Morphological + Texture + Saturation)
        │
        ▼
   Measurement Engine (Pixel-to-Metric mm² Area, Length, Width, Centroid)
        │
        ▼
   Severity Scoring (0–100 Multi-Factor Analysis)
        │
        ▼
   Repair Cost Estimation Engine (INR - Indian Rupees ₹)
```

---

## 2. Model A: Vehicle Panel Detection
- **Purpose**: Classifies vehicle body panels and extracts Region of Interest (ROI) coordinates.
- **Panels Detected**:
  - `Hood`
  - `Front Door` (Left & Right)
  - `Rear Door` (Left & Right)
  - `Fender` (Front & Rear)
  - `Bumper` (Front & Rear)
  - `Roof`
  - `Trunk / Tailgate`
- **Output**: Panel bounding boxes, panel classification, and panel critical weight multipliers for the severity score.

---

## 3. Model B: Paint Defect Detection (RT-DETR v2-L)
- **Base Architecture**: RT-DETR v2 Large (Real-Time DEtection TRansformer).
- **Backbone**: Hybrid Encoder with intra-scale interaction and cross-scale fusion.
- **Decoder**: Transformer decoder with deformable attention and query refinement.
- **Resolution**: 1024 × 1024 px.
- **Supported Defect Classes**:
  1. `scratch`
  2. `hairline_scratch`
  3. `deep_scratch`
  4. `paint_crack`
  5. `paint_peel`
  6. `dirt_nib`
  7. `orange_peel`
  8. `paint_run`
  9. `fisheye`

---

## 4. SAM 2.1: Prompt-Driven Defect Segmentation
RT-DETR v2 provides localized bounding box prompts. SAM 2.1 takes these coordinates as point/box prompts to output pixel-level polygon masks:
- Eliminates bounding box background bias.
- Resolves micro-scratches with sub-millimeter edge precision.
- Output: Binary mask PNG, contour coordinate arrays, polygon area in $mm^2$.

---

## 5. Glare & Specular Reflection Filter
Vehicle paint possesses high specular reflectivity under direct garage lighting, LED inspection lamps, and sunlight:
- **Brightness Map**: Evaluates V/L channel overexposure ($V \ge 240$).
- **Color Desaturation**: Glares exhibit near-zero chroma ($S \le 45$).
- **Morphological Gradient**: Detects bloom and uniform light spread vs sharp directional scratches.
- **Threshold**: Rejects detections scoring $\ge 0.48$ glare probability.

---

## 6. Directory Layout (`ai_model/src/`)

| File | Purpose |
|---|---|
| `predict.py` | Primary backend entrypoint (`predict_image`). Handles model cache and fallback. |
| `preprocess.py` | Contrast Limited Adaptive Histogram Equalization (CLAHE), gamma, letterbox. |
| `postprocess.py` | Non-Maximum Suppression (NMS), confidence filtering, annotation drawing. |
| `measure.py` | Geometric computation of length, width, area, centroid, metric conversion. |
| `severity.py` | 0–100 severity index formulation, recommendations, and INR cost calculation. |
| `glare_filter.py` | Reflection filter to eliminate false positives from ambient light. |
| `calibration.py` | Dynamic scale factor ($mm/pixel$) from DPI, camera distance, or markers. |
| `export.py` | Export PyTorch `.pt` to ONNX and TorchScript. |

---

## 7. Model Weights System (`ai_model/weights/`)
- Target weights file: `ai_model/weights/best.pt`
- When present: The application loads the trained PyTorch / RT-DETR model with CUDA acceleration.
- When absent: The application logs `"Model not trained. Please place best.pt inside ai_model/weights."` and uses a deterministic fallback, ensuring backend APIs, frontend, and tests never crash.
- ONNX export: `ai_model/weights/best.onnx` can be placed here for CPU/edge optimization.

---

## 8. Integration with Backend
The backend imports **strictly from `ai_model.src.predict`**:
```python
from ai_model.src.predict import predict_image

detections = predict_image(image_path="storage/uploads/inspection.jpg")
```
No training logic or dataset dependencies exist within the backend.

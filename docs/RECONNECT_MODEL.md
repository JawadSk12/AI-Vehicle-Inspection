# 🔄 Model Reconnection Guide: Google Colab to Paint Defect AI Web Application

This document provides step-by-step instructions on connecting the model trained on Google Colab back into the Paint Defect AI platform.

---

## 🏛️ System Boundary & The Single Point of Connection

Paint Defect AI enforces a strict, decoupled boundary between cloud model training and on-premise/local web inference:

```
┌───────────────────────────────────────────────────────────┐
│              PART B: GOOGLE COLAB TRAINING                │
│  [ai_model.zip] ──> RT-DETR v2-L GPU ──> Validation mAP   │
│                                              │            │
│                       Produces               ▼            │
│              [TRAINED_MODEL.zip]                   │
└─────────────────────────────┬─────────────────────────────┘
                              │
                    DOWNLOAD & EXTRACT
                              │
┌─────────────────────────────▼─────────────────────────────┐
│              THE ONLY POINT OF CONNECTION                 │
│               ai_model/weights/best.pt                    │
└─────────────────────────────┬─────────────────────────────┘
                              │
                    AUTOMATIC DETECTION
                              │
┌─────────────────────────────▼─────────────────────────────┐
│             PART A: Paint Defect AI WEB APPLICATION                │
│                                                           │
│   FastAPI Backend                 React Dashboard         │
│   ┌─────────────────────┐         ┌─────────────────────┐ │
│   │ POST /api/predict   │◄────────┤ Upload Vehicle Img  │ │
│   │  - RT-DETR v2 Infer │         │  - Real-time Visual │ │
│   │  - Glare Rejection  │────────►│  - Severity Meter   │ │
│   │  - Measurement (mm) │         │  - INR Repair Cost  │ │
│   │  - PDF Report Gen   │         │  - Defect Map       │ │
│   └─────────────────────┘         └─────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

---

## 📋 Step-by-Step Reconnection Procedure

### Step 1: Download Model from Colab
When training finishes in `colab/train_colab.ipynb`, Google Colab automatically triggers the download of:
```
TRAINED_MODEL.zip
```
*(If the download popup is blocked by your browser, check the files sidebar in Google Colab on the left, right-click `TRAINED_MODEL.zip`, and click **Download**).*

```
┌───────────────────────────────────────────────────────────┐
│ [Screenshot Placeholder: Google Colab Download Completed]  │
│ Showing TRAINED_MODEL.zip ready in browser tray   │
└───────────────────────────────────────────────────────────┘
```

---

### Step 2: Extract the ZIP Archive
Extract `TRAINED_MODEL.zip` on your computer. Inside you will find:
```
TRAINED_MODEL/
├── best.pt                  <-- Primary PyTorch RT-DETR model weights
├── best.onnx                <-- Optimized ONNX format for edge/CPU inference
├── training_metrics.json    <-- Final mAP50, mAP50-95, precision, and recall scores
├── loss_curve.png           <-- Bounding box loss and class loss curves
├── confusion_matrix.png     <-- Class prediction accuracy matrix
└── pr_curve.png             <-- Precision-Recall evaluation curve
```

---

### Step 3: Copy `best.pt` into `ai_model/weights/`

Copy the extracted `best.pt` directly into the `ai_model/weights/` folder of your Paint Defect AI project:

#### Windows (PowerShell):
```powershell
Copy-Item "C:\Users\<YourUser>\Downloads\TRAINED_MODEL\best.pt" -Destination "ai_model\weights\best.pt" -Force
```

#### Windows (Command Prompt):
```cmd
copy "C:\Users\%USERNAME%\Downloads\TRAINED_MODEL\best.pt" "ai_model\weights\best.pt"
```

#### macOS / Linux:
```bash
cp ~/Downloads/TRAINED_MODEL/best.pt ai_model/weights/best.pt
```

*(Optional)* If you plan to run ONNX inference on CPU, also copy `best.onnx`:
```powershell
Copy-Item "C:\Users\<YourUser>\Downloads\TRAINED_MODEL\best.onnx" -Destination "ai_model\weights\best.onnx" -Force
```

---

### Step 4: Run or Restart the Backend
Run your backend service using your preferred environment:

#### Option 1: Native Python
```powershell
# From project root
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

#### Option 2: Docker Compose
```powershell
docker compose up --build
```

---

### Step 5: Automatic Detection Verification

As soon as the backend initializes, check your terminal logs. You will observe:
```log
INFO: Loading RT-DETR v2 from ai_model/weights/best.pt on cuda:0...
INFO: RT-DETR model successfully loaded into memory.
INFO: Application startup complete. Uvicorn running on http://0.0.0.0:8000
```

If `best.pt` is missing or in the wrong directory, the backend logs:
```log
WARNING: Model not trained. Please place best.pt inside ai_model/weights.
INFO: Running with safe default detections...
```
*(The server will never crash if the weights are absent; it will gracefully instruct you to place `best.pt` in `ai_model/weights/`)*.

```
┌───────────────────────────────────────────────────────────┐
│ [Screenshot Placeholder: Terminal Startup Log]            │
│ Showing RT-DETR v2 loaded into memory from best.pt        │
└───────────────────────────────────────────────────────────┘
```

---

### Step 6: Verify Live Predictions on Dashboard

1. Open your browser to the Paint Defect AI Frontend: **`http://localhost:5173`** (or `http://localhost:3000`).
2. Log in with your credentials.
3. Click **New Inspection** from the sidebar.
4. Enter vehicle details:
   - Vehicle Number: `MH-12-AB-1234`
   - Vehicle Model: `Tata Harrier Dark Edition`
   - Owner Name: `John Doe`
   - Inspector Name: `A. Sharma`
5. Drag and drop a vehicle inspection photo and click **Analyze Inspection**.
6. Inspect the results page:
   - **Bounding Boxes**: Scratches, cracks, or paint peel identified with confidence scores.
   - **Measurements**: Real-world length, width, and surface area in $mm^2$.
   - **Severity Rating**: Dynamic score (0–100) and severity category.
   - **Repair Estimation**: Itemized cost breakdown in Indian Rupees (**₹ INR**).
   - **Download PDF**: Complete professional A4 inspection certificate with QR verification.

```
┌───────────────────────────────────────────────────────────┐
│ [Screenshot Placeholder: Inspection Result Page]          │
│ Side-by-side comparison: Original Photo vs Annotated BBoxes│
│ with Defect Metric Cards and ₹ INR Repair Cost             │
└───────────────────────────────────────────────────────────┘
```

---

## 🔍 Troubleshooting Checklist

| Symptom | Cause | Solution |
|---|---|---|
| Warning: `Model not trained. Please place best.pt inside ai_model/weights.` | `best.pt` is named differently or placed in the wrong directory | Ensure the file is at exactly `ai_model/weights/best.pt` (all lowercase extension). |
| Out of CUDA memory error on local machine | GPU has insufficient VRAM | RT-DETR automatically falls back to CPU if CUDA is exhausted, or set `device="cpu"` in config. |
| Inaccurate measurements (mm) | Camera distance or DPI mismatch | Adjust the calibration scale factor via `ai_model/src/calibration.py` or provide distance in cm. |
| Permission Denied copying file in Docker | Volume mount mismatch | Check that `docker-compose.yml` mounts `- ./ai_model/weights:/app/ai_model/weights`. |

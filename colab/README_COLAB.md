# 🚗 Paint Defect AI - Google Colab Training Guide

This guide details the complete, step-by-step workflow for training **RT-DETR v2-L** on Google Colab GPU and exporting the trained model back to your local Paint Defect AI web application.

---

## 📋 Overview of the Isolated Architecture

```
PART A: Local Machine (Paint Defect AI Web Application)
  ├── 1. Run: python colab/prepare_dataset.py  ──> Generates: ai_model.zip
  └── 2. Keep frontend/backend running in inference mode

PART B: Google Colab (GPU Cloud Training)
  ├── 1. Upload: colab/train_colab.ipynb & ai_model.zip
  ├── 2. Train RT-DETR v2-L (1024px, AdamW, Cosine Annealing, 150 epochs)
  ├── 3. Validate (mAP@50, mAP@50-95, Precision, Recall)
  ├── 4. Export: best.pt + best.onnx + loss_curve.png
  └── 5. Auto-Download: TRAINED_MODEL.zip

RECONNECTION:
  └── Copy best.pt into ai_model/weights/best.pt ──> Production inference active!
```

---

## 🛠️ Step-by-Step Instructions

### Step 1: Package Your Dataset Locally
On your local machine, run the automated dataset packaging script from the project root:
```bash
python colab/prepare_dataset.py
```
This inspects `ai_model/dataset/` and creates `ai_model.zip` containing:
- `dataset/data.yaml`
- `dataset/train/` (`images/` and `labels/`)
- `dataset/valid/` (`images/` and `labels/`)
- `dataset/test/` (`images/` and `labels/`)

---

### Step 2: Open Google Colab
1. Navigate to [Google Colab](https://colab.research.google.com/).
2. Click **File > Upload notebook** and select `colab/train_colab.ipynb` from this project.
3. Switch runtime to GPU:
   - Click **Runtime > Change runtime type**
   - Under **Hardware accelerator**, select **T4 GPU** (or V100/A100 if you have Colab Pro)
   - Click **Save**

---

### Step 3: Run the Training Notebook
Execute each cell sequentially in `train_colab.ipynb`:

1. **Step 1 (GPU Check)**:
   Confirms NVIDIA CUDA is detected and displays VRAM (e.g. 15.0 GB on T4).
2. **Step 2 (Install Dependencies)**:
   Installs `ultralytics`, `albumentations`, `onnx`, `pyyaml`, `matplotlib`, and dependencies.
3. **Step 3 (Upload Dataset)**:
   Prompts you to select `ai_model.zip`. Colab automatically unzips it, locates `data.yaml`, and prepares the split paths.
4. **Step 4 (Train Model)**:
   Initializes `RT-DETR v2-L` (Large) with 1024px input size, AdamW optimizer (learning rate 1e-4), Cosine Annealing scheduler, and automatic mixed precision (FP16).
5. **Step 5 (Validation)**:
   Evaluates against the held-out test split, displaying mAP50, mAP50-95, precision, and recall.
6. **Step 6 (Export & Package)**:
   Exports the model to ONNX (`best.onnx`), compiles metric curves (`loss_curve.png`, `confusion_matrix.png`, `pr_curve.png`), writes `training_metrics.json`, and bundles everything into `TRAINED_MODEL.zip`.
7. **Step 7 (Download)**:
   Colab automatically triggers a browser download of `TRAINED_MODEL.zip`.

---

### Step 4: Reconnect to Local Application
Once `TRAINED_MODEL.zip` finishes downloading:
1. Extract `TRAINED_MODEL.zip` on your computer.
2. Copy `best.pt` into your project's `ai_model/weights/` folder:
   ```powershell
   Copy-Item "path\to\extracted\best.pt" "ai_model\weights\best.pt"
   ```
3. (Optional) Copy `best.onnx` into `ai_model/weights/best.onnx` for edge/CPU inference.
4. Start your Paint Defect AI backend or refresh:
   The backend immediately detects `ai_model/weights/best.pt` and switches from fallback mode to live RT-DETR v2 inference!

For more details on verifying the model reconnection, see [docs/RECONNECT_MODEL.md](../docs/RECONNECT_MODEL.md).

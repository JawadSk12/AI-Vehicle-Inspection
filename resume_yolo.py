import torch
from ultralytics import YOLO

# 1. Load your best trained checkpoint from the previous 50 epochs
checkpoint = r"runs/detect/car_scratches_model-2/weights/best.pt"
print(f"[INFO] Loading trained weights from: {checkpoint}")
model = YOLO(checkpoint)

# 2. Select device (GPU if available, else CPU)
device = "0" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Training on device: {device}")

# 3. Train for additional epochs (e.g. 25 more epochs)
model.train(
    data=r"car-scratches-1/data.yaml",
    epochs=25,
    imgsz=640,
    batch=4 if device == "cpu" else 16,
    device=device,
    amp=(device != "cpu"),
    workers=2 if device == "cpu" else 8,
    plots=False,
    name="car_scratches_continued"
)

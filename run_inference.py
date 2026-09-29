import os
import cv2
import numpy as np
from ultralytics import YOLO

# 1. Path to your fine-tuned segmentation model weights
MODEL_PATH = "runs/segment/car_scratches_model/weights/best.pt"

# 2. Optical Scale Factor: 1 pixel = 0.05 mm
SCALE_FACTOR_MM_PER_PIX = 0.05

def analyze_paint_defects(image_path):
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model file not found at: {MODEL_PATH}")
        print("[INFO] Ensure train.py has completed training with 'yolov8s-seg.pt'.")
        return

    if not os.path.exists(image_path):
        print(f"[ERROR] Test image not found at: {image_path}")
        return

    # Load model and run inference on GPU
    model = YOLO(MODEL_PATH)
    results = model.predict(source=image_path, conf=0.25, save=True, device=0)
    
    for result in results:
        boxes = result.boxes
        masks = result.masks  # Segmentation mask objects
        
        if masks is None or len(masks) == 0:
            print("[INFO] No paint defects detected. Surface PASS.")
            return

        print(f"\n[INFO] Detected {len(masks)} defect(s):")
        
        # Extract full-resolution polygon contours
        for i, polygon in enumerate(masks.xy):
            cls_id = int(boxes[i].cls[0])
            class_name = model.names[cls_id]
            confidence = float(boxes[i].conf[0])
            
            # Calculate pixel area from polygon coordinates
            pixel_area = cv2.contourArea(polygon.astype(np.float32))
            
            # Convert pixel area to physical surface area (mm²)
            physical_area_mm2 = pixel_area * (SCALE_FACTOR_MM_PER_PIX ** 2)
            
            print(f"  └─ Defect #{i+1}: [{class_name.upper()}] | "
                  f"Confidence: {confidence:.2f} | "
                  f"Area: {physical_area_mm2:.3f} mm²")

if __name__ == "__main__":
    # Specify your target test image
    test_image_path = "car-scratches-1/test/images/sample_panel.jpg"
    analyze_paint_defects(test_image_path)
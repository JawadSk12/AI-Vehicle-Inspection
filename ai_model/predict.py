"""
CAPVIA AI - Standalone Inference Script
Usage: python ai_model/predict.py --image path/to/image.jpg
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import cv2

def predict(image_path: str, weights: str, conf: float = 0.25, save: bool = True) -> list:
    try:
        from ultralytics import RTDETR
    except ImportError:
        print("ERROR: Install ultralytics - pip install ultralytics")
        sys.exit(1)
    model = RTDETR(weights)
    results = model.predict(source=image_path, conf=conf, save=save, verbose=True)
    detections = []
    for result in results:
        img = cv2.imread(image_path)
        h, w = img.shape[:2]
        if result.boxes is None:
            continue
        for box in result.boxes:
            cls_id = int(box.cls[0])
            detections.append({"class_id":cls_id,"class_name":result.names[cls_id],"confidence":round(float(box.conf[0]),4),"bbox":[round(v) for v in box.xyxy[0].tolist()],"image_width":w,"image_height":h})
    print(json.dumps(detections, indent=2))
    return detections

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--image",   required=True)
    p.add_argument("--weights", default="ai_model/weights/best_rtdetr.pt")
    p.add_argument("--conf",    type=float, default=0.25)
    p.add_argument("--no-save", dest="save", action="store_false")
    args = p.parse_args()
    predict(args.image, args.weights, args.conf, args.save)

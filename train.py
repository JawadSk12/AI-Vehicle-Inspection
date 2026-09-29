import os
from roboflow import Roboflow
from ultralytics import YOLO

def download_and_train():
    # 1. Initialize Roboflow with your credentials
    rf = Roboflow(api_key="KnktCPHdeG8ZUbjohQGM")
    project = rf.workspace("vedd-brxwm").project("car-scratches-cwghg")
    version = project.version(1)
    dataset = version.download("yolov8")

    # 2. Load standard YOLOv8 detection model (yolov8s.pt)
    model = YOLO("yolov8s.pt")
    

    # 3. Locate data.yaml from the downloaded dataset
    data_yaml_path = os.path.join(dataset.location, "data.yaml")

    # 4. Start training on GPU
    print("[INFO] Starting training on GPU...")
    model.train(
        data=data_yaml_path,
        epochs=50,
        imgsz=640,
        batch=16,
        device=0,
        name="car_scratches_model",
        amp=False  # <--- Add this line to bypass the asset download check
    )

if __name__ == "__main__":
    download_and_train()
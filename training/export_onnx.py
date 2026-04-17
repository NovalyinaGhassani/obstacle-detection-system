from ultralytics import YOLO
import os

# Path model hasil training
MODEL_PATH = os.path.join("runs", "train", "yolov8n_optimized", "weights", "best.pt")

if not os.path.exists(MODEL_PATH):
    print("Model tidak ditemukan, lakukan training")
    exit()

# Load model
model = YOLO(MODEL_PATH)

# Export ke ONNX (optimized untuk CPU / Raspberry Pi)
model.export(
    format="onnx",
    imgsz=320,
    dynamic=True,
    simplify=True,
    device="cpu"
)

print("Export ONNX selesai")
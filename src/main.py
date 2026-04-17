import cv2
import time
import numpy as np
import onnxruntime as ort
import os
import argparse

# ================= GPIO (AUTO DETECT RASPBERRY PI) =================
try:
    import RPi.GPIO as GPIO
    RPI = True
except:
    print("Running in simulation mode (no GPIO)")
    RPI = False

LED_PIN = 12

if RPI:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)

# ================= MODEL =================
model_path = "models/best.onnx"
session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])

input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# ================= CONFIG =================
IMG_WIDTH, IMG_HEIGHT = 320, 320
VIDEO_WIDTH, VIDEO_HEIGHT = 512, 300

label_dict = {
    0: 'kapal cargo',
    1: 'kapal ikan tradisional',
    2: 'kapal keruk pasir',
    3: 'kapal tugboat',
}

kapal_kecil = ['kapal tugboat', 'kapal ikan tradisional']
kapal_besar = ['kapal keruk pasir', 'kapal cargo']

threshold_kapal_kecil = 2113
threshold_kapal_besar = 11061
confidence_threshold = 0.7

# ================= INPUT SOURCE =================
parser = argparse.ArgumentParser()
parser.add_argument("--source", type=str, default="webcam",
                    help="webcam atau path ke video file")
args = parser.parse_args()

if args.source == "webcam":
    cap = cv2.VideoCapture(0)
else:
    cap = cv2.VideoCapture(args.source)

# Safety check
if not cap.isOpened():
    print("Error: tidak bisa buka source")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)

# ================= FOLDER =================
BASE_OUTPUT_DIR = "outputs"

# buat folder utama kalau belum ada
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# folder per session (timestamp)
folder_name = os.path.join(BASE_OUTPUT_DIR, time.strftime("%Y%m%d-%H%M%S", time.localtime()))
os.makedirs(folder_name, exist_ok=True)

# ================= PREPROCESS =================
def preprocess_frame(frame):
    frame_resized = cv2.resize(frame, (IMG_WIDTH, IMG_HEIGHT))
    frame_preprocessed = frame_resized.astype(np.float32) / 255.0
    frame_preprocessed = frame_preprocessed.transpose(2, 0, 1)
    return np.expand_dims(frame_preprocessed, axis=0)

# ================= MAIN =================
def main():
    frame_count = 0
    start_time = time.perf_counter()
    avg_fps = 0
    last_capture_time = 0
    cooldown = 2  # detik
    MAX_CAPTURES = 50
    capture_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (VIDEO_WIDTH, VIDEO_HEIGHT))
        input_tensor = preprocess_frame(frame)

        outputs = session.run([output_name], {input_name: input_tensor})[0]

        if len(outputs.shape) > 2:
            outputs = np.squeeze(outputs)

        height, width, _ = frame.shape
        danger_detected = False

        for det in outputs:
            x1, y1, x2, y2, conf, class_id = det

            if conf < confidence_threshold:
                continue

            x1 = int(x1 * width / IMG_WIDTH)
            y1 = int(y1 * height / IMG_HEIGHT)
            x2 = int(x2 * width / IMG_WIDTH)
            y2 = int(y2 * height / IMG_HEIGHT)

            class_id = int(class_id)
            label = label_dict.get(class_id, "Unknown")
            label_clean = label.replace(" ", "_")

            area = (x2 - x1) * (y2 - y1)
            color = (0, 255, 0)
            warning = ""

            if label in kapal_kecil and area > threshold_kapal_kecil:
                color = (0, 0, 255)
                warning = "PERINGATAN BAHAYA"
                danger_detected = True

            elif label in kapal_besar and area > threshold_kapal_besar:
                color = (0, 0, 255)
                warning = "PERINGATAN BAHAYA"
                danger_detected = True

            # DRAW
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label}: {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            if warning:
                cv2.putText(frame, warning, (x1, y2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # ================= ACTION =================
        current_time = time.perf_counter()

        if danger_detected:
            if RPI:
                GPIO.output(LED_PIN, GPIO.HIGH)
            else:
                print("⚠️ WARNING: LED ON (simulated)")

            # Capture danger (cooldown)
            if current_time - last_capture_time > cooldown and capture_count < MAX_CAPTURES:
                filename = os.path.join(folder_name, f"danger_{int(current_time*1000)}.jpg")
                small_frame = cv2.resize(frame, (320, 240))  # optional biar ringan
                cv2.imwrite(filename, small_frame)
                
                print(f"Captured: {filename}")
                
                last_capture_time = current_time
                capture_count += 1

        else:
            if RPI:
                GPIO.output(LED_PIN, GPIO.LOW)

        # ================= FPS =================
        frame_count += 1
        elapsed_time = time.perf_counter() - start_time

        if elapsed_time >= 1.0:
            avg_fps = frame_count / elapsed_time
            frame_count = 0
            start_time = time.perf_counter()

        cv2.putText(frame, f"Captures: {capture_count}/{MAX_CAPTURES}", (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        # ================= DISPLAY =================
        cv2.imshow("Obstacle Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()

    if RPI:
        GPIO.cleanup()

    cv2.destroyAllWindows()

# ================= RUN =================
if __name__ == "__main__":
    main()
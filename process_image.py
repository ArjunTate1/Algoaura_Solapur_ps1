import re
import cv2
import numpy as np
import pytesseract
from PIL import Image
from pathlib import Path
from ultralytics import YOLO

# ------------------ CONFIG ------------------

MODEL_PATH = Path("runs/detect/train2/weights/best.pt")
CONF_THRESHOLD = 0.6

# Pixel-to-meter scaling (DECLARED ASSUMPTION)
MM_PER_PIXEL = 2.5  # 2.5 mm per pixel (approx)

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# ------------------ LOAD MODEL ------------------

model = YOLO(MODEL_PATH)

# ------------------ MAIN PROCESS FUNCTION ------------------

def process_image(image_path: str):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Load image
    pil_img = Image.open(image_path).convert("RGB")
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # ------------------ YOLO DETECTION ------------------

    results = model.predict(
        source=img,
        conf=0.3,
        save=False
    )

    potholes = []

    boxes = results[0].boxes
    if boxes is not None:
        for box in boxes:
            conf = float(box.conf[0])
            if conf < CONF_THRESHOLD:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Pixel calculations
            length_px = x2 - x1
            breadth_px = y2 - y1
            area_px = length_px * breadth_px

            # Meter conversion
            length_m = (length_px * MM_PER_PIXEL) / 1000
            breadth_m = (breadth_px * MM_PER_PIXEL) / 1000
            area_m2 = length_m * breadth_m

            potholes.append({
                "confidence": round(conf, 2),
                "length_px": length_px,
                "breadth_px": breadth_px,
                "area_px": area_px,
                "length_m": round(length_m, 3),
                "breadth_m": round(breadth_m, 3),
                "area_m2": round(area_m2, 4)
            })

            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                img,
                f"Area: {area_px}px2",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

    # ------------------ OCR ------------------

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ocr_text = pytesseract.image_to_string(
        gray,
        config="--psm 6"
    )

    # ------------------ GPS EXTRACTION ------------------

    lat_match = re.search(r"Lat\s*([\d.]+)", ocr_text, re.IGNORECASE)
    lon_match = re.search(r"Long\s*([\d.]+)", ocr_text, re.IGNORECASE)

    latitude = lat_match.group(1) if lat_match else None
    longitude = lon_match.group(1) if lon_match else None

    address = None
    for line in ocr_text.splitlines():
        if "India" in line:
            address = line.strip()
            break

    # ------------------ FINAL RESPONSE ------------------

    return {
        "pothole_count": len(potholes),
        "potholes": potholes,
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "annotated_image": img
    }

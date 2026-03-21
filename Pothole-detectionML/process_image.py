import re
import cv2
import numpy as np
import pytesseract
import shutil
import platform
import os
from PIL import Image, ExifTags
from pathlib import Path
from ultralytics import YOLO
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# ── Load .env ──
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# ------------------ CLOUDINARY CONFIG ------------------

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key    = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
)

def upload_to_cloudinary(file_path, folder="margakshat"):
    try:
        res = cloudinary.uploader.upload(
            str(file_path),
            folder=folder,
            resource_type="image"
        )
        return res["secure_url"]
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        return None

# ------------------ CONFIG ------------------

MODEL_PATH     = Path("runs/detect/train2/weights/best.pt")
CONF_THRESHOLD = 0.6
MM_PER_PIXEL   = 2.5

# ------------------ AUTO-DETECT TESSERACT ------------------

def find_tesseract():
    # Check system PATH first
    path = shutil.which("tesseract")
    if path:
        return path

    # Windows common locations
    if platform.system() == "Windows":
        windows_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(
                os.environ.get("USERNAME", "")
            ),
        ]
        for p in windows_paths:
            if os.path.exists(p):
                return p

    # Mac (homebrew)
    if platform.system() == "Darwin":
        for p in ["/usr/local/bin/tesseract", "/opt/homebrew/bin/tesseract"]:
            if os.path.exists(p):
                return p

    # Linux fallback
    return "tesseract"

tesseract_path = find_tesseract()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    print(f"Tesseract found at: {tesseract_path}")
else:
    print("WARNING: Tesseract not found — OCR will not work")

# ------------------ LOAD MODEL ------------------

model = YOLO(MODEL_PATH)

# ------------------ GPS EXTRACTION ------------------

def extract_gps_from_exif(image_path):
    """Extract GPS coordinates from image EXIF metadata."""
    try:
        img      = Image.open(image_path)
        exif_raw = img._getexif()
        if not exif_raw:
            return None, None

        gps_info = {}
        for tag, value in exif_raw.items():
            tag_name = ExifTags.TAGS.get(tag, tag)
            if tag_name == "GPSInfo":
                for gps_tag, gps_val in value.items():
                    gps_info[ExifTags.GPSTAGS.get(gps_tag, gps_tag)] = gps_val

        if not gps_info:
            return None, None

        def convert_dms(dms, ref):
            d = float(dms[0])
            m = float(dms[1])
            s = float(dms[2])
            val = d + m / 60 + s / 3600
            if ref in ['S', 'W']:
                val = -val
            return round(val, 6)

        lat = convert_dms(gps_info['GPSLatitude'],  gps_info['GPSLatitudeRef'])
        lng = convert_dms(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
        print(f"EXIF GPS found: {lat}, {lng}")
        return str(lat), str(lng)

    except Exception as e:
        print(f"EXIF extraction failed: {e}")
        return None, None


def extract_gps_from_ocr(ocr_text):
    """Extract GPS from camera-stamped text watermark on image."""
    lat_match = re.search(
        r"Lat(?:itude)?\s*[:\s]*([\d]{1,3}\.[\d]+)",
        ocr_text, re.IGNORECASE
    )
    lon_match = re.search(
        r"Lon(?:g|gitude)?\s*[:\s]*([\d]{1,3}\.[\d]+)",
        ocr_text, re.IGNORECASE
    )
    lat = lat_match.group(1) if lat_match else None
    lng = lon_match.group(1) if lon_match else None
    if lat and lng:
        print(f"OCR GPS found: {lat}, {lng}")
    return lat, lng


def extract_address_from_ocr(ocr_text):
    """Extract address line from OCR text."""
    for line in ocr_text.splitlines():
        line = line.strip()
        if "India" in line and len(line) > 6:
            return line
    return None

# ------------------ MAIN PROCESS FUNCTION ------------------

def process_image(image_path: str):

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    pil_img = Image.open(image_path).convert("RGB")
    img     = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # ── Upload ORIGINAL image to Cloudinary ──
    original_url = upload_to_cloudinary(image_path, folder="margakshat/originals")

    # ------------------ YOLO DETECTION ------------------

    results  = model.predict(source=img, conf=0.3, save=False)
    potholes = []
    boxes    = results[0].boxes

    if boxes is not None:
        for box in boxes:
            conf = float(box.conf[0])
            if conf < CONF_THRESHOLD:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            length_px  = x2 - x1
            breadth_px = y2 - y1
            area_px    = length_px * breadth_px

            length_m  = (length_px  * MM_PER_PIXEL) / 1000
            breadth_m = (breadth_px * MM_PER_PIXEL) / 1000
            area_m2   = length_m * breadth_m

            potholes.append({
                "confidence": round(conf, 2),
                "length_px":  length_px,
                "breadth_px": breadth_px,
                "area_px":    area_px,
                "length_m":   round(length_m, 3),
                "breadth_m":  round(breadth_m, 3),
                "area_m2":    round(area_m2, 4)
            })

            # Draw bounding box + label on processed image
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                img,
                f"{round(conf*100)}% | {round(area_m2, 3)}m2",
                (x1, max(y1 - 8, 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 1
            )

    # ------------------ SAVE + UPLOAD PROCESSED IMAGE ------------------

    processed_path = image_path.parent / f"processed_{image_path.name}"
    cv2.imwrite(str(processed_path), img)
    processed_url = upload_to_cloudinary(processed_path, folder="margakshat/processed")

    if processed_path.exists():
        os.remove(processed_path)

    # ------------------ OCR ------------------

    gray     = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ocr_text = pytesseract.image_to_string(gray, config="--psm 6")

    # ------------------ GPS EXTRACTION ------------------

    # Step 1 — Try EXIF metadata (most accurate)
    latitude, longitude = extract_gps_from_exif(image_path)
    gps_source = "exif" if latitude and longitude else None

    # Step 2 — Try OCR watermark text on image
    if not latitude or not longitude:
        latitude, longitude = extract_gps_from_ocr(ocr_text)
        gps_source = "ocr" if latitude and longitude else None

    # Step 3 — Browser GPS fallback handled in backend_api.py
    if not latitude or not longitude:
        print("No GPS found in image — will use browser GPS fallback")
        gps_source = "browser_fallback"

    # ------------------ ADDRESS EXTRACTION ------------------

    address = extract_address_from_ocr(ocr_text)

    # ------------------ FINAL RESPONSE ------------------

    return {
        "pothole_count": len(potholes),
        "potholes":      potholes,
        "address":       address,
        "latitude":      latitude,
        "longitude":     longitude,
        "gps_source":    gps_source,
        "original_img":  original_url,
        "processed_img": processed_url
    }

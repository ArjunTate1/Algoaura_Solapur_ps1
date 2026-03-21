import os
import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
from sklearn.model_selection import train_test_split

# ---------------- CONFIG ----------------
BASE_DIR = Path(__file__).parent
IMG_DIR = BASE_DIR / "annotated-images" / "images"
XML_DIR = BASE_DIR / "annotated-images" / "xml"
OUT_DIR = BASE_DIR.parent / "dataset"

IMG_TRAIN = OUT_DIR / "images" / "train"
IMG_VAL   = OUT_DIR / "images" / "val"
LBL_TRAIN = OUT_DIR / "labels" / "train"
LBL_VAL   = OUT_DIR / "labels" / "val"

SPLIT = 0.2
CLASS_MAP = {"pothole": 0}
# ----------------------------------------

for d in [IMG_TRAIN, IMG_VAL, LBL_TRAIN, LBL_VAL]:
    d.mkdir(parents=True, exist_ok=True)

def convert_xml(xml_path, label_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    size = root.find("size")
    w = int(size.find("width").text)
    h = int(size.find("height").text)

    with open(label_path, "w") as f:
        for obj in root.findall("object"):
            name = obj.find("name").text.lower()
            if name not in CLASS_MAP:
                continue

            cls = CLASS_MAP[name]
            bnd = obj.find("bndbox")
            xmin = int(bnd.find("xmin").text)
            ymin = int(bnd.find("ymin").text)
            xmax = int(bnd.find("xmax").text)
            ymax = int(bnd.find("ymax").text)

            xc = ((xmin + xmax) / 2) / w
            yc = ((ymin + ymax) / 2) / h
            bw = (xmax - xmin) / w
            bh = (ymax - ymin) / h

            f.write(f"{cls} {xc} {yc} {bw} {bh}\n")

images = list(IMG_DIR.glob("*.jpg"))
train, val = train_test_split(images, test_size=SPLIT, random_state=42)

def process(img_list, img_out, lbl_out):
    for img in img_list:
        xml = XML_DIR / f"{img.stem}.xml"
        if not xml.exists():
            continue
        shutil.copy(img, img_out / img.name)
        convert_xml(xml, lbl_out / f"{img.stem}.txt")

process(train, IMG_TRAIN, LBL_TRAIN)
process(val, IMG_VAL, LBL_VAL)

print("XML → YOLO conversion done")
print(f"Train images: {len(train)}")
print(f"Val images: {len(val)}")

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile
from process_image import process_image

# ------------------ PAGE CONFIG ------------------

st.set_page_config(
    page_title="Pothole Detection System",
    layout="centered"
)

st.title("🕳️ Pothole Detection, Measurement & GPS Extraction")

st.markdown(
    """
    Upload a road image (JPG / PNG / WEBP).  
    The system will:
    - Detect potholes using YOLOv8  
    - Calculate Length, Breadth, and Area (pixels & meters)  
    - Extract GPS / address text using OCR  
    """
)

# ------------------ FILE UPLOADER ------------------

uploaded_file = st.file_uploader(
    "Upload road image",
    type=["jpg", "jpeg", "png", "webp"]  # ✅ WEBP ALLOWED
)

if uploaded_file is not None:

    # ------------------ LOAD IMAGE SAFELY ------------------

    try:
        pil_img = Image.open(uploaded_file).convert("RGB")
    except Exception as e:
        st.error(f"Failed to read image: {e}")
        st.stop()

    img_np = np.array(pil_img)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Save to a temporary file (YOLO prefers file paths)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        temp_image_path = tmp.name
        cv2.imwrite(temp_image_path, img_bgr)

    # ------------------ PROCESS IMAGE ------------------

    with st.spinner("Detecting potholes and calculating measurements..."):
        result = process_image(temp_image_path)

    st.success("Processing completed successfully!")

    # ------------------ SUMMARY ------------------

    st.subheader("📊 Detection Summary")
    st.write("**Potholes detected:**", result["pothole_count"])
    st.write("**Address:**", result["address"])
    st.write("**Latitude:**", result["latitude"])
    st.write("**Longitude:**", result["longitude"])

    # ------------------ POTHOLE DETAILS ------------------

    if result["potholes"]:
        st.subheader("📐 Pothole Measurements")

        for idx, pothole in enumerate(result["potholes"], start=1):
            st.markdown(f"### Pothole {idx}")
            st.write("Confidence:", pothole["confidence"])
            st.write("Length (px):", pothole["length_px"])
            st.write("Breadth (px):", pothole["breadth_px"])
            st.write("Area (px²):", pothole["area_px"])
            st.write("Length (m):", pothole["length_m"])
            st.write("Breadth (m):", pothole["breadth_m"])
            st.write("Area (m²):", pothole["area_m2"])
            st.divider()
    else:
        st.warning("No potholes detected with sufficient confidence.")

    # ------------------ SHOW IMAGE ------------------

    st.subheader("🖼️ Annotated Image")

    annotated_rgb = cv2.cvtColor(
        result["annotated_image"],
        cv2.COLOR_BGR2RGB
    )

    st.image(
        annotated_rgb,
        caption="Detected potholes with bounding boxes and area",
        use_column_width=True
    )

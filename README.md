# 🛣️ Margakshat — AI-Powered Road Damage Monitor
### Solapur Municipal Corporation · Maharashtra · Smart City Challenge

> An end-to-end AI system for detecting, managing, and resolving road damage using computer vision, GPS extraction, priority scoring, and a multi-role dashboard.

---

## 🎥 Demo Video
> 📹 [Add your demo video link here — YouTube / Google Drive]

---

## 📸 Screenshots
> Add screenshots of your dashboards here after recording

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| 🤖 AI Detection | YOLOv8 detects potholes with bounding boxes, confidence scores, and physical dimensions |
| 📍 GPS Extraction | Extracts coordinates from EXIF metadata → OCR watermark → Browser GPS (priority order) |
| 🎯 Z-Score Priority | Ranks potholes: 30% count + 40% area + 30% report frequency |
| 👥 3-Role System | Separate dashboards for Users, Admins, and Contractors |
| 🗺️ Live Map | Satellite view, heatmap, clustering, real-time GPS navigation |
| 🔧 Repair Verification | Contractor uploads repair photo → User approves/rejects + star rating |
| 💬 Discussion Forum | Citizens post issues, upvote, comment; admins moderate and pin |
| 🤖 AI Chatbot | RAG-based chatbot using Motor Vehicles Act PDF + Llama3 (offline) |
| 📊 Analytics | Live charts for all 3 roles using MongoDB data |
| ☁️ Cloud Storage | Original, processed, and repair images stored on Cloudinary |

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Maps | Leaflet.js, OpenStreetMap, OSRM Routing |
| Charts | Chart.js |
| Backend | FastAPI (Python 3.11) |
| Database | MongoDB 8.x |
| AI Detection | YOLOv8 (Ultralytics) |
| OCR | Tesseract |
| Chatbot | Ollama (Llama3) + LangChain + FAISS |
| Image Storage | Cloudinary |

---

## 📁 Project Structure

```
Algoaura_Solapur_ps1/
├── Backend/
│   ├── __init__.py
│   ├── backend_api.py          # All FastAPI routes
│   ├── database.py             # MongoDB operations
│   └── process_image.py        # YOLO + Cloudinary + GPS extraction
├── Pothole-detectionML/
│   ├── app.py                  # Standalone Streamlit version (optional)
│   └── process_image.py        # ML processing module
├── chatbot/
│   ├── app.py                  # Chatbot RAG logic
│   ├── 2202011053641.pdf        # Motor Vehicles Act (source document)
│   └── requirements.txt
├── frontend/
│   ├── login.html              # Role-based login
│   ├── user.html               # Report potholes + view map
│   ├── admin.html              # Manage reports + assign contractors
│   ├── contractor.html         # View tasks + upload repair proof
│   ├── maps.html               # Live satellite map
│   ├── forum.html              # Community discussion forum
│   ├── analytics.html          # Role-based charts
│   └── chatbot.html            # AI assistant UI
├── runs/
│   └── best.pt                 # Trained YOLOv8 model weights (5.9MB)
├── .env.example                # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Prerequisites

Install these **before** running the project:

| Tool | Download Link |
|------|--------------|
| Python 3.11+ | https://www.python.org/downloads/ |
| MongoDB 8.x | https://www.mongodb.com/try/download/community |
| Tesseract OCR | https://github.com/UB-Mannheim/tesseract/wiki |
| Ollama | https://ollama.com/download |
| VS Code + Live Server extension | https://code.visualstudio.com |

---

## 🚀 Setup & Run

### Step 1 — Clone the repository
```bash
git clone https://github.com/ArjunTate1/Algoaura_Solapur_ps1.git
cd Algoaura_Solapur_ps1
```

### Step 2 — Create virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Mac / Linux
source .venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Create `.env` file
Create a file named `.env` in the project root:
```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```
Get free credentials at [cloudinary.com](https://cloudinary.com)

### Step 5 — Start MongoDB
Open a terminal and run:
```bash
# Windows
"C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe" --dbpath C:\data\db --wiredTigerCacheSizeGB 0.5

# Mac / Linux
mongod --dbpath /data/db
```
Keep this terminal open.

### Step 6 — Start Ollama (for chatbot)
Open a new terminal:
```bash
ollama pull llama3
ollama serve
```
Keep this terminal open.

### Step 7 — Start FastAPI backend
Open a new terminal:
```bash
uvicorn Backend.backend_api:app --reload
```
Backend runs at `http://127.0.0.1:8000`

### Step 8 — Open the frontend
Open `frontend/login.html` with **VS Code Live Server** (right-click → Open with Live Server)

---

## 👥 Create Test Users

Visit `http://127.0.0.1:8000/docs` and use `POST /register` to create:

```json
{"username": "admin1",       "password": "admin123",       "role": "admin"}
{"username": "contractor1",  "password": "contractor123",  "role": "contractor"}
{"username": "user1",        "password": "user123",        "role": "user"}
```

---

## 🔑 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Authenticate user |
| POST | `/register` | Create new user |
| GET | `/potholes` | All pothole reports |
| POST | `/upload` | Upload image with GPS |
| GET | `/potholes/priority` | Z-score ranked potholes |
| PATCH | `/assign` | Assign pothole to contractor |
| GET | `/my-tasks` | Contractor's assigned tasks |
| POST | `/repair/submit` | Upload repair proof photo |
| POST | `/repair/approve` | Approve repair + rate |
| POST | `/repair/reject` | Reject repair with reason |
| POST | `/chat` | AI chatbot query |
| GET | `/forum/posts` | All forum posts |
| POST | `/forum/post` | Create discussion post |
| PATCH | `/forum/pin` | Admin pin post |

---

## 🎯 Z-Score Priority Algorithm

```
Z = 0.30 × normalized_pothole_count
  + 0.40 × normalized_area_m²
  + 0.30 × normalized_report_frequency

Priority Levels:
  Z ≥ 0.7  →  🔴 Critical
  Z ≥ 0.4  →  🟠 High
  Z ≥ 0.2  →  🟡 Medium
  Z < 0.2  →  🟢 Low
```

---

## 🔄 Repair Verification Workflow

```
1. Admin assigns pothole to contractor
2. Contractor fixes road
3. Contractor uploads repair photo → status: pending_review
4. User reviews repair photo
   ├── Approve + 1-5 star rating → status: resolved
   └── Reject with reason → status: assigned (contractor redoes)
5. Rating saved to MongoDB for contractor performance tracking
```

---

## 🗺️ Map Features

- 🛰️ Satellite + Street view toggle
- 🔥 Heatmap density overlay
- 📍 Marker clustering
- 🧭 Live GPS tracking with vehicle selection (Car / Bike / Walking)
- ⚠️ Pothole proximity warnings during navigation
- 📐 Click-to-copy coordinates with DMS conversion

---

## 📊 Analytics by Role

| Role | Charts Available |
|------|----------------|
| 🛡️ Admin | Severity donut · Status breakdown · Reports over time · Contractor performance · Top hotspot locations |
| 👤 User | My reports history · Severity breakdown · Status tracker |
| 🔧 Contractor | Resolved vs Pending · Severity of tasks · Work done by week · Resolution rate % |

---

## 🌐 Environment Variables

| Variable | Description |
|----------|-------------|
| `CLOUDINARY_CLOUD_NAME` | Cloudinary account cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |

---

## 📋 Dependencies

```
# Backend
fastapi, uvicorn, pymongo, python-multipart
python-dotenv, cloudinary

# AI & Detection
ultralytics, opencv-python, pytesseract, Pillow

# Chatbot
langchain, langchain-community, langchain-ollama
faiss-cpu, pypdf, sentence-transformers

# Frontend (CDN - no install needed)
Leaflet.js, Chart.js, OpenStreetMap, OSRM
```

---

## 🏆 Team

**Algoaura** — Built for Solapur Municipal Corporation Smart City Hackathon

---

## 📝 Notes

- GPS coordinates are extracted in priority: **EXIF → OCR watermark → Browser GPS**
- Duplicate reports from same location are **automatically merged** and count increases
- The YOLO model (`best.pt`) is trained on a custom pothole dataset
- All images are stored on Cloudinary — no local storage needed in production
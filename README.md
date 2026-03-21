# 🛣️ Margakshat — Road Damage Monitor
### Solapur Municipal Corporation · Maharashtra

An AI-powered road damage detection and management system that allows citizens to report potholes, administrators to manage and assign repairs, and contractors to submit proof of completed work.

---

## 🚀 Features

- **AI Pothole Detection** — YOLOv8 model detects potholes from uploaded images
- **GPS Extraction** — Extracts coordinates from EXIF metadata or OCR watermarks
- **Z-Score Priority System** — Ranks potholes by count (30%) + area (40%) + report frequency (30%)
- **Role-based Dashboards** — Separate interfaces for Users, Admins, and Contractors
- **Live Map** — Satellite view with heatmap, clustering, and real-time navigation
- **Repair Verification** — Contractors upload repair photos, users approve/reject with star ratings
- **Discussion Forum** — Citizens post issues, upvote, comment; admins moderate
- **AI Chatbot** — Answers Indian traffic law questions using RAG (Llama3 + Motor Vehicles Act PDF)
- **Analytics** — Charts for all 3 roles using live database data
- **Cloudinary Storage** — Original, processed, and repair images stored in cloud

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript, Leaflet.js, Chart.js |
| Backend | FastAPI (Python) |
| Database | MongoDB |
| AI Detection | YOLOv8 (Ultralytics) |
| OCR | Tesseract |
| Chatbot | Ollama (Llama3) + LangChain + FAISS |
| Image Storage | Cloudinary |
| Maps | OpenStreetMap + OSRM Routing |

---

## 📁 Project Structure

```
Algoaura_Solapur_ps1/
├── Backend/
│   ├── __init__.py
│   ├── backend_api.py      # FastAPI routes
│   ├── database.py         # MongoDB functions
│   └── process_image.py    # YOLO detection + Cloudinary upload
├── Pothole-detectionML/
│   ├── app.py              # Standalone Streamlit chatbot (optional)
│   └── process_image.py    # ML processing
├── chatbot/
│   ├── app.py              # Chatbot logic
│   ├── 2202011053641.pdf   # Motor Vehicles Act PDF
│   └── requirements.txt
├── frontend/
│   ├── login.html          # Login page (3 roles)
│   ├── user.html           # User dashboard
│   ├── admin.html          # Admin dashboard
│   ├── contractor.html     # Contractor dashboard
│   ├── maps.html           # Live pothole map
│   ├── forum.html          # Discussion forum
│   ├── analytics.html      # Charts and graphs
│   └── chatbot.html        # AI assistant UI
├── runs/
│   └── best.pt             # Trained YOLOv8 model weights
├── .env.example            # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.11+
- MongoDB 8.x
- Tesseract OCR
- Ollama (for chatbot)
- Node.js (optional, for Live Server)

---

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Algoaura_Solapur_ps1.git
cd Algoaura_Solapur_ps1
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Mac/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

Get your credentials from [cloudinary.com](https://cloudinary.com) → Dashboard.

### 5. Start MongoDB
```cmd
# Windows (Command Prompt as Admin)
"C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe" --dbpath C:\data\db --wiredTigerCacheSizeGB 0.5
```

### 6. Start Ollama (for Chatbot)
```bash
ollama pull llama3
ollama serve
```

### 7. Start the Backend
```bash
uvicorn Backend.backend_api:app --reload
```

Backend will be available at `http://127.0.0.1:8000`

### 8. Open the Frontend
Open `frontend/login.html` with VS Code Live Server or any local server.

---

## 👥 Create Test Users

Visit `http://127.0.0.1:8000/docs` and use `POST /register` to create:

```json
{"username": "admin1", "password": "admin123", "role": "admin"}
{"username": "contractor1", "password": "contractor123", "role": "contractor"}
{"username": "user1", "password": "user123", "role": "user"}
```

---

## 🔑 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Login and get role |
| POST | `/register` | Create new user |
| GET | `/potholes` | Get all pothole reports |
| POST | `/upload` | Upload image with GPS metadata |
| POST | `/detect` | Detect potholes from image |
| GET | `/potholes/priority` | Get Z-score ranked potholes |
| PATCH | `/assign` | Admin assigns pothole to contractor |
| GET | `/my-tasks` | Contractor's assigned tasks |
| POST | `/repair/submit` | Contractor uploads repair photo |
| POST | `/repair/approve` | User approves repair + rates |
| POST | `/repair/reject` | User rejects repair |
| GET | `/contractors` | List all contractors |
| POST | `/chat` | AI chatbot query |
| GET | `/forum/posts` | Get all forum posts |
| POST | `/forum/post` | Create new post |
| POST | `/forum/comment` | Add comment to post |
| POST | `/forum/upvote` | Upvote a post |
| PATCH | `/forum/pin` | Admin pins a post |
| DELETE | `/forum/post/{id}` | Admin deletes a post |

---

## 🤖 Z-Score Priority Algorithm

Each pothole is ranked using a weighted Z-score:

```
Z = 0.30 × normalized_pothole_count
  + 0.40 × normalized_area (m²)
  + 0.30 × normalized_report_frequency

Priority:
  Z ≥ 0.7  → Critical
  Z ≥ 0.4  → High
  Z ≥ 0.2  → Medium
  Z < 0.2  → Low
```

---

## 🔄 Repair Verification Flow

```
Admin assigns → Contractor fixes road → Uploads repair photo
→ Status: pending_review → User reviews photo
→ Approve (1-5 star rating) → Status: resolved
→ Reject (with reason) → Status: assigned (contractor redoes)
```

---

## 🗺️ Map Features

- Satellite + Street view toggle
- Heatmap density overlay
- Marker clustering
- Live GPS tracking
- Turn-by-turn navigation (Car / Bike / Walking)
- Pothole proximity warnings during navigation
- Click-to-copy coordinates

---

## 📊 Analytics

| Role | Charts |
|------|--------|
| Admin | Severity donut, Status donut, Reports over time, Contractor performance, Top hotspots |
| User | My reports history, Severity breakdown, Status tracker |
| Contractor | Resolved vs Pending, Severity of tasks, Work done by week |

---

## 🌐 Environment Variables

| Variable | Description |
|----------|-------------|
| `CLOUDINARY_CLOUD_NAME` | Your Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Your Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Your Cloudinary API secret |

---

## 📝 Notes

- Tesseract OCR must be installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`
- The YOLO model (`best.pt`) is included in `runs/` folder
- GPS coordinates are extracted in priority order: EXIF → OCR watermark → Browser GPS
- Duplicate reports from the same location are automatically merged

---

## 🏆 Team

**Algoaura** — Built for Solapur Municipal Corporation Smart City Challenge

# Margakshat — Road Damage Monitor

## Setup
1. Clone the repo
2. Create `.env` file with:
   CLOUDINARY_CLOUD_NAME=...
   CLOUDINARY_API_KEY=...
   CLOUDINARY_API_SECRET=...
3. Install dependencies:
   pip install -r requirements.txt
4. Run backend:
   uvicorn backend.backend_api:app --reload
5. Open frontend1/login.html with Live Server

## Test accounts
Create via POST /register:
- user1 / user123 (role: user)
- admin1 / admin123 (role: admin)
- contractor1 / contractor123 (role: contractor)


## Chatbot Setup
The chatbot requires Ollama running locally.

1. Install Ollama from https://ollama.com
2. Pull the model:
   ollama pull llama3
3. Run Ollama:
   ollama serve
4. Run the chatbot backend is already integrated into FastAPI via /chat endpoint

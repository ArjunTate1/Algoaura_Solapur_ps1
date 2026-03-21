from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware  
import shutil
import os

from backend.process_image import process_image
from backend.database import save_pothole_report, get_all_potholes


# Add these imports at the top
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama


import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv







app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend API working"}


# =====================================
# EXISTING IMAGE DETECTION API
# =====================================

@app.post("/detect")
async def detect(file: UploadFile = File(...)):

    file_location = f"temp_{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = process_image(file_location)

    saved_data = save_pothole_report(result)

    return saved_data


# =================================
# CAMERA UPLOAD API 
# =================================

@app.post("/upload")
async def upload_from_camera(
    file:    UploadFile = File(...),
    lat:     str = Form(None),
    lng:     str = Form(None),
    address: str = Form(None),
    time:    str = Form(None)
):
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = process_image(file_location)

    # Browser GPS fallback — only used if image had no GPS
    if not result.get("latitude") and lat:
        result["latitude"]   = lat
        result["longitude"]  = lng
        result["gps_source"] = "browser"

    # Browser address fallback
    if not result.get("address") and address:
        result["address"] = address

    result["time"] = time

    saved_data = save_pothole_report(result)

    if os.path.exists(file_location):
        os.remove(file_location)

    return saved_data






@app.get("/potholes")
def get_potholes():
    from backend.database import get_all_potholes
    return get_all_potholes()




from backend.database import save_pothole_report, get_all_potholes, get_user, create_user

@app.post("/login")
def login(data: dict):
    user = get_user(data["username"], data["password"])
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"role": user["role"], "username": user["username"]}

@app.post("/register")
def register(data: dict):
    uid = create_user(data["username"], data["password"], data["role"])
    if not uid:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User created", "id": uid}

{"username": "admin1",      "password": "admin123",      "role": "admin"}
{"username": "contractor1", "password": "contractor123", "role": "contractor"}
{"username": "user1",       "password": "user123",       "role": "user"}

@app.patch("/assign")
def assign_pothole(data: dict):
    from backend.database import assign_to_contractor
    return assign_to_contractor(data["pothole_id"], data["contractor"])

@app.get("/contractors")
def get_contractors():
    from backend.database import get_users_by_role
    return get_users_by_role("contractor")

@app.get("/my-tasks")
def my_tasks(contractor: str):
    from backend.database import get_assigned_potholes
    return get_assigned_potholes(contractor)

@app.patch("/resolve")
def resolve_pothole(data: dict):
    from backend.database import mark_resolved
    return mark_resolved(data["pothole_id"])









# ── Load vectorstore once on startup ──
PDF_PATH = "C:/Users/Asus/Desktop/Algoaura/chatbot2/genai-traffic-law-assistant/2202011053641.pdf"

def load_vectorstore():
    loader   = PyPDFLoader(PDF_PATH)
    docs     = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=200)
    chunks   = splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.from_documents(chunks, embeddings)

vectorstore = load_vectorstore()
llm = ChatOllama(model="llama3", temperature=0)

@app.post("/chat")
def chat(data: dict):
    query = data.get("message", "").strip()
    if not query:
        return {"answer": "Please ask a question."}

    docs = vectorstore.similarity_search(query, k=4)
    if not docs:
        return {"answer": "I am not sure based on the document."}

    context = "\n\n".join(doc.page_content for doc in docs)
    prompt  = f"""You are a legal assistant for Margakshat, the Solapur road monitoring app.
Answer questions about Indian traffic laws AND how to use the Margakshat app.

RULES:
- For traffic law questions, answer strictly from the context below.
- For app usage questions (reporting potholes, navigation, login), answer helpfully.
- If unsure, say "I am not sure based on the document."

Context:
{context}

Question: {query}
Answer:"""

    response = llm.invoke(prompt)
    return {"answer": response.content.strip()}





@app.get("/forum/posts")
def forum_posts():
    from backend.database import get_forum_posts
    return [p for p in get_forum_posts() if not p.get("deleted")]

@app.post("/forum/post")
def forum_post(data: dict):
    from backend.database import create_forum_post
    return {"id": create_forum_post(data["username"], data["title"], data["body"])}

@app.post("/forum/comment")
def forum_comment(data: dict):
    from backend.database import add_comment
    return add_comment(data["post_id"], data["username"], data["comment"])

@app.post("/forum/upvote")
def forum_upvote(data: dict):
    from backend.database import upvote_post
    return upvote_post(data["post_id"], data["username"])

@app.patch("/forum/pin")
def forum_pin(data: dict):
    from backend.database import pin_post
    return pin_post(data["post_id"], data["pinned"])

@app.delete("/forum/post/{post_id}")
def forum_delete(post_id: str):
    from backend.database import delete_post
    return delete_post(post_id)

@app.get("/potholes/priority")
def get_priority():
    from backend.database import get_potholes_with_priority
    return get_potholes_with_priority()

load_dotenv()

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key    = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
)

def upload_to_cloudinary(file_path, folder="margakshat"):
    res = cloudinary.uploader.upload(
        file_path,
        folder=folder,
        resource_type="image"
    )
    return res["secure_url"]
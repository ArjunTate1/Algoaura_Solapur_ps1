from fastapi import FastAPI, UploadFile
import shutil
from process_image import detect_pothole

app = FastAPI()

@app.post("/detect")
async def detect(file: UploadFile):

    file_location = f"temp/{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = detect_pothole(file_location)

    return result

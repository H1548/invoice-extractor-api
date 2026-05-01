from fastapi import FastAPI, File, UploadFile, HTTPException,APIRouter
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.services.pipeline_service import Pipeline
import os
import tempfile

ALLOWED_EXTENSIONS = {
    "application/pdf", 
    "image/png", 
    "image/jpeg", 
    "image/tiff"
}

router = APIRouter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline_service
    pipeline_service = Pipeline()
    yield



@router.post("/extract")
async def prompt_pipeline(file: UploadFile = File(...)):

    if file.content_type not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type: {file.content_type}. Allowed: PDF, PNG, JPEG, TIFF."
            )
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    

    try:
        output = pipeline_service.process_invoice(tmp_path)
    finally:
         if os.path.exists(tmp_path):
              os.remove(tmp_path)

    return output

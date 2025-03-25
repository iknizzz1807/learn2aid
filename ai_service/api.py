from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from typing import Optional
import tempfile
import os
from model import model

router = APIRouter()


@router.get("/")
def read_root():
    return {"status": "healthy", "service": "AI Service - Gemini Video Analysis"}


@router.post("/predict")
async def predict(file: UploadFile = File(...), movement_name: str = Form("exercise")):
    try:
        print(f"Received file: {file.filename}, content_type: {file.content_type}")
        print(f"Movement name: {movement_name}")
        # Create a temporary file to store the uploaded video
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            # Write the uploaded video to the temporary file
            contents = await file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name

        # Process with Gemini
        result = model.predict(temp_file_path, movement_name)

        # Delete the temporary file
        os.unlink(temp_file_path)

        # Return the result
        if "error" in result:
            return JSONResponse(status_code=500, content=result)
        return result

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"An error occurred during processing: {str(e)}"},
        )

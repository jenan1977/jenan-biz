import os
import uuid
from fastapi import HTTPException, UploadFile
from app.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp"}


class FileService:

    @staticmethod
    def validate_file(file: UploadFile):
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed extensions: {ALLOWED_EXTENSIONS}",
            )

    @staticmethod
    async def save_file(file: UploadFile) -> str:
        FileService.validate_file(file)
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        ext = os.path.splitext(file.filename)[1].lower()
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        content = await file.read()
        with open(filepath, "wb") as f:
            f.write(content)
        return filepath

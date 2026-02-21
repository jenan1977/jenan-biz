import os
import uuid
from fastapi import UploadFile

from ..config import settings


async def save_upload_file(upload_file: UploadFile) -> str:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(upload_file.filename)[1] if upload_file.filename else ""
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    content = await upload_file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    return f"/uploads/{filename}"

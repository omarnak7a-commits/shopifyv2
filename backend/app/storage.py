import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def save_upload(file: UploadFile, subdir: str) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, or WebP images are accepted.")

    contents = file.file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image is too large. Maximum 10MB.")

    ext = ".jpg"
    if file.content_type == "image/png":
        ext = ".png"
    elif file.content_type == "image/webp":
        ext = ".webp"

    filename = f"{uuid.uuid4().hex}{ext}"
    dest_dir = settings.storage_path / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    file_path = dest_dir / filename
    file_path.write_bytes(contents)

    return f"/api/files/{subdir}/{filename}"


def save_bytes(data: bytes, subdir: str, ext: str = ".jpg") -> str:
    filename = f"{uuid.uuid4().hex}{ext}"
    dest_dir = settings.storage_path / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    file_path = dest_dir / filename
    file_path.write_bytes(data)
    return f"/api/files/{subdir}/{filename}"


def resolve_file_path(url_path: str) -> Path:
    relative = url_path.replace("/api/files/", "")
    full = settings.storage_path / relative
    if not full.resolve().is_relative_to(settings.storage_path.resolve()):
        raise HTTPException(status_code=403, detail="Forbidden path.")
    return full

import json
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db, SessionLocal
from app.config import settings
from app.seed import seed_database
from app.routers import auth, stores, products, tryon, analytics, admin, store_products

app = FastAPI(title="TryOnix API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "provider": settings.tryon_provider,
        "storage": settings.storage_mode,
    }


app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(store_products.router)
app.include_router(products.router)
app.include_router(tryon.router)
app.include_router(analytics.router)
app.include_router(admin.router)


@app.get("/api/files/{subdir}/{filename}")
def serve_file(subdir: str, filename: str):
    from fastapi.responses import FileResponse
    file_path = settings.storage_path / subdir / filename
    if not file_path.resolve().is_relative_to(settings.storage_path.resolve()):
        raise HTTPException(status_code=403, detail="Forbidden path.")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    content_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    ext = file_path.suffix.lower()
    media_type = content_types.get(ext, "application/octet-stream")
    return FileResponse(str(file_path), media_type=media_type)

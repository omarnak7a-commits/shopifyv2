import os
import sys
import tempfile
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ["TRYON_PROVIDER"] = "mock"
os.environ["DATABASE_URL"] = "sqlite:///./test_tryonix.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["STORAGE_DIR"] = "./test_storage"

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture(scope="function")
def client():
    from app.database import Base, engine, SessionLocal
    from app.seed import seed_database
    from app.main import app

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=engine)
    storage = Path("./test_storage")
    if storage.exists():
        shutil.rmtree(storage)
    db_file = Path("./test_tryonix.db")
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
def auth_headers(client):
    response = client.post("/api/auth/login", json={"email": "store@north.co", "password": "store123"})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client):
    response = client.post("/api/auth/login", json={"email": "admin@tryonix.com", "password": "admin123"})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

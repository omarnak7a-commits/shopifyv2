import os
import sys
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ["TRYON_PROVIDER"] = "mock"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["STORAGE_DIR"] = "./test_storage"

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture(scope="function")
def client():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    from app.database import Base
    from app.seed import seed_database
    from app.main import app
    from app import database as db_module

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    db_module.engine = engine
    db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    db = db_module.SessionLocal()
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

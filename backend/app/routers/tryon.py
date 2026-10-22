import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TryOnSession, Product, Store, UsageEvent, User
from app.schemas import TryOnSessionOut
from app.dependencies import get_current_user
from app.storage import save_upload, save_bytes, resolve_file_path
from app.config import settings
from app.providers.fashn import FashnProvider
from app.providers.mock import MockProvider

router = APIRouter(prefix="/api/tryon", tags=["tryon"])


def _get_provider():
    if settings.tryon_provider == "mock":
        return MockProvider()
    return FashnProvider()


def _process_tryon(session_id: str, person_image_url: str, garment_image_url: str, category: str):
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        session = db.query(TryOnSession).filter(TryOnSession.id == session_id).first()
        if not session:
            return

        person_path = resolve_file_path(person_image_url)
        provider = _get_provider()

        try:
            result_bytes = provider.generate(person_path, garment_image_url, category)
            result_url = save_bytes(result_bytes, "results", ".png")
            session.result_image = result_url
            session.status = "completed"
            session.completed_at = datetime.now(timezone.utc)
        except Exception as e:
            session.status = "failed"
            session.completed_at = datetime.now(timezone.utc)
            session.result_image = None

            db.add(UsageEvent(
                id=f"e-{uuid.uuid4().hex[:12]}",
                type="try_on_failed",
                store_id=session.store_id,
                product_id=session.product_id,
                session_id=session.id,
            ))
            db.commit()
            return

        db.add(UsageEvent(
            id=f"e-{uuid.uuid4().hex[:12]}",
            type="try_on_completed",
            store_id=session.store_id,
            product_id=session.product_id,
            session_id=session.id,
        ))
        db.commit()
    finally:
        db.close()


@router.post("/sessions", response_model=TryOnSessionOut)
def create_tryon_session(
    background_tasks: BackgroundTasks,
    productId: str = Form(...),
    consent: str = Form("false"),
    personImage: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == productId).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    store = db.query(Store).filter(Store.id == product.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")

    person_image_url = save_upload(personImage, "persons")

    session = TryOnSession(
        id=f"t-{uuid.uuid4().hex[:12]}",
        product_id=productId,
        store_id=store.id,
        person_image=person_image_url,
        status="processing",
        consent=consent.lower() == "true",
    )
    db.add(session)
    db.add(UsageEvent(
        id=f"e-{uuid.uuid4().hex[:12]}",
        type="try_on_started",
        store_id=store.id,
        product_id=productId,
        session_id=session.id,
    ))
    db.commit()
    db.refresh(session)

    background_tasks.add_task(
        _process_tryon,
        session.id,
        person_image_url,
        product.image,
        product.category,
    )

    return TryOnSessionOut.from_orm_session(session)


@router.get("/sessions/{session_id}", response_model=TryOnSessionOut)
def get_tryon_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(TryOnSession).filter(TryOnSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Try-on session not found.")
    return TryOnSessionOut.from_orm_session(session)

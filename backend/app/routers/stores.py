import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Store, User
from app.schemas import StoreOut, StoreCreate, StoreUpdate
from app.dependencies import get_current_user, require_store_owner

router = APIRouter(prefix="/api/stores", tags=["stores"])


@router.get("", response_model=list[StoreOut])
def list_stores(db: Session = Depends(get_db)):
    stores = db.query(Store).all()
    return [StoreOut.from_orm_store(s) for s in stores]


@router.get("/{slug}", response_model=StoreOut)
def get_store(slug: str, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.slug == slug).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")
    return StoreOut.from_orm_store(store)


@router.post("", response_model=StoreOut)
def create_store(
    req: StoreCreate,
    user: User = Depends(require_store_owner),
    db: Session = Depends(get_db),
):
    slug = req.slug.strip().lower()
    existing = db.query(Store).filter(Store.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="A store with this slug already exists.")

    store = Store(
        id=f"s-{uuid.uuid4().hex[:12]}",
        slug=slug,
        name=req.name,
        tagline=req.tagline,
        description=req.description,
        logo_text=req.logoText or req.name[0].upper(),
        banner_image=req.bannerImage,
        owner_id=user.id,
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    return StoreOut.from_orm_store(store)


@router.patch("/{store_id}", response_model=StoreOut)
def update_store(
    store_id: str,
    req: StoreUpdate,
    user: User = Depends(require_store_owner),
    db: Session = Depends(get_db),
):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")
    if store.owner_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only edit your own store.")

    if req.name is not None:
        store.name = req.name
    if req.tagline is not None:
        store.tagline = req.tagline
    if req.description is not None:
        store.description = req.description
    db.commit()
    db.refresh(store)
    return StoreOut.from_orm_store(store)

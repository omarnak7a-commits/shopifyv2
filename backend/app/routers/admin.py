import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, TryOnSession, Store, Product
from app.schemas import UserOut, TryOnSessionOut, StoreOut, ProductOut
from app.dependencies import require_admin
import json

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [UserOut.from_orm_user(u) for u in users]


@router.patch("/users/{user_id}/toggle-disabled", response_model=UserOut)
def toggle_user_disabled(
    user_id: str,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found.")
    target.disabled = not target.disabled
    db.commit()
    db.refresh(target)
    return UserOut.from_orm_user(target)


@router.get("/sessions", response_model=list[TryOnSessionOut])
def list_all_sessions(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    sessions = db.query(TryOnSession).all()
    return [TryOnSessionOut.from_orm_session(s) for s in sessions]


@router.get("/sessions/failed", response_model=list[TryOnSessionOut])
def list_failed_sessions(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    sessions = db.query(TryOnSession).filter(TryOnSession.status == "failed").all()
    return [TryOnSessionOut.from_orm_session(s) for s in sessions]

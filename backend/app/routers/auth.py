from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, UserOut
from app.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.dependencies import get_current_user

import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    role = req.role if req.role in ("customer", "store_owner", "admin") else "customer"
    display_name = req.displayName.strip() or email.split("@")[0]

    user = User(
        id=f"u-{uuid.uuid4().hex[:12]}",
        email=email,
        password_hash=hash_password(req.password),
        role=role,
        display_name=display_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token_data = {"sub": user.id, "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=UserOut.from_orm_user(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    if user.disabled:
        raise HTTPException(status_code=401, detail="This account has been disabled.")

    token_data = {"sub": user.id, "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=UserOut.from_orm_user(user),
    )


@router.post("/refresh", response_model=dict)
def refresh(req: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.disabled:
        raise HTTPException(status_code=401, detail="User not found or disabled.")

    token_data = {"sub": user.id, "role": user.role}
    return {"access_token": create_access_token(token_data), "token_type": "bearer"}


@router.post("/logout")
def logout():
    return {"message": "Logged out. Discard your tokens on the client."}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.from_orm_user(user)

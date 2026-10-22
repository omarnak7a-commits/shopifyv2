import json
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    email: str
    role: str
    displayName: str
    createdAt: str
    disabled: bool = False

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_user(cls, user) -> "UserOut":
        return cls(
            id=user.id,
            email=user.email,
            role=user.role,
            displayName=user.display_name,
            createdAt=user.created_at.isoformat() if hasattr(user.created_at, "isoformat") else str(user.created_at),
            disabled=user.disabled,
        )


class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str = "customer"
    displayName: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class StoreOut(BaseModel):
    id: str
    slug: str
    name: str
    tagline: str
    description: str
    logoText: str
    bannerImage: str
    ownerId: str
    createdAt: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_store(cls, store) -> "StoreOut":
        return cls(
            id=store.id,
            slug=store.slug,
            name=store.name,
            tagline=store.tagline,
            description=store.description,
            logoText=store.logo_text,
            bannerImage=store.banner_image,
            ownerId=store.owner_id,
            createdAt=store.created_at.isoformat() if hasattr(store.created_at, "isoformat") else str(store.created_at),
        )


class StoreCreate(BaseModel):
    name: str
    slug: str
    tagline: str = ""
    description: str = ""
    logoText: str = ""
    bannerImage: str = ""


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None


class VariantOut(BaseModel):
    id: str
    color: str
    colorHex: str
    sizes: list[str]


class ProductOut(BaseModel):
    id: str
    storeId: str
    name: str
    description: str
    category: str
    price: Optional[float]
    image: str
    variants: list[VariantOut]
    createdAt: str

    class Config:
        from_attributes = True


class VariantCreate(BaseModel):
    color: str = ""
    colorHex: str = "#000000"
    sizes: list[str] = Field(default_factory=list)


class ProductCreate(BaseModel):
    storeId: str
    name: str
    description: str = ""
    category: str = "Other"
    price: Optional[float] = None
    variants: list[VariantCreate] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    variants: Optional[list[VariantCreate]] = None


class TryOnSessionOut(BaseModel):
    id: str
    productId: str
    storeId: str
    personImage: str
    resultImage: Optional[str]
    status: str
    consent: bool
    createdAt: str
    completedAt: Optional[str]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_session(cls, s) -> "TryOnSessionOut":
        return cls(
            id=s.id,
            productId=s.product_id,
            storeId=s.store_id,
            personImage=s.person_image,
            resultImage=s.result_image,
            status=s.status,
            consent=s.consent,
            createdAt=s.created_at.isoformat() if hasattr(s.created_at, "isoformat") else str(s.created_at),
            completedAt=s.completed_at.isoformat() if s.completed_at and hasattr(s.completed_at, "isoformat") else (str(s.completed_at) if s.completed_at else None),
        )


class AnalyticsSummary(BaseModel):
    totalTryOns: int
    successful: int
    failed: int
    mostTriedProduct: Optional[dict] = None
    recentSessions: list[TryOnSessionOut] = Field(default_factory=list)


TokenResponse.model_rebuild()


def variants_to_json(variants_data: list) -> str:
    result = []
    for v in variants_data:
        if hasattr(v, "sizes") and isinstance(v.sizes, str):
            sizes = json.loads(v.sizes)
        elif hasattr(v, "sizes"):
            sizes = v.sizes
        elif isinstance(v, dict):
            sizes = v.get("sizes", [])
        else:
            sizes = []
        result.append({
            "id": v.id if hasattr(v, "id") else "",
            "color": v.color if hasattr(v, "color") else v.get("color", ""),
            "colorHex": v.color_hex if hasattr(v, "color_hex") else v.get("colorHex", "#000000"),
            "sizes": sizes,
        })
    return json.dumps(result)


def parse_variants(variants_json: str) -> list[dict]:
    if not variants_json:
        return []
    return json.loads(variants_json)

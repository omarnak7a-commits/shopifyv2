import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: _uid("u"))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="customer")
    display_name = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    stores = relationship("Store", back_populates="owner")


class Store(Base):
    __tablename__ = "stores"

    id = Column(String, primary_key=True, default=lambda: _uid("s"))
    slug = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    tagline = Column(String, default="")
    description = Column(Text, default="")
    logo_text = Column(String, default="")
    banner_image = Column(Text, default="")
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="stores")
    products = relationship("Product", back_populates="store", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: _uid("p"))
    store_id = Column(String, ForeignKey("stores.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, default="Other")
    price = Column(Float, nullable=True)
    image = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    store = relationship("Store", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(String, primary_key=True, default=lambda: _uid("v"))
    product_id = Column(String, ForeignKey("products.id"), nullable=False, index=True)
    color = Column(String, default="")
    color_hex = Column(String, default="#000000")
    sizes = Column(Text, default="[]")

    product = relationship("Product", back_populates="variants")


class TryOnSession(Base):
    __tablename__ = "try_on_sessions"

    id = Column(String, primary_key=True, default=lambda: _uid("t"))
    product_id = Column(String, ForeignKey("products.id"), nullable=False, index=True)
    store_id = Column(String, ForeignKey("stores.id"), nullable=False, index=True)
    person_image = Column(Text, default="")
    result_image = Column(Text, nullable=True)
    status = Column(String, default="processing")
    consent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(String, primary_key=True, default=lambda: _uid("e"))
    type = Column(String, nullable=False)
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    product_id = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product, ProductVariant, Store
from app.schemas import ProductOut

router = APIRouter(prefix="/api/stores", tags=["store-products"])


def _product_to_out(p: Product) -> ProductOut:
    variants = []
    for v in p.variants:
        variants.append({
            "id": v.id,
            "color": v.color,
            "colorHex": v.color_hex,
            "sizes": json.loads(v.sizes) if v.sizes else [],
        })
    return ProductOut(
        id=p.id,
        storeId=p.store_id,
        name=p.name,
        description=p.description,
        category=p.category,
        price=p.price,
        image=p.image,
        variants=variants,
        createdAt=p.created_at.isoformat() if hasattr(p.created_at, "isoformat") else str(p.created_at),
    )


@router.get("/{slug}/products", response_model=list[ProductOut])
def list_store_products(slug: str, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.slug == slug).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")
    products = db.query(Product).filter(Product.store_id == store.id).all()
    return [_product_to_out(p) for p in products]

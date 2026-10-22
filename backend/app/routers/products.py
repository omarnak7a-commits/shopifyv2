import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product, ProductVariant, Store, User
from app.schemas import ProductOut, ProductCreate, ProductUpdate, VariantCreate
from app.dependencies import require_store_owner, get_current_user
from app.storage import save_upload

router = APIRouter(prefix="/api/products", tags=["products"])


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


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return _product_to_out(product)


@router.post("", response_model=ProductOut)
def create_product(
    storeId: str = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    category: str = Form("Other"),
    price: str = Form(""),
    variants_json: str = Form("[]"),
    image: UploadFile = File(default=None),
    user: User = Depends(require_store_owner),
    db: Session = Depends(get_db),
):
    store = db.query(Store).filter(Store.id == storeId).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")
    if store.owner_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only add products to your own store.")

    image_url = ""
    if image:
        image_url = save_upload(image, "products")

    product = Product(
        id=f"p-{uuid.uuid4().hex[:12]}",
        store_id=storeId,
        name=name,
        description=description,
        category=category,
        price=float(price) if price else None,
        image=image_url,
    )
    db.add(product)
    db.flush()

    for v_data in json.loads(variants_json):
        v = ProductVariant(
            id=f"v-{uuid.uuid4().hex[:12]}",
            product_id=product.id,
            color=v_data.get("color", ""),
            color_hex=v_data.get("colorHex", "#000000"),
            sizes=json.dumps(v_data.get("sizes", [])),
        )
        db.add(v)

    db.commit()
    db.refresh(product)
    return _product_to_out(product)


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: str,
    name: str = Form(None),
    description: str = Form(None),
    category: str = Form(None),
    price: str = Form(None),
    variants_json: str = Form(None),
    image: UploadFile = File(default=None),
    user: User = Depends(require_store_owner),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    store = db.query(Store).filter(Store.id == product.store_id).first()
    if store.owner_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only edit your own products.")

    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if category is not None:
        product.category = category
    if price is not None:
        product.price = float(price) if price else None
    if image:
        product.image = save_upload(image, "products")
    if variants_json is not None:
        db.query(ProductVariant).filter(ProductVariant.product_id == product_id).delete()
        for v_data in json.loads(variants_json):
            v = ProductVariant(
                id=f"v-{uuid.uuid4().hex[:12]}",
                product_id=product.id,
                color=v_data.get("color", ""),
                color_hex=v_data.get("colorHex", "#000000"),
                sizes=json.dumps(v_data.get("sizes", [])),
            )
            db.add(v)

    db.commit()
    db.refresh(product)
    return _product_to_out(product)


@router.delete("/{product_id}")
def delete_product(
    product_id: str,
    user: User = Depends(require_store_owner),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    store = db.query(Store).filter(Store.id == product.store_id).first()
    if store.owner_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only delete your own products.")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted."}

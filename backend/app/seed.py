import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import User, Store, Product, ProductVariant
from app.security import hash_password


def seed_database(db: Session) -> None:
    if db.query(User).count() > 0:
        return

    admin = User(
        id="u-admin-1",
        email="admin@tryonix.com",
        password_hash=hash_password("admin123"),
        role="admin",
        display_name="Admin",
        created_at=datetime(2025, 7, 1, tzinfo=timezone.utc),
    )
    owner1 = User(
        id="u-owner-1",
        email="store@north.co",
        password_hash=hash_password("store123"),
        role="store_owner",
        display_name="Mara Linden",
        created_at=datetime(2025, 8, 12, 10, 0, tzinfo=timezone.utc),
    )
    owner2 = User(
        id="u-owner-2",
        email="hello@studio-nine.co",
        password_hash=hash_password("studio123"),
        role="store_owner",
        display_name="Theo Vance",
        created_at=datetime(2025, 9, 1, 14, 30, tzinfo=timezone.utc),
    )
    db.add_all([admin, owner1, owner2])

    store1 = Store(
        id="s-north",
        slug="north-studio",
        name="North Studio",
        tagline="Quiet essentials, made to last.",
        description="North Studio makes considered wardrobe staples in natural fabrics — pieces designed to be worn often and kept for years.",
        logo_text="N",
        banner_image="https://images.pexels.com/photos/8581033/pexels-photo-8581033.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        owner_id="u-owner-1",
        created_at=datetime(2025, 8, 12, 10, 0, tzinfo=timezone.utc),
    )
    store2 = Store(
        id="s-nine",
        slug="studio-nine",
        name="Studio Nine",
        tagline="Considered pieces for everyday wear.",
        description="Studio Nine is a small collection of modern basics and soft tailoring — clothing that feels easy and lived-in from the first wear.",
        logo_text="9",
        banner_image="https://images.pexels.com/photos/9594685/pexels-photo-9594685.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        owner_id="u-owner-2",
        created_at=datetime(2025, 9, 1, 14, 30, tzinfo=timezone.utc),
    )
    db.add_all([store1, store2])
    db.flush()

    products_data = [
        ("p-001", "s-north", "Oversized Cotton Tee", "A relaxed-fit tee cut from heavyweight organic cotton. Slightly dropped shoulders and a clean, boxy silhouette that pairs with everything.", "T-Shirts", 48.0, "https://images.pexels.com/photos/5746098/pexels-photo-5746098.jpeg?auto=compress&cs=tinysrgb&h=650&w=940", datetime(2025, 8, 15, 9, tzinfo=timezone.utc), [
            ("Off White", "#F3F1EC", ["S", "M", "L", "XL"]),
            ("Stone", "#B0A89E", ["S", "M", "L"]),
            ("Black", "#1C1C1C", ["S", "M", "L", "XL"]),
        ]),
        ("p-002", "s-north", "Linen Camp Shirt", "A lightweight linen shirt with an open collar and relaxed body. Breathable and soft, made for warm days and slow mornings.", "Shirts", 89.0, "https://images.pexels.com/photos/8408556/pexels-photo-8408556.jpeg?auto=compress&cs=tinysrgb&h=650&w=940", datetime(2025, 8, 18, 12, tzinfo=timezone.utc), [
            ("Sand", "#D4C5A9", ["S", "M", "L", "XL"]),
            ("Olive", "#6B6B4A", ["M", "L"]),
        ]),
        ("p-003", "s-north", "Heavyweight Hoodie", "A brushed-fleece hoodie with a generous hood and ribbed cuffs. Warm without bulk, with a clean finish that holds its shape.", "Hoodies", 120.0, "https://images.pexels.com/photos/9594087/pexels-photo-9594087.jpeg?auto=compress&cs=tinysrgb&h=650&w=940", datetime(2025, 8, 20, 10, tzinfo=timezone.utc), [
            ("Heather Grey", "#A8A8A4", ["S", "M", "L", "XL"]),
            ("Black", "#1C1C1C", ["S", "M", "L", "XL"]),
        ]),
        ("p-004", "s-north", "Quilted Field Jacket", "A lightweight quilted jacket with a stand collar and zip front. Designed for transitional weather and easy layering.", "Jackets", 195.0, "https://images.pexels.com/photos/6044143/pexels-photo-6044143.jpeg?auto=compress&cs=tinysrgb&h=650&w=940", datetime(2025, 8, 25, 8, tzinfo=timezone.utc), [
            ("Black", "#1C1C1C", ["S", "M", "L", "XL"]),
            ("Khaki", "#8B7E5E", ["M", "L", "XL"]),
        ]),
        ("p-005", "s-nine", "Slip Midi Dress", "A bias-cut slip dress in a soft, flowing fabric. Adjustable straps and a gentle drape that moves with you.", "Dresses", 135.0, "https://images.pexels.com/photos/31674953/pexels-photo-31674953.jpeg?auto=compress&cs=tinysrgb&h=650&w=940", datetime(2025, 9, 3, 11, tzinfo=timezone.utc), [
            ("Ivory", "#EFEAE2", ["XS", "S", "M", "L"]),
            ("Black", "#1C1C1C", ["XS", "S", "M", "L"]),
        ]),
        ("p-006", "s-nine", "Wide-Leg Trouser", "High-waisted trousers with a wide, flowing leg. A tailored waistband and a fluid drape for an easy, polished look.", "Pants", 110.0, "https://images.pexels.com/photos/36856704/pexels-photo-36856704.jpeg?auto=compress&cs=tinysrgb&h=650&w=940", datetime(2025, 9, 5, 13, tzinfo=timezone.utc), [
            ("Camel", "#B89B78", ["XS", "S", "M", "L"]),
            ("Charcoal", "#3A3A3A", ["S", "M", "L"]),
        ]),
        ("p-007", "s-nine", "Soft Tailored Blazer", "An unstructured blazer with a relaxed shoulder and natural drape. Wear it open over a tee or buttoned for a cleaner line.", "Jackets", 175.0, "https://images.pexels.com/photos/19778358/pexels-photo-19778358.jpeg?auto=compress&cs=tinysrgb&h=650&w=940", datetime(2025, 9, 8, 9, 30, tzinfo=timezone.utc), [
            ("Check", "#7A6E5E", ["XS", "S", "M", "L"]),
            ("Black", "#1C1C1C", ["S", "M", "L"]),
        ]),
        ("p-008", "s-nine", "Merino Knit Top", "A fine-gauge merino top with a close, comfortable fit. Lightweight warmth and a smooth, matte finish.", "Shirts", 95.0, "https://images.pexels.com/photos/36646353/pexels-photo-36646353.jpeg?auto=compress&cs=tinysrgb&h=650&w=940", datetime(2025, 9, 10, 10, tzinfo=timezone.utc), [
            ("Black", "#1C1C1C", ["XS", "S", "M", "L"]),
            ("Oat", "#D8CFC0", ["XS", "S", "M"]),
        ]),
    ]

    for pid, sid, name, desc, cat, price, image, created, variants in products_data:
        product = Product(
            id=pid,
            store_id=sid,
            name=name,
            description=desc,
            category=cat,
            price=price,
            image=image,
            created_at=created,
        )
        db.add(product)
        db.flush()
        for color, color_hex, sizes in variants:
            v = ProductVariant(
                product_id=pid,
                color=color,
                color_hex=color_hex,
                sizes=json.dumps(sizes),
            )
            db.add(v)

    db.commit()

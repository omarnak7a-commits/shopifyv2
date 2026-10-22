import io
import json


def _make_image_bytes():
    return io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x05\xfe\xd4\x00\x00\x00\x00IEND\xaeB`\x82')


def test_get_product(client):
    response = client.get("/api/products/p-001")
    assert response.status_code == 200
    product = response.json()
    assert product["name"] == "Oversized Cotton Tee"
    assert len(product["variants"]) == 3


def test_get_product_not_found(client):
    response = client.get("/api/products/nonexistent")
    assert response.status_code == 404


def test_list_store_products(client):
    response = client.get("/api/stores/north-studio/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 4
    assert all(p["storeId"] == "s-north" for p in products)


def test_create_product(client, auth_headers):
    store_resp = client.get("/api/stores/north-studio", headers=auth_headers)
    store_id = store_resp.json()["id"]

    variants = json.dumps([
        {"color": "Black", "colorHex": "#000000", "sizes": ["S", "M", "L"]},
    ])
    response = client.post(
        "/api/products",
        data={
            "storeId": store_id,
            "name": "Test Product",
            "description": "A test product",
            "category": "T-Shirts",
            "price": "29.99",
            "variants_json": variants,
        },
        files={"image": ("test.png", _make_image_bytes(), "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    product = response.json()
    assert product["name"] == "Test Product"
    assert product["price"] == 29.99
    assert product["image"].startswith("/api/files/products/")
    assert len(product["variants"]) == 1


def test_create_product_unauthorized(client):
    response = client.post("/api/products", data={
        "storeId": "s-north",
        "name": "Test",
    })
    assert response.status_code == 401


def test_update_product(client, auth_headers):
    response = client.patch(
        "/api/products/p-001",
        data={"name": "Updated Tee", "price": "55.00"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Tee"
    assert response.json()["price"] == 55.0


def test_delete_product(client, auth_headers):
    variants = json.dumps([{"color": "Red", "colorHex": "#FF0000", "sizes": ["M"]}])
    create_resp = client.post(
        "/api/products",
        data={
            "storeId": "s-north",
            "name": "Delete Me",
            "description": "",
            "category": "Other",
            "price": "",
            "variants_json": variants,
        },
        files={"image": ("test.png", _make_image_bytes(), "image/png")},
        headers=auth_headers,
    )
    product_id = create_resp.json()["id"]

    response = client.delete(f"/api/products/{product_id}", headers=auth_headers)
    assert response.status_code == 200

    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 404

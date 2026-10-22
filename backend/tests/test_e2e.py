"""End-to-end test: full user flow with mock provider.

Register → Login → Create Store → Add Product → Fetch Product →
Upload Person Photo → Create Try-On Session → Poll Status → Fetch Result
"""
import io
import time
import json


def _make_image_bytes():
    return io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x05\xfe\xd4\x00\x00\x00\x00IEND\xaeB`\x82')


def test_e2e_full_flow(client):
    # 1. Register
    reg_resp = client.post("/api/auth/register", json={
        "email": "e2e@test.com",
        "password": "password123",
        "role": "store_owner",
        "displayName": "E2E Tester",
    })
    assert reg_resp.status_code == 200, reg_resp.text
    reg_data = reg_resp.json()
    headers = {"Authorization": f"Bearer {reg_data['access_token']}"}
    assert reg_data["user"]["role"] == "store_owner"

    # 2. Login (verify credentials work)
    login_resp = client.post("/api/auth/login", json={
        "email": "e2e@test.com",
        "password": "password123",
    })
    assert login_resp.status_code == 200
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # 3. Create Store
    store_resp = client.post("/api/stores", json={
        "name": "E2E Store",
        "slug": "e2e-store",
        "tagline": "End to end test store",
        "description": "Testing the full flow",
    }, headers=headers)
    assert store_resp.status_code == 200, store_resp.text
    store = store_resp.json()
    store_id = store["id"]
    assert store["slug"] == "e2e-store"

    # 4. Add Product with image
    variants = json.dumps([
        {"color": "Blue", "colorHex": "#0000FF", "sizes": ["S", "M", "L"]},
    ])
    product_resp = client.post(
        "/api/products",
        data={
            "storeId": store_id,
            "name": "E2E Test Shirt",
            "description": "A shirt for e2e testing",
            "category": "T-Shirts",
            "price": "39.99",
            "variants_json": variants,
        },
        files={"image": ("product.png", _make_image_bytes(), "image/png")},
        headers=headers,
    )
    assert product_resp.status_code == 200, product_resp.text
    product = product_resp.json()
    product_id = product["id"]
    assert product["name"] == "E2E Test Shirt"
    assert product["image"].startswith("/api/files/products/")

    # 5. Fetch Product
    fetch_resp = client.get(f"/api/products/{product_id}")
    assert fetch_resp.status_code == 200
    fetched = fetch_resp.json()
    assert fetched["name"] == "E2E Test Shirt"
    assert fetched["id"] == product_id
    assert len(fetched["variants"]) == 1

    # 6. Upload Person Photo + 7. Create Try-On Session
    tryon_resp = client.post(
        "/api/tryon/sessions",
        data={
            "productId": product_id,
            "consent": "true",
        },
        files={"personImage": ("person.png", _make_image_bytes(), "image/png")},
        headers=headers,
    )
    assert tryon_resp.status_code == 200, tryon_resp.text
    session = tryon_resp.json()
    session_id = session["id"]
    assert session["status"] == "processing"
    assert session["personImage"].startswith("/api/files/persons/")

    # 8. Poll Status until complete
    final_status = None
    result_data = None
    for _ in range(20):
        poll_resp = client.get(f"/api/tryon/sessions/{session_id}", headers=headers)
        assert poll_resp.status_code == 200
        result_data = poll_resp.json()
        final_status = result_data["status"]
        if final_status != "processing":
            break
        time.sleep(0.5)

    assert final_status in ("completed", "failed"), f"Session still processing after 20 polls: {final_status}"

    # 9. Fetch Result (if completed)
    if final_status == "completed":
        result_url = result_data["resultImage"]
        assert result_url is not None
        assert result_url.startswith("/api/files/results/")

        img_resp = client.get(result_url)
        assert img_resp.status_code == 200
        assert len(img_resp.content) > 0
        assert img_resp.headers["content-type"].startswith("image/")

    # Verify analytics reflect the try-on
    analytics_resp = client.get(f"/api/analytics/{store_id}", headers=headers)
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()
    assert analytics["totalTryOns"] == 1

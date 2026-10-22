import io
import time
import json


def _make_image_bytes():
    return io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x05\xfe\xd4\x00\x00\x00\x00IEND\xaeB`\x82')


def test_analytics_empty(client, auth_headers):
    response = client.get("/api/analytics/s-north", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["totalTryOns"] == 0
    assert data["successful"] == 0
    assert data["failed"] == 0
    assert data["mostTriedProduct"] is None


def test_analytics_after_tryon(client, auth_headers):
    create_resp = client.post(
        "/api/tryon/sessions",
        data={"productId": "p-001", "consent": "true"},
        files={"personImage": ("person.png", _make_image_bytes(), "image/png")},
        headers=auth_headers,
    )
    session_id = create_resp.json()["id"]

    for _ in range(15):
        response = client.get(f"/api/tryon/sessions/{session_id}", headers=auth_headers)
        data = response.json()
        if data["status"] != "processing":
            break
        time.sleep(1)

    analytics = client.get("/api/analytics/s-north", headers=auth_headers).json()
    assert analytics["totalTryOns"] == 1
    if data["status"] == "completed":
        assert analytics["successful"] == 1
    else:
        assert analytics["failed"] == 1
    assert analytics["mostTriedProduct"] is not None
    assert analytics["mostTriedProduct"]["name"] == "Oversized Cotton Tee"

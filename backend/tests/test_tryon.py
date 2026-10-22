import io
import time
import json


def _make_image_bytes():
    return io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x05\xfe\xd4\x00\x00\x00\x00IEND\xaeB`\x82')


def test_create_tryon_session(client, auth_headers):
    response = client.post(
        "/api/tryon/sessions",
        data={
            "productId": "p-001",
            "consent": "true",
        },
        files={"personImage": ("person.png", _make_image_bytes(), "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    session = response.json()
    assert session["status"] == "processing"
    assert session["productId"] == "p-001"
    assert session["personImage"].startswith("/api/files/persons/")


def test_poll_tryon_session(client, auth_headers):
    create_resp = client.post(
        "/api/tryon/sessions",
        data={
            "productId": "p-001",
            "consent": "true",
        },
        files={"personImage": ("person.png", _make_image_bytes(), "image/png")},
        headers=auth_headers,
    )
    session_id = create_resp.json()["id"]

    for _ in range(15):
        response = client.get(f"/api/tryon/sessions/{session_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        if data["status"] != "processing":
            break
        time.sleep(1)

    assert data["status"] in ("completed", "failed")
    if data["status"] == "completed":
        assert data["resultImage"] is not None
        assert data["resultImage"].startswith("/api/files/results/")


def test_tryon_session_not_found(client, auth_headers):
    response = client.get("/api/tryon/sessions/nonexistent", headers=auth_headers)
    assert response.status_code == 404


def test_tryon_unauthorized(client):
    response = client.post(
        "/api/tryon/sessions",
        data={"productId": "p-001", "consent": "true"},
        files={"personImage": ("person.png", _make_image_bytes(), "image/png")},
    )
    assert response.status_code == 401

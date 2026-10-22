def test_list_stores(client):
    response = client.get("/api/stores")
    assert response.status_code == 200
    stores = response.json()
    assert len(stores) >= 2
    assert any(s["slug"] == "north-studio" for s in stores)


def test_get_store_by_slug(client):
    response = client.get("/api/stores/north-studio")
    assert response.status_code == 200
    store = response.json()
    assert store["name"] == "North Studio"
    assert store["slug"] == "north-studio"


def test_get_store_not_found(client):
    response = client.get("/api/stores/nonexistent")
    assert response.status_code == 404


def test_create_store(client, auth_headers):
    response = client.post("/api/stores", json={
        "name": "Test Store",
        "slug": "test-store",
        "tagline": "A test store",
        "description": "For testing",
    }, headers=auth_headers)
    assert response.status_code == 200
    store = response.json()
    assert store["name"] == "Test Store"
    assert store["slug"] == "test-store"


def test_create_store_duplicate_slug(client, auth_headers):
    response = client.post("/api/stores", json={
        "name": "North Studio 2",
        "slug": "north-studio",
        "tagline": "Copy",
        "description": "Copy",
    }, headers=auth_headers)
    assert response.status_code == 400


def test_create_store_unauthorized(client):
    response = client.post("/api/stores", json={
        "name": "Test",
        "slug": "test",
        "tagline": "",
        "description": "",
    })
    assert response.status_code == 401


def test_update_store(client, auth_headers):
    create_resp = client.post("/api/stores", json={
        "name": "Update Test",
        "slug": "update-test",
        "tagline": "Before",
        "description": "Before",
    }, headers=auth_headers)
    store_id = create_resp.json()["id"]

    response = client.patch(f"/api/stores/{store_id}", json={
        "name": "Updated Name",
        "tagline": "After",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert response.json()["tagline"] == "After"

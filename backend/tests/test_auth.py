def test_register(client):
    response = client.post("/api/auth/register", json={
        "email": "newuser@test.com",
        "password": "password123",
        "role": "customer",
        "displayName": "New User",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "newuser@test.com"
    assert data["user"]["role"] == "customer"
    assert data["user"]["displayName"] == "New User"


def test_register_duplicate(client):
    response = client.post("/api/auth/register", json={
        "email": "store@north.co",
        "password": "password123",
        "role": "customer",
        "displayName": "Dup",
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client):
    response = client.post("/api/auth/login", json={
        "email": "store@north.co",
        "password": "store123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "store@north.co"
    assert data["user"]["role"] == "store_owner"


def test_login_wrong_password(client):
    response = client.post("/api/auth/login", json={
        "email": "store@north.co",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_login_nonexistent(client):
    response = client.post("/api/auth/login", json={
        "email": "nobody@test.com",
        "password": "password123",
    })
    assert response.status_code == 401


def test_refresh_token(client):
    login_resp = client.post("/api/auth/login", json={
        "email": "store@north.co",
        "password": "store123",
    })
    refresh_token = login_resp.json()["refresh_token"]

    response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_logout(client):
    response = client.post("/api/auth/logout")
    assert response.status_code == 200


def test_me_endpoint(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "store@north.co"


def test_me_without_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_admin_list_users(client, admin_headers):
    response = client.get("/api/admin/users", headers=admin_headers)
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 3


def test_admin_list_users_non_admin(client, auth_headers):
    response = client.get("/api/admin/users", headers=auth_headers)
    assert response.status_code == 403


def test_toggle_user_disabled(client, admin_headers):
    response = client.patch("/api/admin/users/u-owner-1/toggle-disabled", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["disabled"] is True

    response = client.patch("/api/admin/users/u-owner-1/toggle-disabled", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["disabled"] is False


def test_admin_list_sessions(client, admin_headers):
    response = client.get("/api/admin/sessions", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_failed_sessions(client, admin_headers):
    response = client.get("/api/admin/sessions/failed", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

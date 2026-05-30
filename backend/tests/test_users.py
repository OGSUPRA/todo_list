from __future__ import annotations

from fastapi.testclient import TestClient


def test_profile_avatar_password_and_delete_flow(client: TestClient, auth_headers: dict[str, str]) -> None:
    update_profile_response = client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"username": "tester-updated", "email": "tester-updated@example.com"},
    )
    assert update_profile_response.status_code == 200
    assert update_profile_response.json()["username"] == "tester-updated"

    upload_response = client.post(
        "/api/v1/users/me/avatar",
        headers=auth_headers,
        files={"file": ("avatar.png", b"fake-image-bytes", "image/png")},
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["avatar_path"].startswith("/media/avatars/")

    password_response = client.post(
        "/api/v1/users/me/password",
        headers=auth_headers,
        json={"current_password": "strong-password", "new_password": "new-strong-password"},
    )
    assert password_response.status_code == 200

    stale_profile_response = client.get("/api/v1/users/me", headers=auth_headers)
    assert stale_profile_response.status_code == 401

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "tester-updated", "password": "new-strong-password"},
    )
    fresh_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    delete_response = client.delete("/api/v1/users/me", headers=fresh_headers)
    assert delete_response.status_code == 200

    after_delete_response = client.get("/api/v1/users/me", headers=fresh_headers)
    assert after_delete_response.status_code == 401

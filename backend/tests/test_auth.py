from __future__ import annotations

from fastapi.testclient import TestClient


def test_healthcheck_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_login_me_refresh_and_logout_flow(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "anna",
            "email": "anna@example.com",
            "password": "strong-password",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["username"] == "anna"
    assert register_response.json()["role"] == "standard"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "anna", "password": "strong-password"},
    )
    assert login_response.status_code == 200
    assert login_response.cookies.get("todo_refresh_token")
    assert login_response.cookies.get("todo_refresh_token", path="/")

    token = login_response.json()["access_token"]
    me_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "anna@example.com"

    client.cookies.set("todo_refresh_token", login_response.cookies.get("todo_refresh_token"))
    refresh_response = client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 200
    refreshed_token = refresh_response.json()["access_token"]
    assert refreshed_token

    logout_response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {refreshed_token}"},
    )
    assert logout_response.status_code == 200

    stale_me_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refreshed_token}"})
    assert stale_me_response.status_code == 401


def test_admin_access_requires_admin_refresh_cookie(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "member",
            "email": "member@example.com",
            "password": "strong-password",
        },
    )
    member_login = client.post(
        "/api/v1/auth/login",
        json={"username": "member", "password": "strong-password"},
    )
    client.cookies.set("todo_refresh_token", member_login.cookies.get("todo_refresh_token"))

    forbidden_response = client.get("/api/v1/auth/admin-access")
    assert forbidden_response.status_code == 403

    client.cookies.clear()
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "chief",
            "email": "admin@example.com",
            "password": "strong-password",
        },
    )
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"username": "chief", "password": "strong-password"},
    )
    client.cookies.set("todo_refresh_token", admin_login.cookies.get("todo_refresh_token"))

    allowed_response = client.get("/api/v1/auth/admin-access")
    assert allowed_response.status_code == 204


def test_login_rejects_invalid_password(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "boris",
            "email": "boris@example.com",
            "password": "strong-password",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "boris", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_rate_limit_blocks_excessive_login_attempts(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "limit-user",
            "email": "limit-user@example.com",
            "password": "strong-password",
        },
        headers={"X-Forwarded-For": "10.0.0.55"},
    )

    last_response = None
    for _ in range(21):
        last_response = client.post(
            "/api/v1/auth/login",
            json={"username": "limit-user", "password": "wrong-password"},
            headers={"X-Forwarded-For": "10.0.0.55"},
        )

    assert last_response is not None
    assert last_response.status_code == 429

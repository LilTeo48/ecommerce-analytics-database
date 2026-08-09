from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "email": "pytest_user@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code in (201, 409)


def test_login_user():
    client.post(
        "/auth/register",
        json={
            "email": "pytest_login@example.com",
            "password": "Password123!",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "pytest_login@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    client.post(
        "/auth/register",
        json={
            "email": "pytest_wrong@example.com",
            "password": "Password123!",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "pytest_wrong@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_protected_route_without_token():
    response = client.get("/customers/")

    assert response.status_code == 401


def test_protected_route_with_token():
    email = "pytest_protected@example.com"
    password = "Password123!"

    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/customers/",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
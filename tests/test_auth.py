from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app

client = TestClient(app)


def test_register_user():
    email = f"pytest_user_{uuid4().hex}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == email
    assert data["is_active"] is True
    assert "user_id" in data


def test_duplicate_registration():
    email = f"pytest_duplicate_{uuid4().hex}@example.com"
    password = "Password123!"

    first_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert first_response.status_code == 201

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 409


def test_login_user():
    email = f"pytest_login_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    email = f"pytest_wrong_{uuid4().hex}@example.com"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123!",
        },
    )

    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_protected_route_without_token():
    response = client.get("/customers/")

    assert response.status_code == 401


def test_protected_route_with_invalid_token():
    response = client.get(
        "/customers/",
        headers={
            "Authorization": "Bearer definitely-not-a-valid-jwt"
        },
    )

    assert response.status_code == 401


def test_protected_route_with_token():
    email = f"pytest_protected_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/customers/",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
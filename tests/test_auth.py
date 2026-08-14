from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import SessionLocal
from app.main import app
from app.models import User

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
    assert data["role"] == "user"
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
    assert response.json() == {
        "detail": "A user with this email already exists."
    }


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
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    assert data["access_token"]
    assert data["refresh_token"]
    assert data["access_token"] != data["refresh_token"]


def test_login_updates_last_login_at():
    email = f"pytest_last_login_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        assert user is not None
        assert user.last_login_at is None

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        assert user is not None
        assert user.last_login_at is not None


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
    assert response.json() == {
        "detail": "Invalid email or password."
    }


def test_refresh_token_creates_new_tokens():
    email = f"pytest_refresh_{uuid4().hex}@example.com"
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

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    assert data["access_token"]
    assert data["refresh_token"]


def test_access_token_cannot_be_used_as_refresh_token():
    email = f"pytest_access_refresh_{uuid4().hex}@example.com"
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

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": access_token,
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid refresh token."
    }


def test_invalid_refresh_token():
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": "definitely-not-a-valid-jwt",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid refresh token."
    }


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


def test_refresh_token_cannot_access_protected_route():
    email = f"pytest_refresh_protected_{uuid4().hex}@example.com"
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

    refresh_token = login_response.json()["refresh_token"]

    response = client.get(
        "/customers/",
        headers={
            "Authorization": f"Bearer {refresh_token}"
        },
    )

    assert response.status_code == 401

def test_refresh_token_cannot_be_reused():
    email = f"pytest_rotation_{uuid4().hex}@example.com"
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

    original_refresh_token = (
        login_response.json()["refresh_token"]
    )

    # First use should succeed.
    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": original_refresh_token,
        },
    )

    assert refresh_response.status_code == 200

    # The original token was revoked during rotation,
    # so attempting to use it again must fail.
    reuse_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": original_refresh_token,
        },
    )

    assert reuse_response.status_code == 401


def test_rotated_refresh_token_can_be_used():
    email = f"pytest_rotated_{uuid4().hex}@example.com"
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

    assert login_response.status_code == 200

    original_refresh_token = (
        login_response.json()["refresh_token"]
    )

    first_refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": original_refresh_token,
        },
    )

    assert first_refresh_response.status_code == 200

    new_refresh_token = (
        first_refresh_response.json()["refresh_token"]
    )

    assert new_refresh_token != original_refresh_token

    # The newly rotated refresh token should work.
    second_refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": new_refresh_token,
        },
    )

    assert second_refresh_response.status_code == 200


def test_logout_revokes_refresh_token():
    email = f"pytest_logout_{uuid4().hex}@example.com"
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

    assert login_response.status_code == 200

    refresh_token = (
        login_response.json()["refresh_token"]
    )

    logout_response = client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert logout_response.status_code == 200
    assert logout_response.json() == {
        "detail": "Logged out successfully.",
    }

    # Logged-out refresh token must no longer work.
    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert refresh_response.status_code == 401


def test_revoked_refresh_token_cannot_logout_again():
    email = f"pytest_double_logout_{uuid4().hex}@example.com"
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

    refresh_token = (
        login_response.json()["refresh_token"]
    )

    first_logout_response = client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert first_logout_response.status_code == 200

    second_logout_response = client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert second_logout_response.status_code == 401

def test_change_password_success():
    email = f"pytest_change_password_{uuid4().hex}@example.com"
    old_password = "Password123!"
    new_password = "NewPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": old_password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/auth/change-password",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "current_password": old_password,
            "new_password": new_password,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "detail": "Password changed successfully.",
    }


def test_change_password_wrong_current_password():
    email = f"pytest_wrong_current_{uuid4().hex}@example.com"
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

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/auth/change-password",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Current password is incorrect.",
    }


def test_change_password_rejects_same_password():
    email = f"pytest_same_password_{uuid4().hex}@example.com"
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

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/auth/change-password",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "current_password": password,
            "new_password": password,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "New password must be different "
            "from current password."
        ),
    }


def test_old_password_fails_after_password_change():
    email = f"pytest_old_password_{uuid4().hex}@example.com"
    old_password = "Password123!"
    new_password = "NewPassword123!"

    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": old_password,
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )

    access_token = login_response.json()["access_token"]

    change_response = client.post(
        "/auth/change-password",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "current_password": old_password,
            "new_password": new_password,
        },
    )

    assert change_response.status_code == 200

    old_login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )

    assert old_login_response.status_code == 401


def test_new_password_works_after_password_change():
    email = f"pytest_new_password_{uuid4().hex}@example.com"
    old_password = "Password123!"
    new_password = "NewPassword123!"

    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": old_password,
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )

    access_token = login_response.json()["access_token"]

    change_response = client.post(
        "/auth/change-password",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "current_password": old_password,
            "new_password": new_password,
        },
    )

    assert change_response.status_code == 200

    new_login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": new_password,
        },
    )

    assert new_login_response.status_code == 200
    assert "access_token" in new_login_response.json()
    assert "refresh_token" in new_login_response.json()


def test_change_password_revokes_existing_refresh_tokens():
    email = f"pytest_revoke_sessions_{uuid4().hex}@example.com"
    old_password = "Password123!"
    new_password = "NewPassword123!"

    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": old_password,
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )

    access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    change_response = client.post(
        "/auth/change-password",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "current_password": old_password,
            "new_password": new_password,
        },
    )

    assert change_response.status_code == 200

    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert refresh_response.status_code == 401
    assert refresh_response.json() == {
        "detail": "Refresh token has been revoked.",
    }        
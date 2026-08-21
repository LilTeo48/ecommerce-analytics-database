from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import SessionLocal
from app.main import app
from app.models import User


client = TestClient(app)

def verify_test_user(email: str) -> None:
    """
    Mark a test user as email verified.

    Existing authentication tests use this helper so they can
    continue testing login, refresh tokens, password changes,
    lockouts, deactivation, and other authenticated behavior
    independently from the email-verification flow.
    """
    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        assert user is not None

        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires_at = None

        db.commit()        


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

    verify_test_user(email)

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

def test_oauth2_token_login():
    email = f"pytest_oauth_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    response = client.post(
        "/auth/token",
        data={
            "username": email,
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

    verify_test_user(email)

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
    email = f"pytest_wrong_password_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid email or password."
    )

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

    verify_test_user(email)

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

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

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

    verify_test_user(email)

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

    verify_test_user(email)

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

    verify_test_user(email)

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

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

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

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

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

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

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

    verify_test_user(email)

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

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

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

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

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

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": old_password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )

    assert login_response.status_code == 200

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

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": old_password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )

    assert login_response.status_code == 200

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

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": old_password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )

    assert login_response.status_code == 200

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

def test_logout_all_requires_authentication():
    response = client.post(
        "/auth/logout-all"
    )

    assert response.status_code == 401


def test_logout_all_revokes_multiple_refresh_tokens():
    email = f"pytest_logout_all_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    first_login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    second_login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert first_login.status_code == 200
    assert second_login.status_code == 200

    first_access_token = (
        first_login.json()["access_token"]
    )
    first_refresh_token = (
        first_login.json()["refresh_token"]
    )
    second_refresh_token = (
        second_login.json()["refresh_token"]
    )

    logout_all_response = client.post(
        "/auth/logout-all",
        headers={
            "Authorization": f"Bearer {first_access_token}"
        },
    )

    assert logout_all_response.status_code == 200
    assert logout_all_response.json() == {
        "detail": "All sessions logged out successfully.",
    }

    first_refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": first_refresh_token,
        },
    )

    second_refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": second_refresh_token,
        },
    )

    assert first_refresh_response.status_code == 401
    assert second_refresh_response.status_code == 401

def test_fresh_login_works_after_logout_all():
    email = f"pytest_logout_all_login_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    logout_all_response = client.post(
        "/auth/logout-all",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert logout_all_response.status_code == 200

    fresh_login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert fresh_login_response.status_code == 200
    assert "access_token" in fresh_login_response.json()
    assert "refresh_token" in fresh_login_response.json()

def test_get_current_user_requires_authentication():
    response = client.get(
        "/auth/me"
    )

    assert response.status_code == 401


def test_get_current_user_with_invalid_token():
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": (
                "Bearer definitely-not-a-valid-jwt"
            )
        },
    )

    assert response.status_code == 401


def test_get_current_user_returns_authenticated_user():
    email = f"pytest_me_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    user_id = register_response.json()["user_id"]

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    access_token = (
        login_response.json()["access_token"]
    )

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == user_id
    assert data["email"] == email
    assert data["role"] == "user"
    assert data["is_active"] is True

def test_refresh_token_cannot_access_current_user():
    email = f"pytest_me_refresh_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

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

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {refresh_token}"
        },
    )

    assert response.status_code == 401

def test_deactivate_account_requires_authentication() -> None:
    response = client.post(
        "/auth/deactivate",
        json={
            "password": "Password123!",
        },
    )

    assert response.status_code == 401


def test_deactivate_account_wrong_password() -> None:
    email = f"pytest_deactivate_wrong_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

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
        "/auth/deactivate",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Password is incorrect.",
    }

def test_deactivate_account_success() -> None:
    email = f"pytest_deactivate_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    tokens = login_response.json()

    response = client.post(
        "/auth/deactivate",
        headers={
            "Authorization": (
                f"Bearer {tokens['access_token']}"
            ),
        },
        json={
            "password": password,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "detail": "Account deactivated successfully.",
    }


def test_deactivated_user_cannot_login() -> None:
    email = f"pytest_deactivated_login_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()[
        "access_token"
    ]

    deactivate_response = client.post(
        "/auth/deactivate",
        headers={
            "Authorization": (
                f"Bearer {access_token}"
            ),
        },
        json={
            "password": password,
        },
    )

    assert deactivate_response.status_code == 200

    second_login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert second_login_response.status_code == 403
    assert second_login_response.json() == {
        "detail": "User account is inactive.",
    }

def test_deactivation_revokes_refresh_token() -> None:
    email = f"pytest_deactivated_refresh_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    tokens = login_response.json()

    deactivate_response = client.post(
        "/auth/deactivate",
        headers={
            "Authorization": (
                f"Bearer {tokens['access_token']}"
            ),
        },
        json={
            "password": password,
        },
    )

    assert deactivate_response.status_code == 200

    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": tokens[
                "refresh_token"
            ],
        },
    )

    assert refresh_response.status_code == 401
    assert refresh_response.json() == {
        "detail": "Refresh token has been revoked.",
    }


def test_deactivated_user_access_token_stops_working() -> None:
    email = f"pytest_deactivated_access_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()[
        "access_token"
    ]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    deactivate_response = client.post(
        "/auth/deactivate",
        headers=headers,
        json={
            "password": password,
        },
    )

    assert deactivate_response.status_code == 200

    me_response = client.get(
        "/auth/me",
        headers=headers,
    )

    assert me_response.status_code == 403
    assert me_response.json() == {
        "detail": "User account is inactive.",
    }

def test_failed_login_attempts_eventually_lock_account():
    email = f"pytest_lockout_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    # Five bad passwords trigger the lockout.
    for _ in range(5):
        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    # Even the correct password should now be rejected
    # while the account is temporarily locked.
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 429
    assert response.json()["detail"] == (
        "Account is temporarily locked. "
        "Please try again later."
    )


def test_successful_login_resets_failed_attempts():
    email = f"pytest_reset_attempts_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    # Accumulate failures without reaching the lockout threshold.
    for _ in range(3):
        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    # A successful login should reset the counter.
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    # Four more failures should still not lock the account,
    # proving the previous three failures were reset.
    for _ in range(4):
        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200


def test_expired_lockout_allows_login():
    email = f"pytest_expired_lock_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    # Trigger the account lockout with five failed attempts.
    for _ in range(5):
        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    # Confirm that the account is currently locked.
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 429
    assert response.json()["detail"] == (
        "Account is temporarily locked. "
        "Please try again later."
    )

    # Simulate the 15-minute lockout having expired
    # by moving locked_until into the past.
    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        assert user is not None

        user.locked_until = (
            datetime.now(timezone.utc)
            .replace(tzinfo=None)
            - timedelta(minutes=1)
        )

        db.commit()

    # The correct password should work once
    # the temporary lockout has expired.
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

def test_registration_creates_verification_token():
    email = f"pytest_verify_token_{uuid4().hex}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123!",
        },
    )

    assert response.status_code == 201

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        assert user is not None
        assert user.is_verified is False
        assert user.verification_token is not None
        assert user.verification_token_expires_at is not None

def test_registration_sends_verification_email(
    monkeypatch,
):
    email = f"pytest_email_send_{uuid4().hex}@example.com"
    password = "Password123!"

    captured = {}

    def fake_send_verification_email(
        sent_email,
        verification_token,
    ):
        captured["email"] = sent_email
        captured["token"] = verification_token

    monkeypatch.setattr(
        "app.auth.send_verification_email",
        fake_send_verification_email,
    )

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        assert user is not None
        assert user.verification_token is not None

        assert captured["email"] == email
        assert captured["token"] == user.verification_token

def test_verify_email_success():
    email = f"pytest_verify_success_{uuid4().hex}@example.com"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123!",
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
        token = user.verification_token

    assert token is not None

    response = client.post(
        "/auth/verify-email",
        json={
            "verification_token": token,
        },
    )

    assert response.status_code == 200
    assert response.json()["detail"] == (
        "Email verified successfully."
    )

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        assert user is not None
        assert user.is_verified is True
        assert user.verification_token is None
        assert user.verification_token_expires_at is None


def test_verify_email_invalid_token():
    response = client.post(
        "/auth/verify-email",
        json={
            "verification_token": "not-a-real-verification-token",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid verification token."
    )


def test_verify_email_expired_token():
    email = f"pytest_verify_expired_{uuid4().hex}@example.com"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123!",
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
        assert user.verification_token is not None

        token = user.verification_token

        user.verification_token_expires_at = (
            datetime.now(timezone.utc)
            .replace(tzinfo=None)
            - timedelta(minutes=1)
        )

        db.commit()

    response = client.post(
        "/auth/verify-email",
        json={
            "verification_token": token,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Verification token has expired."
    )


def test_verification_token_cannot_be_reused():
    email = f"pytest_verify_reuse_{uuid4().hex}@example.com"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123!",
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
        token = user.verification_token

    assert token is not None

    first_response = client.post(
        "/auth/verify-email",
        json={
            "verification_token": token,
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/auth/verify-email",
        json={
            "verification_token": token,
        },
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == (
        "Invalid verification token."
    )

def get_password_reset_token(email: str) -> str:
    response = client.post(
        "/auth/forgot-password",
        json={
            "email": email,
        },
    )

    assert response.status_code == 200

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        assert user is not None
        assert user.password_reset_token is not None

        return user.password_reset_token

def test_forgot_password_generates_reset_token():
    email = f"pytest_forgot_{uuid4().hex}@example.com"
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
        "/auth/forgot-password",
        json={
            "email": email,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "detail": (
            "If an account with that email exists, "
            "a password reset link has been generated."
        )
    }

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        assert user is not None
        assert user.password_reset_token is not None
        assert user.password_reset_token_expires_at is not None


def test_forgot_password_unknown_email_returns_generic_response():
    email = f"missing_{uuid4().hex}@example.com"

    response = client.post(
        "/auth/forgot-password",
        json={
            "email": email,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "detail": (
            "If an account with that email exists, "
            "a password reset link has been generated."
        )
    }

def test_forgot_password_sends_reset_email(
    monkeypatch,
):
    email = f"pytest_reset_email_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    captured = {}

    def fake_send_password_reset_email(
        sent_email,
        reset_token,
    ):
        captured["email"] = sent_email
        captured["token"] = reset_token

    monkeypatch.setattr(
        "app.auth.send_password_reset_email",
        fake_send_password_reset_email,
    )

    response = client.post(
        "/auth/forgot-password",
        json={
            "email": email,
        },
    )

    assert response.status_code == 200

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        assert user is not None
        assert user.password_reset_token is not None

        assert captured["email"] == email
        assert captured["token"] == user.password_reset_token


def test_reset_password_success():
    email = f"pytest_reset_{uuid4().hex}@example.com"
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

    token = get_password_reset_token(email)

    response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": new_password,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "detail": "Password reset successfully.",
    }


def test_reset_password_invalid_token():
    response = client.post(
        "/auth/reset-password",
        json={
            "token": "invalid-token",
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid password reset token.",
    }


def test_reset_password_expired_token():
    email = f"pytest_reset_expired_{uuid4().hex}@example.com"
    password = "Password123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    token = get_password_reset_token(email)

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        assert user is not None

        user.password_reset_token_expires_at = (
            datetime.now(timezone.utc)
            .replace(tzinfo=None)
            - timedelta(minutes=1)
        )

        db.commit()

    response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Password reset token has expired.",
    }


def test_reset_password_token_cannot_be_reused():
    email = f"pytest_reset_reuse_{uuid4().hex}@example.com"
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

    token = get_password_reset_token(email)

    first_response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": new_password,
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": "AnotherPassword123!",
        },
    )

    assert second_response.status_code == 400
    assert second_response.json() == {
        "detail": "Invalid password reset token.",
    }


def test_old_password_fails_after_password_reset():
    email = f"pytest_reset_old_{uuid4().hex}@example.com"
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

    verify_test_user(email)

    token = get_password_reset_token(email)

    reset_response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": new_password,
        },
    )

    assert reset_response.status_code == 200

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )

    assert response.status_code == 401


def test_new_password_works_after_password_reset():
    email = f"pytest_reset_new_{uuid4().hex}@example.com"
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

    verify_test_user(email)

    token = get_password_reset_token(email)

    reset_response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": new_password,
        },
    )

    assert reset_response.status_code == 200

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": new_password,
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_password_reset_revokes_existing_refresh_tokens():
    email = f"pytest_reset_revoke_{uuid4().hex}@example.com"
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

    verify_test_user(email)

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    token = get_password_reset_token(email)

    reset_response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": new_password,
        },
    )

    assert reset_response.status_code == 200

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


def test_password_reset_clears_lockout_state():
    email = f"pytest_reset_lockout_{uuid4().hex}@example.com"
    password = "Password123!"
    new_password = "NewPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    verify_test_user(email)

    for _ in range(5):
        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    token = get_password_reset_token(email)

    reset_response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": new_password,
        },
    )

    assert reset_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": new_password,
        },
    )

    assert login_response.status_code == 200            


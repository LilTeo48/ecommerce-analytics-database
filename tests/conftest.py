import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

# Local pytest runs connect to Docker PostgreSQL through the host-mapped port.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/ecommerce_analytics",
)

from app.database import SessionLocal
from app.main import app
from app.models import User


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    email = f"pytest_{uuid4().hex}@example.com"
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

    return {
        "Authorization": f"Bearer {token}"
    }


@pytest.fixture
def authenticated_client(client, auth_headers):
    client.headers.update(auth_headers)
    return client


@pytest.fixture
def admin_client(client):
    email = f"pytest_admin_{uuid4().hex}@example.com"
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
            select(User).where(User.email == email)
        )

        assert user is not None

        user.role = "admin"

        db.commit()

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    client.headers.update(
        {
            "Authorization": f"Bearer {token}"
        }
    )

    return client
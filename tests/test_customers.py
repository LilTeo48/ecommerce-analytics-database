from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_customers() -> None:
    response = client.get("/customers/")

    assert response.status_code == 200

    customers = response.json()

    assert isinstance(customers, list)

    for customer in customers:
        assert "customer_id" in customer
        assert "first_name" in customer
        assert "last_name" in customer
        assert "email" in customer
        assert "signup_date" in customer


def test_get_customers_with_pagination() -> None:
    response = client.get(
        "/customers/",
        params={
            "skip": 0,
            "limit": 2,
        },
    )

    assert response.status_code == 200

    customers = response.json()

    assert isinstance(customers, list)
    assert len(customers) <= 2


def test_get_existing_customer() -> None:
    customers_response = client.get("/customers/")

    assert customers_response.status_code == 200

    customers = customers_response.json()

    if not customers:
        return

    customer_id = customers[0]["customer_id"]

    response = client.get(f"/customers/{customer_id}")

    assert response.status_code == 200

    customer = response.json()

    assert customer["customer_id"] == customer_id
    assert "email" in customer


def test_get_missing_customer() -> None:
    response = client.get("/customers/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Customer not found.",
    }


def test_invalid_customer_pagination() -> None:
    response = client.get(
        "/customers/",
        params={
            "skip": -1,
            "limit": 101,
        },
    )

    assert response.status_code == 422
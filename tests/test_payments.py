from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_payments() -> None:
    response = client.get("/payments/")

    assert response.status_code == 200

    payments = response.json()

    assert isinstance(payments, list)

    for payment in payments:
        assert "payment_id" in payment
        assert "order_id" in payment
        assert "payment_date" in payment
        assert "payment_method" in payment
        assert "amount" in payment


def test_get_payments_with_pagination() -> None:
    response = client.get(
        "/payments/",
        params={
            "skip": 0,
            "limit": 2,
        },
    )

    assert response.status_code == 200

    payments = response.json()

    assert isinstance(payments, list)
    assert len(payments) <= 2


def test_get_existing_payment() -> None:
    payments_response = client.get("/payments/")

    assert payments_response.status_code == 200

    payments = payments_response.json()

    if not payments:
        return

    payment_id = payments[0]["payment_id"]

    response = client.get(f"/payments/{payment_id}")

    assert response.status_code == 200

    payment = response.json()

    assert payment["payment_id"] == payment_id
    assert "order_id" in payment
    assert "payment_date" in payment
    assert "payment_method" in payment
    assert "amount" in payment


def test_get_payment_by_order() -> None:
    payments_response = client.get("/payments/")

    assert payments_response.status_code == 200

    payments = payments_response.json()

    if not payments:
        return

    order_id = payments[0]["order_id"]

    response = client.get(f"/payments/order/{order_id}")

    assert response.status_code == 200

    payment = response.json()

    assert payment["order_id"] == order_id
    assert "payment_id" in payment
    assert "amount" in payment


def test_get_missing_payment() -> None:
    response = client.get("/payments/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Payment not found.",
    }


def test_invalid_payment_pagination() -> None:
    response = client.get(
        "/payments/",
        params={
            "skip": -1,
            "limit": 101,
        },
    )

    assert response.status_code == 422
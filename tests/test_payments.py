def test_get_payments(authenticated_client) -> None:
    response = authenticated_client.get("/payments/")

    assert response.status_code == 200

    payments = response.json()

    assert isinstance(payments, list)

    for payment in payments:
        assert "payment_id" in payment
        assert "order_id" in payment
        assert "payment_date" in payment
        assert "payment_method" in payment
        assert "amount" in payment


def test_get_payments_with_pagination(authenticated_client) -> None:
    response = authenticated_client.get(
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


def test_get_existing_payment(authenticated_client) -> None:
    payments_response = authenticated_client.get("/payments/")

    assert payments_response.status_code == 200

    payments = payments_response.json()

    if not payments:
        return

    payment_id = payments[0]["payment_id"]

    response = authenticated_client.get(
        f"/payments/{payment_id}"
    )

    assert response.status_code == 200

    payment = response.json()

    assert payment["payment_id"] == payment_id
    assert "order_id" in payment
    assert "payment_date" in payment
    assert "payment_method" in payment
    assert "amount" in payment


def test_get_payment_by_order(authenticated_client) -> None:
    payments_response = authenticated_client.get("/payments/")

    assert payments_response.status_code == 200

    payments = payments_response.json()

    if not payments:
        return

    order_id = payments[0]["order_id"]

    response = authenticated_client.get(
        f"/payments/order/{order_id}"
    )

    assert response.status_code == 200

    payment = response.json()

    assert payment["order_id"] == order_id
    assert "payment_id" in payment
    assert "amount" in payment


def test_get_missing_payment(authenticated_client) -> None:
    response = authenticated_client.get(
        "/payments/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Payment not found.",
    }


def test_invalid_payment_pagination(
    authenticated_client,
) -> None:
    response = authenticated_client.get(
        "/payments/",
        params={
            "skip": -1,
            "limit": 101,
        },
    )

    assert response.status_code == 422


# -------------------------
# RBAC tests
# -------------------------

def test_regular_user_cannot_create_payment(
    authenticated_client,
) -> None:
    response = authenticated_client.post(
        "/payments/",
        json={
            "order_id": 1,
            "payment_date": "2026-08-13",
            "payment_method": "Credit Card",
            "amount": "49.99",
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin privileges required.",
    }


def test_regular_user_cannot_delete_payment(
    authenticated_client,
) -> None:
    response = authenticated_client.delete(
        "/payments/1"
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin privileges required.",
    }


def test_admin_can_manage_payment(admin_client) -> None:
    orders_response = admin_client.get("/orders/")

    assert orders_response.status_code == 200

    orders = orders_response.json()

    unpaid_order_id = None

    for order in orders:
        payment_response = admin_client.get(
            f"/payments/order/{order['order_id']}"
        )

        if payment_response.status_code == 404:
            unpaid_order_id = order["order_id"]
            break

    if unpaid_order_id is None:
        return

    create_response = admin_client.post(
        "/payments/",
        json={
            "order_id": unpaid_order_id,
            "payment_date": "2026-08-13",
            "payment_method": "Credit Card",
            "amount": "49.99",
        },
    )

    assert create_response.status_code == 201

    payment = create_response.json()
    payment_id = payment["payment_id"]

    assert payment["order_id"] == unpaid_order_id
    assert payment["payment_method"] == "Credit Card"

    delete_response = admin_client.delete(
        f"/payments/{payment_id}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["payment_id"] == payment_id
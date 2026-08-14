def test_get_orders(authenticated_client) -> None:
    response = authenticated_client.get("/orders/")

    assert response.status_code == 200

    orders = response.json()

    assert isinstance(orders, list)

    for order in orders:
        assert "order_id" in order
        assert "customer_id" in order
        assert "order_date" in order
        assert "order_status" in order
        assert "total_amount" in order


def test_get_orders_with_pagination(authenticated_client) -> None:
    response = authenticated_client.get(
        "/orders/",
        params={
            "skip": 0,
            "limit": 2,
        },
    )

    assert response.status_code == 200

    orders = response.json()

    assert isinstance(orders, list)
    assert len(orders) <= 2


def test_get_existing_order(authenticated_client) -> None:
    orders_response = authenticated_client.get("/orders/")

    assert orders_response.status_code == 200

    orders = orders_response.json()

    if not orders:
        return

    order_id = orders[0]["order_id"]

    response = authenticated_client.get(
        f"/orders/{order_id}"
    )

    assert response.status_code == 200

    order = response.json()

    assert order["order_id"] == order_id
    assert "customer_id" in order
    assert "order_status" in order
    assert "total_amount" in order


def test_get_missing_order(authenticated_client) -> None:
    response = authenticated_client.get(
        "/orders/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Order not found.",
    }


def test_invalid_order_pagination(
    authenticated_client,
) -> None:
    response = authenticated_client.get(
        "/orders/",
        params={
            "skip": -1,
            "limit": 101,
        },
    )

    assert response.status_code == 422


# -------------------------
# RBAC tests
# -------------------------

def test_regular_user_cannot_create_order(
    authenticated_client,
) -> None:
    response = authenticated_client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "order_date": "2026-08-13",
            "order_status": "Pending",
            "total_amount": "49.99",
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin privileges required.",
    }


def test_admin_can_create_order(admin_client) -> None:
    response = admin_client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "order_date": "2026-08-13",
            "order_status": "Pending",
            "total_amount": "49.99",
        },
    )

    assert response.status_code == 201

    order = response.json()

    assert order["customer_id"] == 1
    assert order["order_status"] == "Pending"
    assert float(order["total_amount"]) == 49.99
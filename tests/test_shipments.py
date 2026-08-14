from uuid import uuid4


def test_get_shipments(authenticated_client) -> None:
    response = authenticated_client.get("/shipments/")

    assert response.status_code == 200

    shipments = response.json()

    assert isinstance(shipments, list)

    for shipment in shipments:
        assert "shipment_id" in shipment
        assert "order_id" in shipment
        assert "shipment_date" in shipment
        assert "delivery_date" in shipment
        assert "shipping_status" in shipment


def test_get_shipments_with_pagination(authenticated_client) -> None:
    response = authenticated_client.get(
        "/shipments/",
        params={
            "skip": 0,
            "limit": 2,
        },
    )

    assert response.status_code == 200

    shipments = response.json()

    assert isinstance(shipments, list)
    assert len(shipments) <= 2


def test_get_existing_shipment(authenticated_client) -> None:
    shipments_response = authenticated_client.get("/shipments/")

    assert shipments_response.status_code == 200

    shipments = shipments_response.json()

    if not shipments:
        return

    shipment_id = shipments[0]["shipment_id"]

    response = authenticated_client.get(
        f"/shipments/{shipment_id}"
    )

    assert response.status_code == 200

    shipment = response.json()

    assert shipment["shipment_id"] == shipment_id
    assert "order_id" in shipment
    assert "shipping_status" in shipment


def test_get_shipment_by_order(authenticated_client) -> None:
    shipments_response = authenticated_client.get("/shipments/")

    assert shipments_response.status_code == 200

    shipments = shipments_response.json()

    if not shipments:
        return

    order_id = shipments[0]["order_id"]

    response = authenticated_client.get(
        f"/shipments/order/{order_id}"
    )

    assert response.status_code == 200

    shipment = response.json()

    assert shipment["order_id"] == order_id
    assert "shipment_id" in shipment
    assert "shipping_status" in shipment


def test_get_missing_shipment(authenticated_client) -> None:
    response = authenticated_client.get(
        "/shipments/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Shipment not found.",
    }


def test_invalid_shipment_pagination(
    authenticated_client,
) -> None:
    response = authenticated_client.get(
        "/shipments/",
        params={
            "skip": -1,
            "limit": 101,
        },
    )

    assert response.status_code == 422


# -------------------------
# RBAC tests
# -------------------------

def test_regular_user_cannot_create_shipment(
    authenticated_client,
) -> None:
    response = authenticated_client.post(
        "/shipments/",
        json={
            "order_id": 1,
            "shipment_date": "2026-08-13",
            "delivery_date": None,
            "shipping_status": "Processing",
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin privileges required.",
    }


def test_regular_user_cannot_update_shipment_status(
    authenticated_client,
) -> None:
    response = authenticated_client.patch(
        "/shipments/1/status",
        params={
            "shipping_status": "Shipped",
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin privileges required.",
    }


def test_regular_user_cannot_delete_shipment(
    authenticated_client,
) -> None:
    response = authenticated_client.delete(
        "/shipments/1"
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin privileges required.",
    }


def test_admin_can_manage_shipment(admin_client) -> None:
    customer_response = admin_client.post(
        "/customers/",
        json={
            "first_name": "Shipment",
            "last_name": "Tester",
            "email": f"shipment_rbac_{uuid4().hex}@example.com",
            "city": "Miami",
            "state": "FL",
            "signup_date": "2026-08-13",
        },
    )

    assert customer_response.status_code == 201

    customer_id = customer_response.json()["customer_id"]

    order_response = admin_client.post(
        "/orders/",
        json={
            "customer_id": customer_id,
            "order_date": "2026-08-13",
            "order_status": "Processing",
            "total_amount": "79.99",
        },
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["order_id"]

    create_response = admin_client.post(
        "/shipments/",
        json={
            "order_id": order_id,
            "shipment_date": "2026-08-13",
            "delivery_date": None,
            "shipping_status": "Processing",
        },
    )

    assert create_response.status_code == 201

    shipment = create_response.json()
    shipment_id = shipment["shipment_id"]

    assert shipment["order_id"] == order_id
    assert shipment["shipping_status"] == "Processing"

    update_response = admin_client.patch(
        f"/shipments/{shipment_id}/status",
        params={
            "shipping_status": "Shipped",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["shipping_status"] == "Shipped"

    delete_response = admin_client.delete(
        f"/shipments/{shipment_id}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["shipment_id"] == shipment_id
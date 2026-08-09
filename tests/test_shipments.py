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


def test_invalid_shipment_pagination(authenticated_client) -> None:
    response = authenticated_client.get(
        "/shipments/",
        params={
            "skip": -1,
            "limit": 101,
        },
    )

    assert response.status_code == 422
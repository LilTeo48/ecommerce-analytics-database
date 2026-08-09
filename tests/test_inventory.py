def test_get_inventory(authenticated_client) -> None:
    response = authenticated_client.get("/inventory/")

    assert response.status_code == 200

    inventory = response.json()

    assert isinstance(inventory, list)

    for product in inventory:
        assert "product_id" in product
        assert "product_name" in product
        assert "stock_quantity" in product


def test_get_inventory_with_pagination(authenticated_client) -> None:
    response = authenticated_client.get(
        "/inventory/",
        params={
            "skip": 0,
            "limit": 2,
        },
    )

    assert response.status_code == 200

    inventory = response.json()

    assert isinstance(inventory, list)
    assert len(inventory) <= 2


def test_get_existing_inventory_product(authenticated_client) -> None:
    inventory_response = authenticated_client.get("/inventory/")

    assert inventory_response.status_code == 200

    inventory = inventory_response.json()

    if not inventory:
        return

    product_id = inventory[0]["product_id"]

    response = authenticated_client.get(
        f"/inventory/{product_id}"
    )

    assert response.status_code == 200

    product = response.json()

    assert product["product_id"] == product_id
    assert "stock_quantity" in product


def test_get_missing_inventory_product(authenticated_client) -> None:
    response = authenticated_client.get(
        "/inventory/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found.",
    }


def test_get_low_stock_products(authenticated_client) -> None:
    response = authenticated_client.get(
        "/inventory/low-stock",
        params={
            "threshold": 100,
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_invalid_inventory_pagination(authenticated_client) -> None:
    response = authenticated_client.get(
        "/inventory/",
        params={
            "skip": -1,
            "limit": 101,
        },
    )

    assert response.status_code == 422


def test_invalid_stock_adjustment(authenticated_client) -> None:
    inventory_response = authenticated_client.get("/inventory/")

    assert inventory_response.status_code == 200

    inventory = inventory_response.json()

    if not inventory:
        return

    product_id = inventory[0]["product_id"]

    response = authenticated_client.patch(
        f"/inventory/{product_id}/adjust",
        json={
            "adjustment": 0,
        },
    )

    assert response.status_code == 422
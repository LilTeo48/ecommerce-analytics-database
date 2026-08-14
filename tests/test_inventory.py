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


def test_invalid_stock_adjustment(admin_client) -> None:
    inventory_response = admin_client.get("/inventory/")

    assert inventory_response.status_code == 200

    inventory = inventory_response.json()

    if not inventory:
        return

    product_id = inventory[0]["product_id"]

    response = admin_client.patch(
        f"/inventory/{product_id}/adjust",
        json={
            "adjustment": 0,
        },
    )

    assert response.status_code == 422


# -------------------------
# RBAC tests
# -------------------------

def test_regular_user_cannot_set_product_stock(
    authenticated_client,
) -> None:
    response = authenticated_client.put(
        "/inventory/1/stock",
        json={
            "stock_quantity": 50,
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin privileges required.",
    }


def test_regular_user_cannot_adjust_product_stock(
    authenticated_client,
) -> None:
    response = authenticated_client.patch(
        "/inventory/1/adjust",
        json={
            "adjustment": 5,
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin privileges required.",
    }


def test_admin_can_manage_inventory(admin_client) -> None:
    inventory_response = admin_client.get("/inventory/")

    assert inventory_response.status_code == 200

    inventory = inventory_response.json()

    if not inventory:
        return

    product = inventory[0]

    product_id = product["product_id"]
    original_stock = product["stock_quantity"]

    set_response = admin_client.put(
        f"/inventory/{product_id}/stock",
        json={
            "stock_quantity": original_stock + 10,
        },
    )

    assert set_response.status_code == 200
    assert (
        set_response.json()["stock_quantity"]
        == original_stock + 10
    )

    adjust_response = admin_client.patch(
        f"/inventory/{product_id}/adjust",
        json={
            "adjustment": -5,
        },
    )

    assert adjust_response.status_code == 200
    assert (
        adjust_response.json()["stock_quantity"]
        == original_stock + 5
    )

    restore_response = admin_client.put(
        f"/inventory/{product_id}/stock",
        json={
            "stock_quantity": original_stock,
        },
    )

    assert restore_response.status_code == 200
    assert (
        restore_response.json()["stock_quantity"]
        == original_stock
    )
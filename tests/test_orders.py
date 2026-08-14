from decimal import Decimal


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
    assert "order_items" in order
    assert isinstance(order["order_items"], list)


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
            "order_date": "2026-08-14",
            "order_status": "Pending",
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin privileges required.",
    }


# -------------------------
# Transactional order tests
# -------------------------

def test_admin_can_create_transactional_order(
    admin_client,
) -> None:
    products_response = admin_client.get("/products/")

    assert products_response.status_code == 200

    products = products_response.json()

    assert len(products) >= 2

    product_1 = products[0]
    product_2 = products[1]

    original_stock_1 = product_1["stock_quantity"]
    original_stock_2 = product_2["stock_quantity"]

    assert original_stock_1 >= 1
    assert original_stock_2 >= 1

    response = admin_client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "order_date": "2026-08-14",
            "order_status": "Pending",
            "items": [
                {
                    "product_id": product_1["product_id"],
                    "quantity": 1,
                },
                {
                    "product_id": product_2["product_id"],
                    "quantity": 1,
                },
            ],
        },
    )

    assert response.status_code == 201

    order = response.json()

    expected_total = (
        Decimal(product_1["price"])
        + Decimal(product_2["price"])
    )

    assert order["customer_id"] == 1
    assert order["order_status"] == "Pending"
    assert Decimal(order["total_amount"]) == expected_total

    assert len(order["order_items"]) == 2

    returned_product_ids = {
        item["product_id"]
        for item in order["order_items"]
    }

    assert returned_product_ids == {
        product_1["product_id"],
        product_2["product_id"],
    }

    inventory_1 = admin_client.get(
        f"/inventory/{product_1['product_id']}"
    )
    inventory_2 = admin_client.get(
        f"/inventory/{product_2['product_id']}"
    )

    assert inventory_1.status_code == 200
    assert inventory_2.status_code == 200

    assert (
        inventory_1.json()["stock_quantity"]
        == original_stock_1 - 1
    )
    assert (
        inventory_2.json()["stock_quantity"]
        == original_stock_2 - 1
    )


def test_order_uses_database_product_price(
    admin_client,
) -> None:
    products_response = admin_client.get("/products/")

    assert products_response.status_code == 200

    products = products_response.json()

    assert products

    product = products[0]

    if product["stock_quantity"] < 2:
        return

    response = admin_client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "order_date": "2026-08-14",
            "order_status": "Pending",
            "items": [
                {
                    "product_id": product["product_id"],
                    "quantity": 2,
                }
            ],
        },
    )

    assert response.status_code == 201

    order = response.json()

    expected_total = Decimal(product["price"]) * 2

    assert Decimal(order["total_amount"]) == expected_total
    assert (
        Decimal(order["order_items"][0]["unit_price"])
        == Decimal(product["price"])
    )


def test_create_order_with_missing_product(
    admin_client,
) -> None:
    response = admin_client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "order_date": "2026-08-14",
            "order_status": "Pending",
            "items": [
                {
                    "product_id": 999999,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product 999999 not found.",
    }


def test_create_order_with_insufficient_stock(
    admin_client,
) -> None:
    products_response = admin_client.get("/products/")

    assert products_response.status_code == 200

    products = products_response.json()

    assert products

    product = products[0]

    response = admin_client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "order_date": "2026-08-14",
            "order_status": "Pending",
            "items": [
                {
                    "product_id": product["product_id"],
                    "quantity": product["stock_quantity"] + 1,
                }
            ],
        },
    )

    assert response.status_code == 409
    assert "Insufficient stock" in response.json()["detail"]


def test_duplicate_products_are_rejected(
    admin_client,
) -> None:
    products_response = admin_client.get("/products/")

    assert products_response.status_code == 200

    products = products_response.json()

    assert products

    product_id = products[0]["product_id"]

    response = admin_client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "order_date": "2026-08-14",
            "order_status": "Pending",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                },
                {
                    "product_id": product_id,
                    "quantity": 1,
                },
            ],
        },
    )

    assert response.status_code == 422


def test_failed_order_does_not_reduce_inventory(
    admin_client,
) -> None:
    products_response = admin_client.get("/products/")

    assert products_response.status_code == 200

    products = products_response.json()

    assert products

    product = products[0]
    product_id = product["product_id"]
    original_stock = product["stock_quantity"]

    response = admin_client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "order_date": "2026-08-14",
            "order_status": "Pending",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                },
                {
                    "product_id": 999999,
                    "quantity": 1,
                },
            ],
        },
    )

    assert response.status_code == 404

    inventory_response = admin_client.get(
        f"/inventory/{product_id}"
    )

    assert inventory_response.status_code == 200

    assert (
        inventory_response.json()["stock_quantity"]
        == original_stock
    )
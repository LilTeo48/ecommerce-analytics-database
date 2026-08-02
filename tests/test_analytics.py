from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_revenue_summary() -> None:
    response = client.get("/analytics/revenue/summary")

    assert response.status_code == 200

    summary = response.json()

    assert "total_revenue" in summary
    assert "average_order_value" in summary
    assert "total_orders" in summary

    assert float(summary["total_revenue"]) >= 0
    assert float(summary["average_order_value"]) >= 0
    assert summary["total_orders"] >= 0


def test_monthly_revenue() -> None:
    response = client.get("/analytics/revenue/monthly")

    assert response.status_code == 200

    results = response.json()

    assert isinstance(results, list)

    for item in results:
        assert "month" in item
        assert "revenue" in item
        assert float(item["revenue"]) >= 0


def test_revenue_by_category() -> None:
    response = client.get("/analytics/revenue/by-category")

    assert response.status_code == 200

    results = response.json()

    assert isinstance(results, list)

    for item in results:
        assert "category" in item
        assert "revenue" in item
        assert float(item["revenue"]) >= 0


def test_top_selling_products() -> None:
    response = client.get(
        "/analytics/products/top-selling",
        params={"limit": 5},
    )

    assert response.status_code == 200

    products = response.json()

    assert isinstance(products, list)
    assert len(products) <= 5

    for product in products:
        assert "product_id" in product
        assert "product_name" in product
        assert "units_sold" in product
        assert "revenue" in product

        assert product["product_id"] > 0
        assert product["units_sold"] >= 0
        assert float(product["revenue"]) >= 0


def test_top_customers() -> None:
    response = client.get(
        "/analytics/customers/top",
        params={"limit": 5},
    )

    assert response.status_code == 200

    customers = response.json()

    assert isinstance(customers, list)
    assert len(customers) <= 5

    for customer in customers:
        assert "customer_id" in customer
        assert "first_name" in customer
        assert "last_name" in customer
        assert "total_orders" in customer
        assert "total_spent" in customer

        assert customer["customer_id"] > 0
        assert customer["total_orders"] >= 0
        assert float(customer["total_spent"]) >= 0


def test_orders_by_status() -> None:
    response = client.get("/analytics/orders/by-status")

    assert response.status_code == 200

    results = response.json()

    assert isinstance(results, list)

    for item in results:
        assert "order_status" in item
        assert "total_orders" in item
        assert "total_revenue" in item

        assert item["total_orders"] >= 0
        assert float(item["total_revenue"]) >= 0


def test_payments_by_method() -> None:
    response = client.get("/analytics/payments/by-method")

    assert response.status_code == 200

    results = response.json()

    assert isinstance(results, list)

    for item in results:
        assert "payment_method" in item
        assert "payment_count" in item
        assert "total_amount" in item

        assert item["payment_count"] >= 0
        assert float(item["total_amount"]) >= 0


def test_shipments_by_status() -> None:
    response = client.get("/analytics/shipments/by-status")

    assert response.status_code == 200

    results = response.json()

    assert isinstance(results, list)

    for item in results:
        assert "shipping_status" in item
        assert "shipment_count" in item
        assert item["shipment_count"] >= 0


def test_inventory_value() -> None:
    response = client.get("/analytics/inventory/value")

    assert response.status_code == 200

    inventory = response.json()

    assert "total_units" in inventory
    assert "total_inventory_value" in inventory

    assert inventory["total_units"] >= 0
    assert float(inventory["total_inventory_value"]) >= 0


def test_never_ordered_products() -> None:
    response = client.get("/analytics/products/never-ordered")

    assert response.status_code == 200

    products = response.json()

    assert isinstance(products, list)

    for product in products:
        assert "product_id" in product
        assert "product_name" in product
        assert "category" in product
        assert "stock_quantity" in product

        assert product["product_id"] > 0
        assert product["stock_quantity"] >= 0


def test_invalid_top_products_limit() -> None:
    response = client.get(
        "/analytics/products/top-selling",
        params={"limit": 101},
    )

    assert response.status_code == 422


def test_invalid_top_customers_limit() -> None:
    response = client.get(
        "/analytics/customers/top",
        params={"limit": 0},
    )

    assert response.status_code == 422
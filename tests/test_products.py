def test_get_products(authenticated_client) -> None:
    response = authenticated_client.get("/products/")

    assert response.status_code == 200

    products = response.json()

    assert isinstance(products, list)

    for product in products:
        assert "product_id" in product
        assert "product_name" in product
        assert "category" in product
        assert "price" in product
        assert "stock_quantity" in product


def test_get_products_with_pagination(authenticated_client) -> None:
    response = authenticated_client.get(
        "/products/",
        params={
            "skip": 0,
            "limit": 2,
        },
    )

    assert response.status_code == 200

    products = response.json()

    assert isinstance(products, list)
    assert len(products) <= 2


def test_get_existing_product(authenticated_client) -> None:
    products_response = authenticated_client.get("/products/")

    assert products_response.status_code == 200

    products = products_response.json()

    if not products:
        return

    product_id = products[0]["product_id"]

    response = authenticated_client.get(
        f"/products/{product_id}"
    )

    assert response.status_code == 200

    product = response.json()

    assert product["product_id"] == product_id
    assert "product_name" in product
    assert "price" in product
    assert "stock_quantity" in product


def test_get_missing_product(authenticated_client) -> None:
    response = authenticated_client.get(
        "/products/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found.",
    }


def test_invalid_product_pagination(
    authenticated_client,
) -> None:
    response = authenticated_client.get(
        "/products/",
        params={
            "skip": -1,
            "limit": 101,
        },
    )

    assert response.status_code == 422
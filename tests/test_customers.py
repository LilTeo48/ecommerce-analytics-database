def test_get_customers(authenticated_client) -> None:
    response = authenticated_client.get("/customers/")

    assert response.status_code == 200

    customers = response.json()

    assert isinstance(customers, list)

    for customer in customers:
        assert "customer_id" in customer
        assert "first_name" in customer
        assert "last_name" in customer
        assert "email" in customer
        assert "signup_date" in customer


def test_get_customers_with_pagination(authenticated_client) -> None:
    response = authenticated_client.get(
        "/customers/",
        params={
            "skip": 0,
            "limit": 2,
        },
    )

    assert response.status_code == 200

    customers = response.json()

    assert isinstance(customers, list)
    assert len(customers) <= 2


def test_get_existing_customer(authenticated_client) -> None:
    customers_response = authenticated_client.get("/customers/")

    assert customers_response.status_code == 200

    customers = customers_response.json()

    if not customers:
        return

    customer_id = customers[0]["customer_id"]

    response = authenticated_client.get(
        f"/customers/{customer_id}"
    )

    assert response.status_code == 200

    customer = response.json()

    assert customer["customer_id"] == customer_id
    assert "email" in customer


def test_get_missing_customer(authenticated_client) -> None:
    response = authenticated_client.get(
        "/customers/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Customer not found.",
    }


def test_invalid_customer_pagination(
    authenticated_client,
) -> None:
    response = authenticated_client.get(
        "/customers/",
        params={
            "skip": -1,
            "limit": 101,
        },
    )

    assert response.status_code == 422
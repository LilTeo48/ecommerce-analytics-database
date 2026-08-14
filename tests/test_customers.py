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


# -------------------------
# RBAC tests
# -------------------------

def test_regular_user_cannot_create_customer(
    authenticated_client,
) -> None:
    response = authenticated_client.post(
        "/customers/",
        json={
            "first_name": "Regular",
            "last_name": "User",
            "email": "regular_rbac_customer@example.com",
            "city": "Miami",
            "state": "FL",
            "signup_date": "2026-08-13",
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin privileges required.",
    }


def test_regular_user_cannot_delete_customer(
    authenticated_client,
) -> None:
    response = authenticated_client.delete(
        "/customers/1"
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin privileges required.",
    }


def test_admin_can_manage_customer(admin_client) -> None:
    create_response = admin_client.post(
        "/customers/",
        json={
            "first_name": "Admin",
            "last_name": "Customer",
            "email": "admin_rbac_customer@example.com",
            "city": "Fort Lauderdale",
            "state": "FL",
            "signup_date": "2026-08-13",
        },
    )

    assert create_response.status_code == 201

    customer = create_response.json()
    customer_id = customer["customer_id"]

    assert customer["first_name"] == "Admin"
    assert customer["last_name"] == "Customer"

    delete_response = admin_client.delete(
        f"/customers/{customer_id}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["customer_id"] == customer_id
# E-Commerce Analytics Database API

A production-style backend REST API built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy** that manages an e-commerce database and provides business analytics through REST endpoints.

## Features

- Customer Management
- Product Management
- Order Management
- Payment Processing
- Shipment Tracking
- Inventory Management
- Business Analytics
- Automatic API Documentation
- Input Validation
- Automated Testing

---

## Tech Stack

<<<<<<< HEAD
### Backend
- Python
=======
- RESTful API built with FastAPI
- PostgreSQL relational database
- SQLAlchemy ORM
- Pydantic request and response validation
- Customer CRUD API
- Product CRUD API
- Order CRUD API
- Payment CRUD API
- Shipment CRUD API
- Inventory Management API
- Advanced Analytics API
- Pagination and input validation
- Interactive Swagger/OpenAPI documentation
- Automated API testing with Pytest
---

# Technologies

- Python 3
>>>>>>> ecff971 (Update README with completed API features and testing)
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

### Testing
- Pytest
- FastAPI TestClient

### Tools
- Git
- GitHub
<<<<<<< HEAD
- Uvicorn
=======
- Pytest
- HTTPX
>>>>>>> ecff971 (Update README with completed API features and testing)

---

## Project Structure

```text
ecommerce-analytics-database/
│
├── app/
│   ├── routers/
<<<<<<< HEAD
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
=======
├── analytics.py
├── customers.py
├── inventory.py
├── orders.py
├── payments.py
├── products.py
├── shipments.py
└── __init__.py

tests/
├── test_health.py
├── test_customers.py
├── test_products.py
├── test_orders.py
├── test_payments.py
├── test_shipments.py
├── test_inventory.py
└── test_analytics.py
>>>>>>> ecff971 (Update README with completed API features and testing)
│
├── tests/
│
├── sql/
│
├── requirements.txt
└── README.md
```

---

## API Modules

### Customers
- Create Customer
- Get Customers
- Get Customer
- Delete Customer

### Products
- Create Product
- Get Products
- Get Product
- Delete Product

### Orders
- Create Order
- Get Orders
- Get Order
- Delete Order

### Payments
- Create Payment
- Get Payments
- Get Payment
- Delete Payment

### Shipments
- Create Shipment
- Update Shipment Status
- Get Shipments
- Delete Shipment

### Inventory
- View Inventory
- View Low Stock Products
- Update Stock
- Adjust Stock

### Analytics

- Revenue Summary
- Monthly Revenue
- Revenue by Category
- Top Selling Products
- Top Customers
- Orders by Status
- Payments by Method
- Shipment Status Analytics
- Inventory Value
- Never Ordered Products

---

## Testing

This project includes automated API tests using **Pytest**.

Current test coverage includes:

- Health endpoints
- Customers
- Products
- Orders
- Payments
- Shipments
- Inventory
- Analytics

**48 automated tests passing**

Run all tests:

```bash
python -m pytest -v
```

---

<<<<<<< HEAD
## Running the Project

Clone the repository
=======
## API Modules

- Customers
- Products
- Orders
- Payments
- Shipments
- Inventory
- Analytics

# Testing

The project includes automated API tests using Pytest.

Current coverage includes:

- Health endpoints
- Customers
- Products
- Orders
- Payments
- Shipments
- Inventory
- Analytics

**48 automated tests passing**

Run the tests:

```bash
python -m pytest -v


# Running the Project

## Clone the repository
>>>>>>> ecff971 (Update README with completed API features and testing)

```bash
git clone https://github.com/LilTeo48/ecommerce-analytics-database.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the API

```bash
uvicorn app.main:app --reload
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

## Example Analytics Endpoints

---

## Future Improvements

- Docker Support
- GitHub Actions CI/CD
- Streamlit Analytics Dashboard
- Authentication (JWT)
- Role-Based Authorization
- API Deployment (Render/Railway)
- Redis Caching
=======
✅ PostgreSQL database
✅ SQL schema
✅ Seed data
✅ SQL analytics
✅ SQLAlchemy models
✅ Pydantic schemas
✅ Customer CRUD
✅ Product CRUD
✅ Order CRUD
✅ Payment CRUD
✅ Shipment CRUD
✅ Inventory API
✅ Analytics API
✅ Pagination validation
✅ Automated testing (48 tests)
✅ FastAPI routers
✅ Interactive Swagger documentation

---

# Future Improvements

- Docker support
- GitHub Actions CI/CD
- Streamlit analytics dashboard
- JWT Authentication
- Role-based authorization
- API deployment (Render/Railway)
>>>>>>> ecff971 (Update README with completed API features and testing)

---

## Author

Tyler Chadwick

Bachelor of Arts in Computer Science
### Connect with me

- **GitHub:** https://github.com/LilTeo48
- **LinkedIn:** https://www.linkedin.com/in/tyler-chadwick-81b9a6275/

Backend Software Engineer | Python | FastAPI | PostgreSQL | SQL

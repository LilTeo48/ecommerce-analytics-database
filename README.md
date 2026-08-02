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

### Backend
- Python
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
- Uvicorn

---

## Project Structure

```text
ecommerce-analytics-database/
│
├── app/
│   ├── routers/
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
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

## Running the Project

Clone the repository

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

```
GET /analytics/revenue/summary

GET /analytics/revenue/monthly

GET /analytics/products/top-selling

GET /analytics/customers/top

GET /analytics/orders/by-status

GET /analytics/inventory/value
```

---

## Future Improvements

- Docker Support
- GitHub Actions CI/CD
- Streamlit Analytics Dashboard
- Authentication (JWT)
- Role-Based Authorization
- API Deployment (Render/Railway)
- Redis Caching

---

## Author

Tyler Chadwick

Bachelor of Arts in Computer Science
### Connect with me

- **GitHub:** https://github.com/LilTeo48
- **LinkedIn:** https://www.linkedin.com/in/tyler-chadwick-81b9a6275/

Backend Software Engineer | Python | FastAPI | PostgreSQL | SQL

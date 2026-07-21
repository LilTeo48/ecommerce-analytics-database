# E-Commerce Analytics API

A full-stack backend project that simulates the backend of a real-world e-commerce platform using **FastAPI**, **PostgreSQL**, and **SQLAlchemy**.

This project demonstrates backend software engineering concepts including REST API development, relational database design, CRUD operations, data validation, and business analytics.

---

# Features

- RESTful API built with FastAPI
- PostgreSQL relational database
- SQLAlchemy ORM
- Pydantic request/response validation
- Customer CRUD API
- Product CRUD API
- Business analytics SQL queries
- Interactive Swagger/OpenAPI documentation
- Seed data for testing

---

# Technologies

- Python 3
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Uvicorn
- psycopg2
- Git
- GitHub

---

# Project Structure

```text
ecommerce-analytics-database/
│
├── app/
│   ├── routers/
│   │   ├── customers.py
│   │   ├── products.py
│   │   └── __init__.py
│   │
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── sql/
│   ├── 01_schema.sql
│   ├── 02_seed_data.sql
│   └── 03_business_queries.sql
│
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

---

# Database Design

The application models six related tables.

- Customers
- Products
- Orders
- Order Items
- Payments
- Shipments

Relationships include:

- One customer → many orders
- One order → many order items
- One product → many order items
- One order → one payment
- One order → one shipment

---

# Current API

## Customers

- POST `/customers`
- GET `/customers`
- GET `/customers/{customer_id}`
- DELETE `/customers/{customer_id}`

## Products

- POST `/products`
- GET `/products`
- GET `/products/{product_id}`
- PATCH `/products/{product_id}/stock`
- DELETE `/products/{product_id}`

---

# Business Analytics

SQL reports currently include:

- Total revenue
- Monthly revenue
- Average order value
- Top-selling products
- Revenue by category
- Repeat customers
- Customer lifetime value
- Products never ordered
- Low inventory report
- Pending shipments

---

# Running the Project

## Clone the repository

```bash
git clone https://github.com/LilTeo48/ecommerce-analytics-database.git
cd ecommerce-analytics-database
```

## Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# PostgreSQL Setup

Create the database:

```sql
CREATE DATABASE ecommerce_analytics;
```

Load the schema:

```bash
psql -d ecommerce_analytics -f sql/01_schema.sql
```

Load seed data:

```bash
psql -d ecommerce_analytics -f sql/02_seed_data.sql
```

---

# Environment Variables

Create a `.env` file in the project root.

```env
DATABASE_URL=postgresql+psycopg2://YOUR_USERNAME@localhost:5432/ecommerce_analytics
```

---

# Run the API

```bash
uvicorn app.main:app --reload
```

---

# Swagger Documentation

FastAPI automatically generates interactive API documentation.

Open:

```
http://127.0.0.1:8000/docs
```

You can create, retrieve, update, and delete customers and products directly from the browser.

---

# Example Endpoints

```
GET /
GET /db

POST /customers
GET /customers
GET /customers/{id}
DELETE /customers/{id}

POST /products
GET /products
GET /products/{id}
PATCH /products/{id}/stock
DELETE /products/{id}
```

---

# Current Progress

- ✅ PostgreSQL database
- ✅ SQL schema
- ✅ Seed data
- ✅ SQL analytics
- ✅ SQLAlchemy models
- ✅ Pydantic schemas
- ✅ Customer CRUD
- ✅ Product CRUD
- ✅ FastAPI routers
- ✅ Interactive Swagger documentation

---

# Planned Features

- Orders API
- Order Items API
- Payments API
- Shipments API
- Authentication & Authorization
- Pagination
- Filtering & Search
- Analytics API endpoints
- React frontend dashboard
- Docker support
- Pytest unit tests
- GitHub Actions CI/CD
- Deployment to Render or Railway

---

# Author

**Tyler Chadwick**

- GitHub: https://github.com/LilTeo48
- LinkedIn: https://www.linkedin.com/in/tyler-chadwick-81b9a6275/

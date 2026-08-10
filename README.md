# E-Commerce Analytics Database API

A production-style backend REST API built with **FastAPI, PostgreSQL, SQLAlchemy, and Docker** for managing e-commerce operations and generating business analytics.

The project demonstrates backend API development, relational database design, JWT authentication, automated testing, containerization, and continuous integration with GitHub Actions.

## Features

- RESTful API built with FastAPI
- PostgreSQL relational database
- SQLAlchemy ORM
- Pydantic request and response validation
- JWT-based authentication
- Protected API endpoints
- Customer management
- Product management
- Order management
- Payment management
- Shipment tracking
- Inventory management
- Business analytics
- Pagination and input validation
- Docker containerization
- Automated testing with Pytest
- Continuous Integration with GitHub Actions
- Interactive Swagger/OpenAPI documentation

---

## Tech Stack

### Backend

- Python 3
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

### Database

- PostgreSQL
- SQL
- psycopg2

### Authentication

- JSON Web Tokens (JWT)
- Password hashing
- Bearer token authentication

### Testing

- Pytest
- FastAPI TestClient
- HTTPX

### DevOps & Tools

- Docker
- Docker Compose
- GitHub Actions
- Git
- GitHub

---

## Project Structure

```text
ecommerce-analytics-database/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── app/
│   ├── routers/
│   │   ├── analytics.py
│   │   ├── customers.py
│   │   ├── inventory.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   ├── products.py
│   │   └── shipments.py
│   │
│   ├── auth.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── security.py
│
├── sql/
│   ├── 01_schema.sql
│   └── 02_seed_data.sql
│
├── tests/
│   ├── conftest.py
│   ├── test_analytics.py
│   ├── test_auth.py
│   ├── test_customers.py
│   ├── test_health.py
│   ├── test_inventory.py
│   ├── test_orders.py
│   ├── test_payments.py
│   ├── test_products.py
│   └── test_shipments.py
│
├── compose.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## API Modules

### Authentication

The API uses JWT bearer authentication to protect application endpoints.

Authentication endpoints include:

- Register user
- Login user
- Generate JWT access token

Protected requests use the following header:

```text
Authorization: Bearer <access_token>
```

### Customers

- Get customers
- Get individual customer
- Pagination support

### Products

- Get products
- Get individual product
- Pagination support

### Orders

- Get orders
- Get individual order
- Order management

### Payments

- Get payments
- Get individual payment
- Payment management

### Shipments

- Get shipments
- Get individual shipment
- Shipment tracking

### Inventory

- View inventory
- View low-stock products
- Set product stock
- Adjust product stock

### Analytics

The analytics API provides business intelligence endpoints built on top of the transactional e-commerce data.

Available analytics include:

- Revenue summary
- Monthly revenue
- Revenue by category
- Top-selling products
- Top customers
- Orders by status
- Payments by method
- Shipments by status
- Total inventory value
- Never-ordered products

---

## Example Analytics Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/analytics/revenue/summary` | Overall revenue metrics |
| GET | `/analytics/revenue/monthly` | Monthly revenue trends |
| GET | `/analytics/revenue/by-category` | Revenue grouped by product category |
| GET | `/analytics/products/top-selling` | Top-selling products |
| GET | `/analytics/customers/top` | Highest-value customers |
| GET | `/analytics/orders/by-status` | Orders grouped by status |
| GET | `/analytics/payments/by-method` | Payments grouped by payment method |
| GET | `/analytics/shipments/by-status` | Shipments grouped by status |
| GET | `/analytics/inventory/value` | Total inventory value |
| GET | `/analytics/products/never-ordered` | Products that have never been ordered |

---

## Authentication Example

### Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123!"}'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123!"}'
```

A successful login returns an access token:

```json
{
  "access_token": "<JWT_ACCESS_TOKEN>",
  "token_type": "bearer"
}
```

### Access a Protected Endpoint

```bash
curl http://localhost:8000/analytics/revenue/summary \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

---

## Running the Project with Docker

### Clone the Repository

```bash
git clone https://github.com/LilTeo48/ecommerce-analytics-database.git
cd ecommerce-analytics-database
```

### Start the Application

```bash
docker compose up --build
```

Docker Compose starts:

- FastAPI application
- PostgreSQL database
- Database health checks
- Database schema and seed data

The API will be available at:

```text
http://localhost:8000
```

---

## Running Locally

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --reload
```

---

## API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI

```text
http://localhost:8000/docs
```

### ReDoc

```text
http://localhost:8000/redoc
```

Swagger UI can also be used to authenticate with a JWT token and test protected API endpoints interactively.

---

## Automated Testing

The project includes a Pytest test suite covering:

- Authentication
- Protected routes
- Health endpoints
- Customers
- Products
- Orders
- Payments
- Shipments
- Inventory
- Analytics
- Pagination validation
- Error handling

Run the complete test suite with:

```bash
python -m pytest -v
```

The tests exercise the FastAPI application against PostgreSQL and verify API responses, validation behavior, authentication requirements, and business analytics.

---

## Continuous Integration

GitHub Actions provides automated continuous integration for the project.

The CI workflow runs automatically on:

- Pushes to `main`
- Pull requests targeting `main`

The pipeline:

1. Checks out the repository
2. Starts a PostgreSQL 16 service
3. Configures Python
4. Installs project dependencies
5. Initializes the database schema
6. Loads seed data
7. Runs the complete Pytest test suite

This ensures changes are automatically validated in a clean environment before they are integrated into the project.

---

## Database Design

The PostgreSQL database models core e-commerce entities including:

- Customers
- Products
- Orders
- Order items
- Payments
- Shipments
- Users

The API uses SQLAlchemy to interact with the relational database while SQL-based analytics aggregate transactional data into business metrics.

---

## Future Improvements

- Role-based authorization
- Streamlit analytics dashboard
- Cloud API deployment
- Managed PostgreSQL deployment
- Redis caching
- Database migrations with Alembic
- Expanded integration testing
- Frontend analytics dashboard

---

## Author

**Tyler Chadwick**

Computer Science Graduate  
Florida International University

Backend Software Engineering | Python | FastAPI | PostgreSQL | SQL

### Connect with Me

- GitHub: `LilTeo48`
- LinkedIn: `tyler-chadwick-81b9a6275`

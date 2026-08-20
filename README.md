# E-Commerce Analytics Database API

A production-style backend REST API built with **FastAPI, PostgreSQL,

SQLAlchemy, and Docker** for managing e-commerce operations and

generating business analytics.

The project demonstrates backend API development, relational database

design, JWT authentication, email verification, secure password reset,

role-based access control (RBAC), secure session management,

transactional order processing, automated testing, containerization,

database migrations, and continuous integration with GitHub Actions.

## Features

- RESTful API built with FastAPI

- PostgreSQL relational database

- SQLAlchemy ORM

- Pydantic request and response validation

- JWT-based authentication

- Email verification with expiring, single-use tokens

- Transactional verification and password-reset emails through Resend

- Login restricted to verified accounts

- Access and refresh token support

- Refresh token rotation and revocation

- Protected API endpoints

- Authenticated user profile endpoint

- Password change with session revocation

- Secure password reset with expiring, single-use tokens

- Password reset with existing-session revocation

- Logout and logout-all session management

- Temporary account lockout after repeated failed login attempts

- Account deactivation

- Role-based authorization

- Customer management

- Product management

- Order management

- Payment management

- Shipment tracking

- Inventory management

- Business analytics

- Pagination and input validation

- Database migrations with Alembic

- Docker containerization

- Automated testing with Pytest

- Continuous Integration with GitHub Actions

- Interactive Swagger/OpenAPI documentation

------------------------------------------------------------------------

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

- Alembic

### Authentication & Authorization

- JSON Web Tokens (JWT)

- Password hashing

- Bearer token authentication

- Access and refresh tokens

- Email verification

- Transactional email delivery for verification and password reset

- Secure password reset

- Expiring, single-use password reset tokens

- Refresh token rotation and revocation

- Temporary account lockout

- Role-based access control (RBAC)

- User and administrator roles

### Testing

- Pytest

- FastAPI TestClient

- HTTPX

- PostgreSQL-backed integration testing

### DevOps & Tools

- Docker

- Docker Compose

- GitHub Actions

- Git

- GitHub

- Resend Email API

------------------------------------------------------------------------

## Project Structure

``` text

ecommerce-analytics-database/

│

├── .github/

│ └── workflows/

│ ├── ci.yml

│ └── tests.yml

│

├── alembic/

│ └── versions/

│

├── app/

│ ├── routers/

│ │ ├── analytics.py

│ │ ├── customers.py

│ │ ├── inventory.py

│ │ ├── orders.py

│ │ ├── payments.py

│ │ ├── products.py

│ │ └── shipments.py

│ │

│ ├── auth.py

│ ├── crud.py

│ ├── database.py

│ ├── email_service.py

│ ├── main.py

│ ├── models.py

│ ├── schemas.py

│ └── security.py

│

├── sql/

│ ├── 01_schema.sql

│ └── 02_seed_data.sql

│

├── tests/

│ ├── conftest.py

│ ├── test_analytics.py

│ ├── test_auth.py

│ ├── test_customers.py

│ ├── test_health.py

│ ├── test_inventory.py

│ ├── test_orders.py

│ ├── test_payments.py

│ ├── test_products.py

│ └── test_shipments.py

│

├── alembic.ini

├── compose.yaml

├── Dockerfile

├── requirements.txt

└── README.md

```

------------------------------------------------------------------------

## API Modules

### Authentication

The API uses JWT bearer authentication with short-lived access tokens

and longer-lived refresh tokens.

Newly registered accounts must complete email verification before they

can log in.

Authentication features include:

- User registration

- Email verification

- Expiring, single-use verification tokens

- Login restricted to verified accounts

- User login

- JWT access tokens

- Refresh tokens

- Refresh token rotation

- Refresh token revocation

- Logout

- Logout from all sessions

- Authenticated user profile retrieval

- Password changes

- Session revocation after password changes

- Password reset requests

- Expiring, single-use password reset tokens

- Password reset token validation

- Session revocation after password resets

- Failed-login tracking

- Temporary account lockout after repeated failed login attempts

- Account deactivation

- Role-based authorization

Protected requests use the following header:

``` text

Authorization: Bearer <access_token>

```

### Role-Based Access Control

The application supports two authorization roles:

- `user`

- `admin`

Authenticated users can access protected read endpoints, while

administrative operations require the `admin` role.

Admin-protected operations include creating, modifying, or deleting

transactional resources such as:

- Customers

- Products

- Orders

- Payments

- Shipments

- Inventory stock levels

Unauthorized write attempts return an HTTP `403 Forbidden` response.

### Customers

- Get customers

- Get individual customer

- Create customers with administrator privileges

- Delete customers with administrator privileges

- Pagination support

### Products

- Get products

- Get individual product

- Create products with administrator privileges

- Update product stock with administrator privileges

- Delete products with administrator privileges

- Pagination support

### Orders

- Get orders

- Get individual order

- Get orders by customer

- Create transactional orders with administrator privileges

- Create multiple order items in a single request

- Validate requested products and inventory

- Retrieve product prices directly from the database

- Calculate order totals server-side

- Automatically deduct purchased quantities from inventory

- Roll back failed order transactions

### Payments

- Get payments

- Get individual payment

- Get payment by order

- Create payments with administrator privileges

- Delete payments with administrator privileges

- Prevent duplicate payments for the same order

- Pagination support

### Shipments

- Get shipments

- Get individual shipment

- Get shipment by order

- Create shipments with administrator privileges

- Update shipment status with administrator privileges

- Delete shipments with administrator privileges

- Prevent duplicate shipments for the same order

- Pagination support

### Inventory

- View inventory

- View low-stock products

- View inventory by product

- Set product stock with administrator privileges

- Adjust product stock with administrator privileges

- Validate inventory adjustments

### Analytics

The analytics API provides business intelligence endpoints built on top

of the transactional e-commerce data.

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

------------------------------------------------------------------------

## Transactional Order Processing

Order creation is handled as a database transaction.

Clients submit the customer, order information, and requested products:

``` json

{

"customer_id": 1,

"order_date": "2026-08-13",

"order_status": "Pending",

"items": [

{

  "product\_id": 1,

  "quantity": 2

},

{

  "product\_id": 3,

  "quantity": 1

}

]

}

```

Clients do **not** provide product prices or the final order total.

During order creation, the backend:

1. Validates that the customer exists.

2. Validates that each requested product exists.

3. Retrieves current product prices from PostgreSQL.

4. Verifies sufficient inventory is available.

5. Calculates the total order amount server-side.

6. Creates the order.

7. Creates the associated order items.

8. Deducts purchased quantities from inventory.

9. Commits the complete transaction.

If any part of the operation fails, the transaction is rolled back so

partial orders and incorrect inventory updates are not persisted.

Duplicate products within the same order request are rejected during

request validation.

------------------------------------------------------------------------

## Example Analytics Endpoints

---------------------------------------------------------------------------------------

Method Endpoint Description

----------------- ------------------------------------- -------------------------------

GET `/analytics/revenue/summary` Overall revenue metrics

GET `/analytics/revenue/monthly` Monthly revenue trends

GET `/analytics/revenue/by-category` Revenue grouped by product

                                                      category

GET `/analytics/products/top-selling` Top-selling products

GET `/analytics/customers/top` Highest-value customers

GET `/analytics/orders/by-status` Orders grouped by status

GET `/analytics/payments/by-method` Payments grouped by payment

                                                      method

GET `/analytics/shipments/by-status` Shipments grouped by shipment

                                                      status

GET `/analytics/inventory/value` Total inventory value

GET `/analytics/products/never-ordered` Products that have never been

                                                      ordered

---------------------------------------------------------------------------------------

------------------------------------------------------------------------

## Authentication Example

### Register a User

``` bash

curl -X POST http://localhost:8000/auth/register \

-H "Content-Type: application/json" \

-d '{"email":"user@example.com","password":"Password123!"}'

```

New accounts are assigned the standard `user` role by default.

New users must verify their email before logging in. Registration

creates a time-limited verification token associated with the account.

### Verify Email

``` bash

curl -X POST http://localhost:8000/auth/verify-email \

-H "Content-Type: application/json" \

-d '{"verification_token":"<VERIFICATION_TOKEN>"}'

```

A valid verification token activates email verification for the account.

Verification tokens expire and cannot be reused after successful

verification.

### Login

``` bash

curl -X POST http://localhost:8000/auth/login \

-H "Content-Type: application/json" \

-d '{"email":"user@example.com","password":"Password123!"}'

```

A successful login returns an access token and refresh token:

``` json

{

"access_token": "<JWT_ACCESS_TOKEN>",

"refresh_token": "<JWT_REFRESH_TOKEN>",

"token_type": "bearer"

}

```

Unverified accounts are rejected until email verification has been

completed.

### Request a Password Reset

``` bash

curl -X POST http://localhost:8000/auth/forgot-password \

-H "Content-Type: application/json" \

-d '{"email":"user@example.com"}'

```

The API generates a cryptographically secure, time-limited password

reset token for registered accounts.

The endpoint returns the same generic response regardless of whether the

email exists, reducing account enumeration risk.

### Reset Password

``` bash

curl -X POST http://localhost:8000/auth/reset-password \

-H "Content-Type: application/json" \

-d '{"token":"<PASSWORD_RESET_TOKEN>","new_password":"NewPassword123!"}'

```

A successful password reset:

- Validates the reset token and its expiration

- Replaces the existing password with a securely hashed new password

- Invalidates the reset token so it cannot be reused

- Revokes existing refresh-token sessions

- Clears failed-login and temporary-lockout state

Password reset links are delivered to registered users through the

Resend email API. Email delivery configuration is loaded securely

through environment variables, while password reset tokens remain

time-limited and single-use.

### Access a Protected Endpoint

``` bash

curl http://localhost:8000/analytics/revenue/summary \

-H "Authorization: Bearer <JWT_ACCESS_TOKEN>"

```

------------------------------------------------------------------------

## Running the Project with Docker

### Clone the Repository

``` bash

git clone https://github.com/LilTeo48/ecommerce-analytics-database.git

cd ecommerce-analytics-database

```

### Configure Environment Variables

The application requires JWT configuration in addition to its database

connection.

Example development configuration:

``` text

DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce_analytics

JWT_SECRET_KEY=<your-secret-key>

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

RESEND_API_KEY=<your-resend-api-key>

EMAIL_FROM=<your-verified-sender>

FRONTEND_URL=http://localhost:3000

```

Do not commit production secrets to source control.

A `.env.example` file can be used to document the required configuration

without exposing real credentials.

### Start the Application

``` bash

docker compose up --build

```

Docker Compose starts:

- FastAPI application

- PostgreSQL database

- Database health checks

- Database schema and seed data

The API will be available at:

``` text

http://localhost:8000

```

------------------------------------------------------------------------

## Running Locally

Create and activate a virtual environment:

``` bash

python -m venv .venv

source .venv/bin/activate

```

Install dependencies:

``` bash

pip install -r requirements.txt

```

Configure the required environment variables and start the API:

``` bash

uvicorn app.main:app --reload

```

------------------------------------------------------------------------

## API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI

``` text

http://localhost:8000/docs

```

### ReDoc

``` text

http://localhost:8000/redoc

```

Swagger UI can be used to authenticate with a JWT token and test

protected API endpoints interactively.

------------------------------------------------------------------------

## Automated Testing

The project includes a comprehensive Pytest test suite covering:

- Authentication

- User registration

- Email verification

- Verification token validation

- Expired verification token rejection

- Verification token reuse prevention

- Unverified-user login rejection

- User login

- JWT access tokens

- Refresh token rotation

- Refresh token reuse prevention

- Refresh token revocation

- Logout

- Logout-all session management

- Authenticated user profile access

- Password changes

- Session revocation after password changes

- Password reset token generation

- Unknown-email enumeration protection

- Successful password reset

- Invalid password reset token rejection

- Expired password reset token rejection

- Password reset token reuse prevention

- Old-password rejection after password reset

- New-password authentication after password reset

- Session revocation after password reset

- Lockout-state clearing after password reset

- Failed-login tracking

- Temporary account lockout

- Successful-login failure-counter reset

- Expired lockout recovery

- Account deactivation

- Protected routes

- Role-based authorization

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

``` bash

python -m pytest -v

```

The tests exercise the FastAPI application against PostgreSQL and verify

API responses, validation behavior, authentication and authorization

requirements, transactional behavior, inventory integrity, and business

analytics.

The current test suite passes:

``` text

127 passed

```

------------------------------------------------------------------------

## Continuous Integration

GitHub Actions provides automated continuous integration for the

project.

The repository contains automated workflows that run on:

- Pushes to `main`

- Pull requests targeting `main`

The CI pipelines:

1. Check out the repository.

2. Start a PostgreSQL 16 service.

3. Configure Python 3.13.

4. Install project dependencies.

5. Configure test JWT environment variables.

6. Initialize the database schema.

7. Load seed data.

8. Run the complete Pytest test suite.

Both GitHub Actions workflows run the complete test suite in a clean

environment.

This ensures authentication, authorization, transactional order

processing, database operations, and analytics are continuously

validated as the project evolves.

------------------------------------------------------------------------

## Database Design

The PostgreSQL database models core e-commerce entities including:

- Customers

- Products

- Orders

- Order items

- Payments

- Shipments

- Users

- Refresh tokens

The `users` model also stores authentication-security state including

email verification status, verification token information, password

reset token information, failed-login attempts, and temporary account

lockout information.

SQLAlchemy provides ORM-based database access, while Alembic manages

database schema migrations.

The analytics layer uses SQL-based aggregations over transactional

e-commerce data to generate business metrics.

------------------------------------------------------------------------

## Security

The API includes several backend security controls:

- Passwords are stored as secure password hashes rather than

plaintext.

- JWT access tokens are used for authenticated requests.

- Refresh tokens support rotation and revocation.

- New accounts must complete email verification before authentication.

- Email verification tokens are time-limited and single-use.

- Invalid and expired verification tokens are rejected.

- Repeated failed login attempts trigger temporary account lockout.

- Successful authentication resets failed-login tracking.

- Password changes revoke existing refresh-token sessions.

- Password reset tokens are cryptographically generated, time-limited,

and single-use.

- Password reset requests use generic responses to reduce account

enumeration risk.

- Successful password resets revoke existing refresh-token sessions.

- Successful password resets clear failed-login and temporary-lockout

state.

- Logout can revoke an individual refresh-token session.

- Logout-all can revoke all active refresh-token sessions for a user.

- Account deactivation revokes existing refresh tokens.

- Inactive user accounts are rejected.

- Administrative operations require the `admin` role.

- Regular users cannot perform protected write operations.

- JWT configuration is loaded through environment variables.

- Product prices and order totals are controlled by the server rather

than trusted from client input.

------------------------------------------------------------------------

## Future Improvements

- Rate limiting

- Streamlit analytics dashboard

- Cloud API deployment

- Managed PostgreSQL deployment

- Redis caching

- Expanded integration testing

- Frontend analytics dashboard

------------------------------------------------------------------------

## Author

**Tyler Chadwick**

Computer Science Graduate\

Florida International University

Backend Software Engineering \| Python \| FastAPI \| PostgreSQL \| SQL

### Connect with Me

- GitHub: `github.com/LilTeo48`

- LinkedIn: `linkedin.com/in/tyler-chadwick-81b9a6275`


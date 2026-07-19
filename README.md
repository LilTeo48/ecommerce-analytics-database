# E-Commerce Database & Analytics System

A PostgreSQL and FastAPI-based e-commerce backend designed to simulate a real-world online retail system.

This project demonstrates relational database design, SQL analytics, REST API development, SQLAlchemy ORM modeling, environment-based configuration, and backend architecture.

## 📌 Project Overview

The system models the backend of an e-commerce platform and provides a foundation for business analytics and API development.

The database tracks:

- Customers
- Products
- Orders
- Order Items
- Payments
- Shipments

The project includes:

- A normalized PostgreSQL database
- Sample seed data
- Business analytics queries
- SQLAlchemy ORM models
- A FastAPI application
- Database health testing
- A layered backend structure for future CRUD and analytics endpoints

---

## 🛠️ Technologies Used

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- SQL
- Pydantic
- Uvicorn
- python-dotenv
- Git
- GitHub

---

## 📂 Project Structure

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
├── sql/
│   ├── 01_schema.sql
│   ├── 02_seed_data.sql
│   └── 03_business_queries.sql
│
├── .env
├── .gitignore
├── README.md
└── requirements.txt

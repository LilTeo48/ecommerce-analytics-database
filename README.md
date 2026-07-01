# E-Commerce Database & Analytics System

A PostgreSQL-based e-commerce database designed to simulate a real-world online retail system. This project demonstrates relational database design, data integrity, and business analytics using SQL.

## 📌 Project Overview

This project models the backend database for an e-commerce platform and answers common business questions through SQL analytics.

The database tracks:

- Customers
- Products
- Orders
- Order Items
- Payments
- Shipments

Using SQL, the project generates insights into sales performance, customer behavior, inventory management, and shipping operations.

---

## 🛠️ Technologies Used

- PostgreSQL
- SQL
- Git
- GitHub

---

## 📂 Project Structure

```
ecommerce-analytics-database/
│
├── sql/
│   ├── 01_schema.sql
│   ├── 02_seed_data.sql
│   └── 03_business_queries.sql
│
├── README.md
└── .gitignore
```

---

## 🗄️ Database Schema

The database consists of six related tables:

- Customers
- Products
- Orders
- Order Items
- Payments
- Shipments

Relationships include:

- One customer can place many orders.
- One order can contain many products.
- Products can appear in many orders.
- Each order has one payment.
- Each order has one shipment.

---

## 📊 Business Analytics

The project includes SQL reports for:

### Sales Analytics

- Total Revenue
- Monthly Revenue
- Average Order Value

### Product Analytics

- Top Selling Products
- Revenue by Product Category
- Products Never Ordered
- Low Stock Products

### Customer Analytics

- Repeat Customers
- Top Customers by Spending
- Customer Lifetime Value (CLV)
- Customer Segmentation

### Operations Analytics

- Orders by State
- Pending Shipments

---

## ▶️ Getting Started

### Create the database

```sql
CREATE DATABASE ecommerce_db;
```

### Load the schema

```bash
psql -d ecommerce_db -f sql/01_schema.sql
```

### Insert sample data

```bash
psql -d ecommerce_db -f sql/02_seed_data.sql
```

### Run analytics queries

```bash
psql -d ecommerce_db -f sql/03_business_queries.sql
```

---

## 📈 Example Insights

This project can answer questions such as:

- What is the total revenue?
- Which products generate the most sales?
- Who are the highest-value customers?
- Which customers are repeat buyers?
- Which products have never been sold?
- Which products are running low on inventory?
- How much revenue is generated each month?
- Which shipments are still pending?

---

## 🚀 Future Improvements

Planned enhancements include:

- Python integration using SQLAlchemy
- Pandas data analysis
- Interactive Streamlit dashboard
- Data visualizations
- Additional business analytics queries
- Docker support
- Automated reporting

---

## 👤 Author

**Tyler Chadwick**

- GitHub: https://github.com/LilTeo48
- LinkedIn: https://www.linkedin.com/in/tyler-chadwick-81b9a6275/

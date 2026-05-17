<<<<<<< HEAD
INSERT INTO customers (first_name, last_name, email, city, state, signup_date)
VALUES
('John', 'Smith', 'john.smith@email.com', 'Miami', 'FL', '2025-01-10'),
('Maria', 'Garcia', 'maria.garcia@email.com', 'Orlando', 'FL', '2025-01-18'),
('David', 'Johnson', 'david.johnson@email.com', 'Dallas', 'TX', '2025-02-02'),
('Sarah', 'Brown', 'sarah.brown@email.com', 'Atlanta', 'GA', '2025-02-20'),
('Michael', 'Davis', 'michael.davis@email.com', 'Phoenix', 'AZ', '2025-03-01');

INSERT INTO products (product_name, category, price, stock_quantity)
VALUES
('Wireless Mouse', 'Electronics', 25.99, 120),
('Mechanical Keyboard', 'Electronics', 79.99, 75),
('Gaming Controller', 'Accessories', 29.99, 100),
('Bluetooth Headphones', 'Electronics', 99.99, 65),
('USB-C Charger', 'Accessories', 19.99, 200);

INSERT INTO orders (customer_id, order_date, order_status)
VALUES
(1, '2025-02-08', 'Completed'),
(2, '2025-02-21', 'Completed'),
(1, '2025-02-21', 'Completed'),
(3, '2025-03-02', 'Completed'),
(4, '2025-03-15', 'Pending');

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
VALUES
(1, 1, 3, 25.99),
(1, 2, 1, 79.99),
(2, 2, 1, 79.99),
(3, 5, 1, 19.99),
(3, 4, 1, 99.99),
(4, 2, 1, 79.99),
(5, 3, 2, 29.99);

INSERT INTO payments (order_id, payment_date, payment_method, amount)
VALUES
(1, '2025-02-08', 'Credit Card', 157.96),
(2, '2025-02-21', 'PayPal', 79.99),
(3, '2025-02-21', 'Debit Card', 119.98),
(4, '2025-03-02', 'Credit Card', 79.99),
(5, '2025-03-15', 'Credit Card', 59.98);

INSERT INTO shipments (order_id, shipment_date, delivery_date, shipping_status)
VALUES
(1, '2025-02-09', '2025-02-12', 'Delivered'),
(2, '2025-02-22', '2025-02-25', 'Delivered'),
(3, '2025-02-22', '2025-02-27', 'Delivered'),
(4, '2025-03-03', '2025-03-07', 'Delivered'),
(5, NULL, NULL, 'Pending');
=======
INSERT INTO customers (first_name, last_name, email, city, state, signup_date)
VALUES
('John', 'Smith', 'john.smith@email.com', 'Miami', 'FL', '2025-01-10'),
('Maria', 'Garcia', 'maria.garcia@email.com', 'Orlando', 'FL', '2025-01-18'),
('David', 'Johnson', 'david.johnson@email.com', 'Dallas', 'TX', '2025-02-02'),
('Sarah', 'Brown', 'sarah.brown@email.com', 'Atlanta', 'GA', '2025-02-20'),
('Michael', 'Davis', 'michael.davis@email.com', 'Phoenix', 'AZ', '2025-03-01');

INSERT INTO products (product_name, category, price, stock_quantity)
VALUES
('Wireless Mouse', 'Electronics', 25.99, 120),
('Mechanical Keyboard', 'Electronics', 79.99, 75),
('Gaming Controller', 'Accessories', 29.99, 100),
('Bluetooth Headphones', 'Electronics', 99.99, 65),
('USB-C Charger', 'Accessories', 19.99, 200);

INSERT INTO orders (customer_id, order_date, order_status)
VALUES
(1, '2025-02-08', 'Completed'),
(2, '2025-02-21', 'Completed'),
(1, '2025-02-21', 'Completed'),
(3, '2025-03-02', 'Completed'),
(4, '2025-03-15', 'Pending');

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
VALUES
(1, 1, 3, 25.99),
(1, 2, 1, 79.99),
(2, 2, 1, 79.99),
(3, 5, 1, 19.99),
(3, 4, 1, 99.99),
(4, 2, 1, 79.99),
(5, 3, 2, 29.99);

INSERT INTO payments (order_id, payment_date, payment_method, amount)
VALUES
(1, '2025-02-08', 'Credit Card', 157.96),
(2, '2025-02-21', 'PayPal', 79.99),
(3, '2025-02-21', 'Debit Card', 119.98),
(4, '2025-03-02', 'Credit Card', 79.99),
(5, '2025-03-15', 'Credit Card', 59.98);

INSERT INTO shipments (order_id, shipment_date, delivery_date, shipping_status)
VALUES
(1, '2025-02-09', '2025-02-12', 'Delivered'),
(2, '2025-02-22', '2025-02-25', 'Delivered'),
(3, '2025-02-22', '2025-02-27', 'Delivered'),
(4, '2025-03-03', '2025-03-07', 'Delivered'),
(5, NULL, NULL, 'Pending');
>>>>>>> 941612c (Add customer lifetime value segmentation query)

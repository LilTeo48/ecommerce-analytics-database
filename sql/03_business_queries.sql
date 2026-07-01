-- Total revenue
SELECT 
    SUM(total_amount) AS total_revenue
FROM orders
WHERE order_status = 'Completed';

-- Top selling products
SELECT
    p.product_name,
    SUM(oi.quantity) AS total_units_sold,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
JOIN orders o 
    ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.product_name
ORDER BY total_revenue DESC;            

-- Revenue by product category
SELECT
    p.category,
    SUM(oi.quantity * oi.unit_price) AS category_revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
JOIN orders o
    ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.category
ORDER BY category_revenue DESC;           

-- Customers with repeat purchases
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(o.order_id) AS total_orders
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING COUNT(o.order_id) > 1
ORDER BY total_orders DESC;

-- Average order value
SELECT 
    ROUND(AVG(amount), 2) AS average_order_value
FROM payments;

-- Orders by state
SELECT 
    c.state,
    COUNT(o.order_id) AS total_orders
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.state
ORDER BY total_orders DESC;

-- Pending shipments
SELECT 
    o.order_id,
    c.first_name,
    c.last_name,
    s.shipping_status
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
JOIN shipments s
    ON o.order_id = s.order_id
WHERE s.shipping_status = 'Pending';

-- Customer lifetime value and segmentation
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity * oi.unit_price) AS lifetime_value,
    CASE
        WHEN SUM(oi.quantity * oi.unit_price) >= 150 THEN 'High Value'
        WHEN SUM(oi.quantity * oi.unit_price) >= 75 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS customer_segment
FROM customers c 
JOIN orders o 
    ON c.customer_id = o.customer_id
JOIN order_items oi 
    ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY c.customer_id, c.first_name, c.last_name, c.state
ORDER BY lifetime_value DESC;            
-- Monthly Revenue
SELECT
    DATE_TRUNC('month', order_date) AS revenue_month,
    SUM(total_amount) AS monthly_revenue,
    COUNT(order_id) AS total_orders
FROM orders
WHERE order_status = 'Completed'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY revenue_month;

-- Top Customers by Spending 
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o     
    ON c.customer_id = o.customer_id
WHERE o.order_status = 'Completed'
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name
ORDER BY total_spent DESC
LIMIT 5; 

-- Products Never Ordered
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.stock_quantity
FROM products p
LEFT JOIN order_items oi
    ON p.product_id = oi.product_id
WHERE oi.product_id IS NULL;

-- Low Stock Products
SELECT
    product_id,
    product_name,
    category,
    stock_quantity
FROM products
WHERE stock_quantity < 100
ORDER BY stock_quantity ASC;
-- 1. Customer count
SELECT COUNT(*)
FROM olist_db.customers;

-- 2. Order count
SELECT COUNT(*)
FROM olist_db.orders;

-- 3. Order item count
SELECT COUNT(*)
FROM olist_db.order_items;

-- 4. Revenue analysis
SELECT
    c.customer_city,
    o.order_status,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.price) AS total_revenue
FROM olist_db.customers c
JOIN olist_db.orders o
    ON c.customer_id = o.customer_id
JOIN olist_db.order_items oi
    ON o.order_id = oi.order_id
GROUP BY
    c.customer_city,
    o.order_status
ORDER BY total_revenue DESC
LIMIT 10;
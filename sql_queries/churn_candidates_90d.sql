-- Customers with no purchases in last 90 days (relative to dataset max date)
WITH last_date AS (
  SELECT DATE(MAX(order_date)) AS max_dt FROM transactions
),
last_purchase AS (
  SELECT customer_id, DATE(MAX(order_date)) AS last_dt
  FROM transactions
  GROUP BY 1
)
SELECT
  c.customer_id,
  c.country,
  c.state,
  l.last_dt AS last_purchase_date,
  CAST((JULIANDAY((SELECT max_dt FROM last_date)) - JULIANDAY(l.last_dt)) AS INT) AS recency_days
FROM customers c
JOIN last_purchase l USING(customer_id)
WHERE recency_days > 90
ORDER BY recency_days DESC;
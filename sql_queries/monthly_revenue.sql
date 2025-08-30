-- Monthly revenue trend
SELECT
  strftime('%Y-%m', order_date) AS order_month,
  COUNT(DISTINCT order_id) AS orders,
  SUM(revenue) AS revenue,
  SUM(quantity) AS units
FROM transactions
GROUP BY 1
ORDER BY 1;
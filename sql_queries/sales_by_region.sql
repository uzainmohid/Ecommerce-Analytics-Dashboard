-- Sales by region (country/state)
SELECT
  country,
  state,
  SUM(revenue) AS revenue,
  COUNT(DISTINCT order_id) AS orders
FROM transactions
GROUP BY 1,2
ORDER BY revenue DESC;
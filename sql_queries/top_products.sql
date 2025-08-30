-- Top products by revenue
SELECT
  p.product_id,
  p.product_name,
  p.category,
  p.subcategory,
  SUM(t.revenue) AS revenue,
  SUM(t.quantity) AS units
FROM transactions t
JOIN products p ON p.product_id = t.product_id
GROUP BY 1,2,3,4
ORDER BY revenue DESC
LIMIT 50;
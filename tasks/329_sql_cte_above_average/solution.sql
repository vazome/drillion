WITH spend AS (
  SELECT customer_id, sum(total) AS spent
  FROM orders
  WHERE status = '{status}'
  GROUP BY customer_id
)
SELECT customer_id, spent
FROM spend
WHERE spent > (SELECT avg(spent) FROM spend)
ORDER BY spent DESC, customer_id;

SELECT city, order_id, total, place
FROM (
  SELECT c.city, o.id AS order_id, o.total,
         row_number() OVER (PARTITION BY c.city ORDER BY o.total DESC, o.id) AS place
  FROM orders AS o
  JOIN customers AS c ON c.id = o.customer_id
) AS ranked
WHERE place <= {n}
ORDER BY city, place;

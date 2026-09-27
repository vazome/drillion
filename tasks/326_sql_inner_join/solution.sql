SELECT o.id AS order_id, c.name, o.status
FROM orders AS o
JOIN customers AS c ON c.id = o.customer_id
WHERE c.city = '{city}'
ORDER BY o.id;

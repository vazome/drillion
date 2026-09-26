SELECT c.id AS customer_id, c.name, count(o.id) AS orders, COALESCE(sum(o.total), 0) AS spent
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id AND o.status <> 'refunded'
WHERE c.city = '{city}'
GROUP BY c.id, c.name
ORDER BY c.id;

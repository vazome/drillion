SELECT DISTINCT ON (customer_id) customer_id, id AS order_id, placed_at
FROM orders
WHERE status = '{status}'
ORDER BY customer_id, placed_at DESC, id DESC;

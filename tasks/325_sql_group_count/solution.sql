SELECT customer_id, count(*) AS paid_orders
FROM orders
WHERE status = 'paid'
GROUP BY customer_id
HAVING count(*) >= {at_least}
ORDER BY paid_orders DESC, customer_id;

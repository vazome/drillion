SELECT name, joined
FROM customers
WHERE city = '{city}'
ORDER BY joined DESC, name
LIMIT {n};

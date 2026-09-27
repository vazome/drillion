SELECT c.id, c.name
FROM customers AS c
WHERE c.city = '{city}'
  AND NOT EXISTS (
    SELECT 1 FROM customers AS r WHERE r.referred_by = c.id
  )
ORDER BY c.id;

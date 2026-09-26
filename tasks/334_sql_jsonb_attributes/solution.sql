SELECT name, attrs ->> 'size' AS size, price
FROM products
WHERE attrs @> '{{"color": "{color}"}}'
  AND (attrs ->> 'stock')::int > 0
ORDER BY name;

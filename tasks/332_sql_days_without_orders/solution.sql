WITH days AS (
  SELECT d::date AS day
  FROM generate_series(
    DATE '{month}-01',
    DATE '{month}-01' + INTERVAL '1 month' - INTERVAL '1 day',
    INTERVAL '1 day'
  ) AS d
)
SELECT days.day, count(o.id) AS orders
FROM days
LEFT JOIN orders AS o ON o.placed_at::date = days.day
GROUP BY days.day
ORDER BY days.day;

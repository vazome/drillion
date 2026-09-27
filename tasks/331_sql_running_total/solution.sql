WITH daily AS (
  SELECT placed_at::date AS day, sum(total) AS revenue
  FROM orders
  WHERE status <> 'refunded'
    AND date_trunc('month', placed_at) = DATE '{month}-01'
  GROUP BY placed_at::date
)
SELECT day, revenue,
       sum(revenue) OVER (ORDER BY day) AS running_total,
       revenue - lag(revenue) OVER (ORDER BY day) AS change
FROM daily
ORDER BY day;

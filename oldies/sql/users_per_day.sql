SELECT dated, count( user )
FROM (
  SELECT DISTINCT to_char( created_at, 'YYYY_MM_DD') dated, "user"
  FROM production.user_activity_logs
) a
GROUP BY dated
ORDER BY dated DESC
LIMIT 30

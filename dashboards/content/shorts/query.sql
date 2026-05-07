SELECT
    CAST("date" AS DATE) AS "date",
    "site",
    SUM("plays") AS "plays"
FROM POC_DATABASE."domo"."shorts_all_sites_agg"
WHERE CAST("date" AS DATE) >= DATEADD(DAY, -7, CURRENT_DATE())
GROUP BY 1, 2
ORDER BY 1, 2;

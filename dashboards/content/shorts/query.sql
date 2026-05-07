SELECT
    CAST("date" AS DATE) AS "date",
    "site",
    "plays",
    "natives",
    "bumpers"
FROM POC_DATABASE."domo"."shorts_all_sites_agg"
WHERE CAST("date" AS DATE) >= DATEADD(DAY, -7, CURRENT_DATE());

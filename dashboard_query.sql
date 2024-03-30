WITH sub AS (
    SELECT
        date, 
        id,
        new_feedbacks,
        ROW_NUMBER() OVER (PARTITION BY date ORDER BY new_feedbacks DESC) AS row_number 
    FROM
        public.dynamic_feedbacks
    WHERE 
        date BETWEEN CURRENT_DATE - 7 AND CURRENT_DATE
)
SELECT
    date,
    id,
    new_feedbacks
FROM
    sub
WHERE
    row_number <= 3;
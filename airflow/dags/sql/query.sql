WITH
    yesterday AS (
        SELECT
            *
        FROM
            count_feedbacks
        WHERE
            date = '{{ ds }}'::date - 1
    ),
    today AS (
        SELECT
            *
        FROM
            count_feedbacks
        WHERE
            date = '{{ ds }}'
    ),
    dyn_query AS (
        SELECT
            today.id AS id,
            today.date AS date,
            today.feedbacks - yesterday.feedbacks AS new_feedbacks
        FROM
            today
            INNER JOIN yesterday ON today.id = yesterday.id
            AND today.feedbacks - yesterday.feedbacks > 0
    )
INSERT INTO
    dynamic_feedbacks (date, id, new_feedbacks)
SELECT
    date,
    id,
    new_feedbacks
FROM
    dyn_query;
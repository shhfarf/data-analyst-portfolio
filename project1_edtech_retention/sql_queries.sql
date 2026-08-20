
WITH cohort_size AS (
    SELECT
        strftime('%Y-%m', signup_date) AS cohort_month,
        COUNT(DISTINCT user_id) AS cohort_users
    FROM users
    GROUP BY 1
),
weekly_active AS (
    SELECT
        strftime('%Y-%m', u.signup_date) AS cohort_month,
        e.week_number,
        COUNT(DISTINCT CASE WHEN e.is_active = 1 THEN e.user_id END) AS active_users
    FROM engagement e
    JOIN users u ON u.user_id = e.user_id
    GROUP BY 1, 2
)
SELECT
    wa.cohort_month,
    wa.week_number,
    wa.active_users,
    cs.cohort_users,
    ROUND(100.0 * wa.active_users / cs.cohort_users, 1) AS retention_pct
FROM weekly_active wa
JOIN cohort_size cs ON cs.cohort_month = wa.cohort_month
ORDER BY wa.cohort_month, wa.week_number;


-- 2. FUNNEL DROP-OFF — на какой неделе теряем больше всего пользователей
-- Используем LAG() (window function) для расчёта week-over-week оттока
WITH weekly_active AS (
    SELECT
        week_number,
        COUNT(DISTINCT CASE WHEN is_active = 1 THEN user_id END) AS active_users
    FROM engagement
    GROUP BY week_number
)
SELECT
    week_number,
    active_users,
    LAG(active_users) OVER (ORDER BY week_number) AS active_prev_week,
    active_users - LAG(active_users) OVER (ORDER BY week_number) AS delta_users,
    ROUND(
        100.0 * (active_users - LAG(active_users) OVER (ORDER BY week_number))
        / NULLIF(LAG(active_users) OVER (ORDER BY week_number), 0), 1
    ) AS drop_pct
FROM weekly_active
ORDER BY week_number;


-- 3. RANKING КАНАЛОВ ПРИВЛЕЧЕНИЯ ПО КАЧЕСТВУ (completion rate) — RANK()
SELECT
    acquisition_channel,
    COUNT(*) AS users_count,
    SUM(completed_course) AS completed_count,
    ROUND(100.0 * SUM(completed_course) / COUNT(*), 1) AS completion_rate_pct,
    RANK() OVER (ORDER BY SUM(completed_course) * 1.0 / COUNT(*) DESC) AS quality_rank
FROM users
GROUP BY acquisition_channel
ORDER BY quality_rank;


-- 4. RFM-подобная сегментация вовлечённости (Recency / Frequency / Volume)
-- Recency: последняя активная неделя; Frequency: сколько недель был активен;
-- Volume: суммарное число событий (аналог Monetary в классическом RFM)
WITH user_stats AS (
    SELECT
        user_id,
        MAX(CASE WHEN is_active = 1 THEN week_number END) AS last_active_week,
        SUM(is_active) AS active_weeks,
        SUM(events_count) AS total_events
    FROM engagement
    GROUP BY user_id
),
scored AS (
    SELECT
        user_id,
        last_active_week,
        active_weeks,
        total_events,
        NTILE(3) OVER (ORDER BY last_active_week DESC) AS recency_score,   -- 1 = самые свежие
        NTILE(3) OVER (ORDER BY active_weeks DESC) AS frequency_score,
        NTILE(3) OVER (ORDER BY total_events DESC) AS volume_score
    FROM user_stats
)
SELECT
    user_id,
    recency_score, frequency_score, volume_score,
    CASE
        WHEN recency_score = 1 AND frequency_score = 1 THEN 'champion'
        WHEN recency_score = 3 AND frequency_score = 3 THEN 'at_risk_lost'
        WHEN recency_score = 1 AND frequency_score >= 2 THEN 'rising'
        ELSE 'core'
    END AS engagement_segment
FROM scored
ORDER BY user_id
LIMIT 20;


-- 5. МЕДИАНА СОБЫТИЙ В НЕДЕЛЮ ПО СЕГМЕНТАМ ПОЛЬЗОВАТЕЛЕЙ (оконная агрегация + CTE)
WITH per_user_week AS (
    SELECT
        u.segment,
        e.user_id,
        e.week_number,
        e.events_count,
        AVG(e.events_count) OVER (PARTITION BY u.segment, e.week_number) AS avg_events_segment_week
    FROM engagement e
    JOIN users u ON u.user_id = e.user_id
)
SELECT DISTINCT segment, week_number, ROUND(avg_events_segment_week, 2) AS avg_events
FROM per_user_week
ORDER BY segment, week_number;

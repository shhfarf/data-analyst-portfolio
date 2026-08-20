import sqlite3
import pandas as pd

con = sqlite3.connect(":memory:")
users = pd.read_csv("data/users.csv")
engagement = pd.read_csv("data/engagement.csv")
users.to_sql("users", con, index=False)
engagement.to_sql("engagement", con, index=False)

queries = {
    "cohort_retention": """
        WITH cohort_size AS (
            SELECT strftime('%Y-%m', signup_date) AS cohort_month,
                   COUNT(DISTINCT user_id) AS cohort_users
            FROM users GROUP BY 1
        ),
        weekly_active AS (
            SELECT strftime('%Y-%m', u.signup_date) AS cohort_month,
                   e.week_number,
                   COUNT(DISTINCT CASE WHEN e.is_active = 1 THEN e.user_id END) AS active_users
            FROM engagement e JOIN users u ON u.user_id = e.user_id
            GROUP BY 1, 2
        )
        SELECT wa.cohort_month, wa.week_number, wa.active_users, cs.cohort_users,
               ROUND(100.0 * wa.active_users / cs.cohort_users, 1) AS retention_pct
        FROM weekly_active wa JOIN cohort_size cs ON cs.cohort_month = wa.cohort_month
        ORDER BY wa.cohort_month, wa.week_number;
    """,
    "funnel_dropoff": """
        WITH weekly_active AS (
            SELECT week_number,
                   COUNT(DISTINCT CASE WHEN is_active = 1 THEN user_id END) AS active_users
            FROM engagement GROUP BY week_number
        )
        SELECT week_number, active_users,
               LAG(active_users) OVER (ORDER BY week_number) AS active_prev_week,
               active_users - LAG(active_users) OVER (ORDER BY week_number) AS delta_users,
               ROUND(100.0 * (active_users - LAG(active_users) OVER (ORDER BY week_number))
                     / NULLIF(LAG(active_users) OVER (ORDER BY week_number), 0), 1) AS drop_pct
        FROM weekly_active ORDER BY week_number;
    """,
    "channel_ranking": """
        SELECT acquisition_channel, COUNT(*) AS users_count,
               SUM(completed_course) AS completed_count,
               ROUND(100.0 * SUM(completed_course) / COUNT(*), 1) AS completion_rate_pct,
               RANK() OVER (ORDER BY SUM(completed_course) * 1.0 / COUNT(*) DESC) AS quality_rank
        FROM users GROUP BY acquisition_channel ORDER BY quality_rank;
    """,
}

for name, q in queries.items():
    df = pd.read_sql(q, con)
    df.to_csv(f"data/result_{name}.csv", index=False)
    print(f"\n=== {name} ===")
    print(df.to_string(index=False))

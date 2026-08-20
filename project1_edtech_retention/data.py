
import numpy as np
import pandas as pd

np.random.seed(42)

N_USERS = 6200
COURSE_START = pd.Timestamp("2025-09-01")
COURSE_WEEKS = 12

# --- Пользователи ---
acquisition_channels = np.random.choice(
    ["organic", "paid_ads", "partner_referral", "corporate", "social_media"],
    size=N_USERS, p=[0.30, 0.25, 0.15, 0.15, 0.15]
)
cohort_month = np.random.choice(
    pd.date_range(COURSE_START, periods=4, freq="MS"), size=N_USERS
)
device = np.random.choice(["desktop", "mobile", "tablet"], size=N_USERS, p=[0.62, 0.33, 0.05])
segment = np.random.choice(["student", "career_changer", "professional_upskill"], size=N_USERS, p=[0.35, 0.30, 0.35])

users = pd.DataFrame({
    "user_id": np.arange(1, N_USERS + 1),
    "signup_date": cohort_month,
    "acquisition_channel": acquisition_channels,
    "device": device,
    "segment": segment,
})

# --- Вовлечённость по неделям (funnel + retention) ---
# Базовая вероятность "выживания" в курсе неделя к неделе, зависит от сегмента и канала
base_hazard = {
    "student": 0.10,
    "career_changer": 0.14,
    "professional_upskill": 0.08,
}
channel_modifier = {
    "organic": -0.02, "paid_ads": 0.03, "partner_referral": -0.03,
    "corporate": -0.05, "social_media": 0.04
}

rows = []
for _, u in users.iterrows():
    active = True
    hazard = base_hazard[u["segment"]] + channel_modifier[u["acquisition_channel"]]
    hazard = max(0.03, hazard)
    for week in range(0, COURSE_WEEKS + 1):
        if week == 0:
            rows.append((u["user_id"], week, 1, np.random.poisson(4) + 1))
            continue
        if active and np.random.random() < hazard:
            active = False
        events_this_week = 0
        if active:
            lam = 3.5 if u["device"] == "desktop" else 2.2
            events_this_week = np.random.poisson(lam)
        rows.append((u["user_id"], week, int(active), events_this_week))

engagement = pd.DataFrame(rows, columns=["user_id", "week_number", "is_active", "events_count"])

# --- Финальный результат прохождения курса ---
completion = engagement.groupby("user_id")["is_active"].sum().reset_index()
completion["completed_course"] = (completion["is_active"] >= COURSE_WEEKS - 1).astype(int)
completion = completion[["user_id", "completed_course"]]

users = users.merge(completion, on="user_id")

users.to_csv("data/users.csv", index=False)
engagement.to_csv("data/engagement.csv", index=False)

print("users:", users.shape)
print("engagement:", engagement.shape)
print(users.head())
print(engagement.head())

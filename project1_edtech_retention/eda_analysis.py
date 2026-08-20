
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

users = pd.read_csv("data/users.csv")
engagement = pd.read_csv("data/engagement.csv")

# ---------- 1. Chi-square: канал привлечения vs завершение курса ----------
contingency = pd.crosstab(users["acquisition_channel"], users["completed_course"])
chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
print("=== Chi-square: acquisition_channel vs completed_course ===")
print(contingency)
print(f"chi2 = {chi2:.2f}, p-value = {p_value:.2e}, dof = {dof}")
print("Вывод:", "статистически значимая связь (p < 0.05)" if p_value < 0.05 else "значимой связи не обнаружено")

# ---------- 2. t-test: engagement corporate vs paid_ads (два худших/лучших по качеству) ----------
merged = engagement.merge(users[["user_id", "acquisition_channel"]], on="user_id")
avg_events_per_user = merged.groupby(["user_id", "acquisition_channel"])["events_count"].mean().reset_index()

corp = avg_events_per_user[avg_events_per_user.acquisition_channel == "corporate"]["events_count"]
paid = avg_events_per_user[avg_events_per_user.acquisition_channel == "paid_ads"]["events_count"]

t_stat, p_val_t = stats.ttest_ind(corp, paid, equal_var=False)  # Welch's t-test
print("\n=== Welch t-test: avg events/week, corporate vs paid_ads ===")
print(f"corporate: mean={corp.mean():.2f}, n={len(corp)}")
print(f"paid_ads:  mean={paid.mean():.2f}, n={len(paid)}")
print(f"t = {t_stat:.2f}, p-value = {p_val_t:.2e}")
print("Вывод:", "различие статистически значимо (p < 0.05)" if p_val_t < 0.05 else "значимого различия нет")

# ---------- 3. Описательная статистика по сегментам ----------
seg_stats = merged.groupby("acquisition_channel")["events_count"].agg(["mean", "median", "std", "count"]).round(2)
print("\n=== Описательная статистика events_count по каналам ===")
print(seg_stats)

# ---------- Графики ----------
retention = pd.read_csv("data/result_cohort_retention.csv")
plt.figure(figsize=(8, 5))
for cohort, grp in retention.groupby("cohort_month"):
    plt.plot(grp["week_number"], grp["retention_pct"], marker="o", label=cohort)
plt.title("Retention curve по когортам (месяц регистрации)")
plt.xlabel("Неделя курса")
plt.ylabel("% активных от когорты")
plt.legend(title="Когорта")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("charts/retention_curves.png", dpi=120)
plt.close()

channel_rank = pd.read_csv("data/result_channel_ranking.csv")
plt.figure(figsize=(7, 5))
plt.bar(channel_rank["acquisition_channel"], channel_rank["completion_rate_pct"], color="#3b6fd6")
plt.title("Completion rate по каналу привлечения")
plt.ylabel("% завершивших курс")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig("charts/completion_by_channel.png", dpi=120)
plt.close()

print("\nГрафики сохранены в charts/")

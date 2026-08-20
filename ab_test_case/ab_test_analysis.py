"""
A/B-тест: новый онбординг-флоу на лендинге курса.
Гипотеза: упрощение формы регистрации (5 полей -> 2 поля) увеличит конверсию в старт курса.

Часть 1: расчёт необходимого размера выборки ДО запуска теста (вручную, по формуле для двух пропорций).
Часть 2: анализ результатов теста на синтетических данных (z-test для пропорций, доверительные интервалы).
Используются только numpy/scipy — без сторонних AB-библиотек, чтобы показать понимание механики теста,
а не просто вызов готовой функции.
"""
import numpy as np
from scipy import stats

# ------------------------------------------------------------------
# ЧАСТЬ 1. Дизайн теста: расчёт размера выборки (формула для двух пропорций)
# ------------------------------------------------------------------
baseline_cr = 0.18          # текущая конверсия лендинга в регистрацию
mde = 0.03                  # minimum detectable effect: хотим поймать рост с 18% до 21%
alpha = 0.05
power = 0.80

p1 = baseline_cr
p2 = baseline_cr + mde
p_bar = (p1 + p2) / 2

z_alpha = stats.norm.ppf(1 - alpha / 2)   # 1.96 для alpha=0.05
z_beta = stats.norm.ppf(power)            # 0.84 для power=0.80

n_per_group = ((z_alpha * np.sqrt(2 * p_bar * (1 - p_bar)) +
                z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / (p2 - p1) ** 2

print("=== ЧАСТЬ 1: Расчёт размера выборки ===")
print(f"Baseline conversion: {baseline_cr:.1%}")
print(f"Minimum Detectable Effect: +{mde:.1%} (до {p2:.1%})")
print(f"Alpha = {alpha}, Power = {power}")
print(f"Необходимый размер выборки на группу: {int(np.ceil(n_per_group))} пользователей")
print(f"Итого на обе группы: {int(np.ceil(n_per_group)) * 2} пользователей")

daily_traffic = 450
days_needed = (int(np.ceil(n_per_group)) * 2) / daily_traffic
print(f"При трафике {daily_traffic}/день тест нужно вести ~{days_needed:.0f} дней "
      f"(рекомендация: не короче 2 полных недель, чтобы учесть недельную сезонность)")

# ------------------------------------------------------------------
# ЧАСТЬ 2. Анализ результатов (синтетические данные по итогам теста)
# ------------------------------------------------------------------
n_control = 2750
n_treatment = 2742
conv_control = int(n_control * 0.181)
conv_treatment = int(n_treatment * 0.214)

p_c = conv_control / n_control
p_t = conv_treatment / n_treatment

print("\n=== ЧАСТЬ 2: Результаты теста ===")
print(f"Control:   {conv_control}/{n_control} = {p_c:.2%}")
print(f"Treatment: {conv_treatment}/{n_treatment} = {p_t:.2%}")

# Z-test для разности пропорций (pooled variance)
p_pool = (conv_control + conv_treatment) / (n_control + n_treatment)
se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_control + 1 / n_treatment))
z_stat = (p_t - p_c) / se_pool
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

# Доверительные интервалы Уилсона (устойчивее нормального приближения)
def wilson_ci(count, n, z=1.96):
    p = count / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return center - half, center + half

ci_t = wilson_ci(conv_treatment, n_treatment)
ci_c = wilson_ci(conv_control, n_control)

print(f"\nZ-statistic = {z_stat:.2f}, p-value = {p_value:.4f}")
print(f"95% CI (treatment): [{ci_t[0]:.2%}, {ci_t[1]:.2%}]")
print(f"95% CI (control):   [{ci_c[0]:.2%}, {ci_c[1]:.2%}]")

relative_lift = (p_t - p_c) / p_c
print(f"Относительный прирост конверсии: +{relative_lift:.1%}")

if p_value < 0.05:
    print("\nВывод: результат статистически значим на уровне 5%. "
          "Рекомендация: раскатать новый флоу на 100% трафика.")
else:
    print("\nВывод: результат НЕ достиг статистической значимости. "
          "Рекомендация: либо продлить тест, либо признать эффект отсутствующим.")

# Sample Ratio Mismatch check — обязательная проверка валидности сплита 50/50
total = n_control + n_treatment
expected = total / 2
chi2_srm = ((n_control - expected) ** 2 / expected) + ((n_treatment - expected) ** 2 / expected)
p_srm = 1 - stats.chi2.cdf(chi2_srm, df=1)
print(f"\nSRM check: chi2 = {chi2_srm:.3f}, p = {p_srm:.3f} "
      f"({'сплит в норме' if p_srm > 0.01 else 'ВНИМАНИЕ: возможен sample ratio mismatch!'})")

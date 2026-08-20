# Портфолио: Data Analyst

Алина Шарф — три сквозных проекта, закрывающих разрыв между продуктовым/UX-опытом и позицией data analyst: SQL, Python + статистика, A/B-тестирование, финансовое моделирование unit economics.

Все данные — синтетические, но смоделированы по структуре реального опыта (EdTech-платформа, поток 6000+ участников, продуктовые метрики), чтобы кейсы звучали правдоподобно на собеседовании и было что рассказать о логике решений.

## Структура

```
portfolio/
├── project1_edtech_retention/   # SQL + Python EDA + статистика + дашборд
│   ├── generate_data.py
│   ├── sql_queries.sql          # window functions, CTE, RANK, NTILE
│   ├── run_sql.py
│   ├── eda_analysis.py          # chi-square, Welch t-test
│   ├── dashboard.html           # интерактивный дашборд (Chart.js)
│   ├── dashboard_data.json
│   ├── charts/
│   ├── data/
│   └── README.md
│
├── project2_unit_economics/     # Финансовая модель Excel: LTV/CAC, сценарный P&L
│   ├── build_model.py
│   ├── unit_economics_model.xlsx
│   └── README.md
│
├── ab_test_case/                # Кейс A/B-теста: от дизайна до решения
│   ├── ab_test_analysis.py      # расчёт выборки, z-test, Wilson CI, SRM-check
│   └── README.md
│
└── README.md                    # этот файл
```

## Как это использовать на собеседовании

**Elevator pitch (30 секунд):** "Я взяла свой реальный опыт работы с образовательной платформой на 6000+ участников и переупаковала его в три технических проекта: SQL-анализ retention и воронки с оконными функциями, Python-статистику для проверки гипотез о качестве каналов, и финансовую модель unit economics, которая напрямую использует данные из SQL-анализа. Отдельно — кейс A/B-теста с полным циклом от расчёта размера выборки до решения о раскатке."

**Если спросят "а был ли у вас реальный такой опыт":** Честно: это учебные проекты на синтетических данных, но структура и метрики отражают то, с чем я реально работала (воронки, BI-отчётность, продуктовые метрики в EdTech) — здесь я углубила именно техническую сторону (SQL/статистика/финмодель), которой не хватало в предыдущих ролях.

**На что смотреть в первую очередь интервьюеру:**
- `project1_edtech_retention/sql_queries.sql` — window functions (LAG, RANK, NTILE) в одном файле
- `project1_edtech_retention/eda_analysis.py` — правильно оформленные статтесты с интерпретацией p-value
- `ab_test_case/README.md` — умение спроектировать тест ДО его запуска, а не только проанализировать постфактум
- `project2_unit_economics/unit_economics_model.xlsx` — связка аналитики с финансовыми решениями бизнеса

## Как воспроизвести

Требуется Python 3.10+ с pandas, numpy, scipy, matplotlib, openpyxl (все стандартные, ставятся через `pip install`).

```bash
cd project1_edtech_retention
python3 generate_data.py && python3 run_sql.py && python3 eda_analysis.py
# открыть dashboard.html в браузере

cd ../project2_unit_economics
python3 build_model.py   # создаст unit_economics_model.xlsx

cd ../ab_test_case
python3 ab_test_analysis.py
```

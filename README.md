# Expense CSV Analyzer

Консольное приложение для анализа расходов из CSV-файла. Проект строит текстовый отчёт, графики и при необходимости Excel-файл с результатами.

## Возможности

- чтение расходов из CSV;
- проверка структуры и значений файла;
- фильтрация по датам и категориям;
- подсчёт общей суммы расходов;
- расчёт среднего и медианного расхода;
- поиск самых крупных операций;
- группировка расходов по категориям, дням и месяцам;
- сохранение текстового отчёта;
- построение графиков в PNG;
- экспорт анализа в Excel.

## Формат CSV

Файл должен содержать 4 колонки:

```csv
date,category,amount,comment
2026-06-01,Еда,1740,Продукты
2026-06-03,Связь,650,Интернет
2026-06-05,Транспорт,360,Такси
```

| Колонка | Назначение |
|---|---|
| `date` | дата операции в формате `YYYY-MM-DD` |
| `category` | категория расхода |
| `amount` | сумма расхода |
| `comment` | комментарий к операции |

Поддерживаются также русские названия колонок: `дата`, `категория`, `сумма`, `комментарий`.

## Установка

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Установка зависимостей:

```bash
pip install -r requirements.txt
```

## Запуск

Запуск с примером из папки `data`:

```bash
python main.py
```

Запуск со своим файлом:

```bash
python main.py path/to/expenses.csv
```

Сохранение результатов в другую папку:

```bash
python main.py data/expenses.csv --out results
```

Фильтр по периоду:

```bash
python main.py data/expenses.csv --from-date 2026-03-01 --to-date 2026-06-30
```

Фильтр по категориям:

```bash
python main.py data/expenses.csv --category Еда --category Транспорт
```

Экспорт в Excel:

```bash
python main.py data/expenses.csv --excel
```

Запуск без графиков:

```bash
python main.py data/expenses.csv --no-charts
```

## Результаты

После запуска в папке `output` создаются файлы:

| Файл | Описание |
|---|---|
| `report.txt` | текстовый отчёт по расходам |
| `categories_pie.png` | круговая диаграмма по категориям |
| `categories_bar.png` | столбчатая диаграмма топ-категорий |
| `daily_expenses.png` | линейный график расходов по дням |
| `monthly_expenses.png` | график расходов по месяцам |
| `expenses_analysis.xlsx` | Excel-отчёт, создаётся при запуске с `--excel` |

## Структура проекта

```text
expense_csv_analyzer/
├── app/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── charts.py
│   ├── config.py
│   ├── loader.py
│   └── reports.py
├── data/
│   └── expenses.csv
├── output/
│   └── .gitkeep
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Назначение файлов

| Файл | Назначение |
|---|---|
| `main.py` | точка входа и обработка аргументов командной строки |
| `app/loader.py` | загрузка CSV, нормализация колонок и проверка данных |
| `app/analyzer.py` | фильтрация, расчёты, группировки и выводы |
| `app/reports.py` | вывод отчёта в консоль, сохранение TXT и Excel |
| `app/charts.py` | создание графиков |
| `app/config.py` | настройки проекта и названия колонок |
| `data/expenses.csv` | пример входных данных |
| `output/` | папка для результатов анализа |

## Используемые библиотеки

- `pandas` — работа с таблицами и CSV;
- `matplotlib` — построение графиков;
- `rich` — красивый вывод в консоль;
- `openpyxl` — создание Excel-файла.
# Expense-CSV-Analyzer

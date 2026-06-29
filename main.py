from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from app.analyzer import analyze_expenses, filter_expenses
from app.charts import create_all_charts
from app.config import DEFAULT_DATA_FILE, DEFAULT_OUTPUT_DIR
from app.loader import CsvLoadError, load_expenses
from app.reports import build_report_text, export_to_excel, print_report, save_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Анализатор расходов из CSV-файла с отчётами и графиками."
    )
    parser.add_argument(
        "csv_file",
        nargs="?",
        default=str(DEFAULT_DATA_FILE),
        help="Путь к CSV-файлу. По умолчанию используется data/expenses.csv",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Папка для сохранения отчёта и графиков. По умолчанию output/",
    )
    parser.add_argument("--from-date", help="Начальная дата фильтра в формате YYYY-MM-DD")
    parser.add_argument("--to-date", help="Конечная дата фильтра в формате YYYY-MM-DD")
    parser.add_argument(
        "--category",
        action="append",
        help="Фильтр по категории. Можно указать несколько раз: --category Еда --category Транспорт",
    )
    parser.add_argument(
        "--currency",
        default="₽",
        help="Символ валюты для отчётов и графиков. По умолчанию ₽",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=7,
        help="Количество крупных операций в отчёте. По умолчанию 7",
    )
    parser.add_argument(
        "--no-charts",
        action="store_true",
        help="Не строить графики",
    )
    parser.add_argument(
        "--excel",
        action="store_true",
        help="Дополнительно сохранить Excel-отчёт",
    )

    return parser.parse_args()


def main() -> int:
    console = Console()
    args = parse_args()

    try:
        expenses = load_expenses(args.csv_file)
        filtered = filter_expenses(
            expenses,
            date_from=args.from_date,
            date_to=args.to_date,
            categories=args.category,
        )
        stats = analyze_expenses(filtered, top_limit=args.top)

        output_dir = Path(args.out)
        output_dir.mkdir(parents=True, exist_ok=True)

        print_report(stats, currency=args.currency)

        report_text = build_report_text(stats, currency=args.currency)
        report_path = save_report(report_text, output_dir)
        console.print(f"[green]Текстовый отчёт сохранён:[/green] {report_path}")

        if not args.no_charts:
            chart_paths = create_all_charts(
                stats.category_summary,
                stats.daily_summary,
                stats.monthly_summary,
                output_dir,
                currency=args.currency,
            )
            for name, path in chart_paths.items():
                console.print(f"[green]График {name} сохранён:[/green] {path}")

        if args.excel:
            excel_path = export_to_excel(filtered, stats, output_dir)
            console.print(f"[green]Excel-отчёт сохранён:[/green] {excel_path}")

        return 0

    except CsvLoadError as error:
        console.print(Panel(str(error), title="Ошибка CSV", border_style="red"))
        return 1
    except ValueError as error:
        console.print(Panel(str(error), title="Ошибка анализа", border_style="red"))
        return 1
    except KeyboardInterrupt:
        console.print("\n[yellow]Работа остановлена пользователем.[/yellow]")
        return 130
    except Exception as error:
        console.print(Panel(str(error), title="Непредвиденная ошибка", border_style="red"))
        return 1


if __name__ == "__main__":
    sys.exit(main())

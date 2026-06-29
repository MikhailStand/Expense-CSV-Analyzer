from __future__ import annotations

from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.analyzer import ExpenseStats
from app.config import AMOUNT_COLUMN, CATEGORY_COLUMN, COMMENT_COLUMN, DATE_COLUMN


def money(value: float, currency: str = "₽") -> str:
    formatted = f"{value:,.2f}".replace(",", " ")
    if formatted.endswith(".00"):
        formatted = formatted[:-3]
    return f"{formatted} {currency}"


def build_report_text(stats: ExpenseStats, currency: str = "₽") -> str:
    max_expense = stats.max_expense

    lines = [
        "ОТЧЁТ ПО РАСХОДАМ",
        "=" * 50,
        f"Период: {stats.min_date} — {stats.max_date}",
        f"Всего потрачено: {money(stats.total, currency)}",
        f"Количество операций: {stats.count}",
        f"Средний расход: {money(stats.average, currency)}",
        f"Медианный расход: {money(stats.median, currency)}",
        "",
        "Самая дорогая операция:",
        f"{max_expense[DATE_COLUMN].strftime('%Y-%m-%d')} | {max_expense[CATEGORY_COLUMN]} | "
        f"{money(max_expense[AMOUNT_COLUMN], currency)} | {max_expense[COMMENT_COLUMN]}",
        "",
        "Расходы по категориям:",
    ]

    for _, row in stats.category_summary.iterrows():
        lines.append(
            f"- {row[CATEGORY_COLUMN]}: {money(row['total'], currency)} "
            f"({int(row['operations'])} операций, средний чек {money(row['average'], currency)})"
        )

    lines.extend(["", "Топ операций:"])
    for _, row in stats.top_expenses.iterrows():
        lines.append(
            f"- {row[DATE_COLUMN].strftime('%Y-%m-%d')} | {row[CATEGORY_COLUMN]} | "
            f"{money(row[AMOUNT_COLUMN], currency)} | {row[COMMENT_COLUMN]}"
        )

    lines.extend(["", "Выводы:"])
    for insight in stats.insights:
        lines.append(f"- {insight}")

    return "\n".join(lines)


def save_report(report: str, output_dir: str | Path, filename: str = "report.txt") -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    report_path = path / filename
    report_path.write_text(report, encoding="utf-8")
    return report_path


def print_report(stats: ExpenseStats, currency: str = "₽") -> None:
    console = Console()

    summary = (
        f"[bold]Период:[/bold] {stats.min_date} — {stats.max_date}\n"
        f"[bold]Всего потрачено:[/bold] {money(stats.total, currency)}\n"
        f"[bold]Операций:[/bold] {stats.count}\n"
        f"[bold]Средний расход:[/bold] {money(stats.average, currency)}\n"
        f"[bold]Медианный расход:[/bold] {money(stats.median, currency)}"
    )
    console.print(Panel(summary, title="Expense CSV Analyzer", border_style="cyan"))

    category_table = Table(title="Расходы по категориям")
    category_table.add_column("Категория", style="bold")
    category_table.add_column("Сумма", justify="right")
    category_table.add_column("Операций", justify="right")
    category_table.add_column("Средний чек", justify="right")

    for _, row in stats.category_summary.iterrows():
        category_table.add_row(
            str(row[CATEGORY_COLUMN]),
            money(float(row["total"]), currency),
            str(int(row["operations"])),
            money(float(row["average"]), currency),
        )

    console.print(category_table)

    top_table = Table(title="Топ операций")
    top_table.add_column("Дата")
    top_table.add_column("Категория")
    top_table.add_column("Сумма", justify="right")
    top_table.add_column("Комментарий")

    for _, row in stats.top_expenses.iterrows():
        top_table.add_row(
            row[DATE_COLUMN].strftime("%Y-%m-%d"),
            str(row[CATEGORY_COLUMN]),
            money(float(row[AMOUNT_COLUMN]), currency),
            str(row[COMMENT_COLUMN]),
        )

    console.print(top_table)

    insight_text = "\n".join(f"• {insight}" for insight in stats.insights)
    console.print(Panel(insight_text, title="Выводы", border_style="green"))


def export_to_excel(
    source_df: pd.DataFrame,
    stats: ExpenseStats,
    output_dir: str | Path,
    filename: str = "expenses_analysis.xlsx",
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    excel_path = output_path / filename

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        source_df.to_excel(writer, sheet_name="Operations", index=False)
        stats.category_summary.to_excel(writer, sheet_name="Categories", index=False)
        stats.daily_summary.to_excel(writer, sheet_name="Daily", index=False)
        stats.monthly_summary.to_excel(writer, sheet_name="Monthly", index=False)
        stats.top_expenses.to_excel(writer, sheet_name="Top expenses", index=False)

    return excel_path

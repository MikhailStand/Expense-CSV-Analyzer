from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from app.config import AMOUNT_COLUMN, CATEGORY_COLUMN


ChartPaths = dict[str, Path]


def _prepare_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _save_current_figure(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()


def _combine_small_categories(category_summary: pd.DataFrame, top_limit: int = 7) -> pd.DataFrame:
    if len(category_summary) <= top_limit:
        return category_summary.copy()

    top = category_summary.head(top_limit).copy()
    other_total = category_summary.iloc[top_limit:]["total"].sum()
    other_operations = category_summary.iloc[top_limit:]["operations"].sum()

    other = pd.DataFrame(
        [
            {
                CATEGORY_COLUMN: "Другое",
                "total": other_total,
                "operations": other_operations,
                "average": other_total / other_operations if other_operations else 0,
            }
        ]
    )

    return pd.concat([top, other], ignore_index=True)


def create_category_pie_chart(
    category_summary: pd.DataFrame,
    output_dir: str | Path,
    currency: str = "₽",
) -> Path:
    output_path = _prepare_output_dir(output_dir) / "categories_pie.png"
    data = _combine_small_categories(category_summary)

    plt.figure(figsize=(9, 7))
    plt.pie(
        data["total"],
        labels=data[CATEGORY_COLUMN],
        autopct="%1.1f%%",
        startangle=90,
    )
    plt.title(f"Доля расходов по категориям, {currency}")
    _save_current_figure(output_path)
    return output_path


def create_category_bar_chart(
    category_summary: pd.DataFrame,
    output_dir: str | Path,
    currency: str = "₽",
    top_limit: int = 10,
) -> Path:
    output_path = _prepare_output_dir(output_dir) / "categories_bar.png"
    data = category_summary.head(top_limit).sort_values("total", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(data[CATEGORY_COLUMN], data["total"])
    plt.title("Топ категорий по расходам")
    plt.xlabel(f"Сумма, {currency}")
    plt.ylabel("Категория")
    plt.grid(axis="x", alpha=0.25)
    _save_current_figure(output_path)
    return output_path


def create_daily_line_chart(
    daily_summary: pd.DataFrame,
    output_dir: str | Path,
    currency: str = "₽",
) -> Path:
    output_path = _prepare_output_dir(output_dir) / "daily_expenses.png"

    plt.figure(figsize=(11, 6))
    plt.plot(daily_summary["day"], daily_summary["total"], marker="o")
    plt.title("Расходы по дням")
    plt.xlabel("Дата")
    plt.ylabel(f"Сумма, {currency}")
    plt.xticks(rotation=45, ha="right")
    plt.grid(alpha=0.25)
    _save_current_figure(output_path)
    return output_path


def create_monthly_bar_chart(
    monthly_summary: pd.DataFrame,
    output_dir: str | Path,
    currency: str = "₽",
) -> Path:
    output_path = _prepare_output_dir(output_dir) / "monthly_expenses.png"

    plt.figure(figsize=(10, 6))
    plt.bar(monthly_summary["month"], monthly_summary["total"])
    plt.title("Расходы по месяцам")
    plt.xlabel("Месяц")
    plt.ylabel(f"Сумма, {currency}")
    plt.xticks(rotation=30, ha="right")
    plt.grid(axis="y", alpha=0.25)
    _save_current_figure(output_path)
    return output_path


def create_all_charts(
    category_summary: pd.DataFrame,
    daily_summary: pd.DataFrame,
    monthly_summary: pd.DataFrame,
    output_dir: str | Path,
    currency: str = "₽",
) -> ChartPaths:
    paths: ChartPaths = {}
    paths["pie"] = create_category_pie_chart(category_summary, output_dir, currency)
    paths["bar"] = create_category_bar_chart(category_summary, output_dir, currency)
    paths["daily"] = create_daily_line_chart(daily_summary, output_dir, currency)
    paths["monthly"] = create_monthly_bar_chart(monthly_summary, output_dir, currency)
    return paths

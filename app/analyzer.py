from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.config import AMOUNT_COLUMN, CATEGORY_COLUMN, COMMENT_COLUMN, DATE_COLUMN


@dataclass(frozen=True)
class ExpenseStats:
    total: float
    count: int
    average: float
    median: float
    min_date: str
    max_date: str
    max_expense: pd.Series
    category_summary: pd.DataFrame
    daily_summary: pd.DataFrame
    monthly_summary: pd.DataFrame
    top_expenses: pd.DataFrame
    insights: list[str]


def filter_expenses(
    df: pd.DataFrame,
    date_from: str | None = None,
    date_to: str | None = None,
    categories: list[str] | None = None,
) -> pd.DataFrame:
    filtered = df.copy()

    if date_from:
        start = pd.to_datetime(date_from)
        filtered = filtered[filtered[DATE_COLUMN] >= start]

    if date_to:
        end = pd.to_datetime(date_to)
        filtered = filtered[filtered[DATE_COLUMN] <= end]

    if categories:
        normalized = {category.lower().strip() for category in categories}
        filtered = filtered[filtered[CATEGORY_COLUMN].str.lower().isin(normalized)]

    return filtered.reset_index(drop=True)


def get_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(CATEGORY_COLUMN, as_index=False)
        .agg(
            total=(AMOUNT_COLUMN, "sum"),
            operations=(AMOUNT_COLUMN, "count"),
            average=(AMOUNT_COLUMN, "mean"),
        )
        .sort_values("total", ascending=False)
        .reset_index(drop=True)
    )


def get_daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("day", as_index=False)
        .agg(total=(AMOUNT_COLUMN, "sum"), operations=(AMOUNT_COLUMN, "count"))
        .sort_values("day")
        .reset_index(drop=True)
    )


def get_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("month", as_index=False)
        .agg(total=(AMOUNT_COLUMN, "sum"), operations=(AMOUNT_COLUMN, "count"))
        .sort_values("month")
        .reset_index(drop=True)
    )


def get_top_expenses(df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    return (
        df.sort_values(AMOUNT_COLUMN, ascending=False)
        .head(limit)
        [[DATE_COLUMN, CATEGORY_COLUMN, AMOUNT_COLUMN, COMMENT_COLUMN]]
        .reset_index(drop=True)
    )


def build_insights(
    df: pd.DataFrame,
    category_summary: pd.DataFrame,
    daily_summary: pd.DataFrame,
    monthly_summary: pd.DataFrame,
) -> list[str]:
    insights: list[str] = []

    if df.empty:
        return ["Нет данных для анализа."]

    top_category = category_summary.iloc[0]
    category_share = top_category["total"] / df[AMOUNT_COLUMN].sum() * 100
    insights.append(
        f"Больше всего денег ушло на категорию «{top_category[CATEGORY_COLUMN]}» — {category_share:.1f}% от всех расходов."
    )

    top_day = daily_summary.sort_values("total", ascending=False).iloc[0]
    insights.append(f"Самый затратный день — {top_day['day']}.")

    if len(monthly_summary) >= 2:
        previous = monthly_summary.iloc[-2]
        current = monthly_summary.iloc[-1]
        diff = current["total"] - previous["total"]
        if previous["total"] > 0:
            percent = abs(diff) / previous["total"] * 100
            direction = "выше" if diff > 0 else "ниже"
            insights.append(
                f"В последнем месяце расходы на {percent:.1f}% {direction}, чем в предыдущем."
            )

    expensive_threshold = df[AMOUNT_COLUMN].mean() * 2
    expensive_count = int((df[AMOUNT_COLUMN] >= expensive_threshold).sum())
    if expensive_count > 0:
        insights.append(f"Найдено крупных покупок выше двойного среднего расхода: {expensive_count}.")

    return insights


def analyze_expenses(df: pd.DataFrame, top_limit: int = 5) -> ExpenseStats:
    if df.empty:
        raise ValueError("После фильтрации не осталось операций для анализа.")

    category_summary = get_category_summary(df)
    daily_summary = get_daily_summary(df)
    monthly_summary = get_monthly_summary(df)
    top_expenses = get_top_expenses(df, limit=top_limit)

    return ExpenseStats(
        total=float(df[AMOUNT_COLUMN].sum()),
        count=int(len(df)),
        average=float(df[AMOUNT_COLUMN].mean()),
        median=float(df[AMOUNT_COLUMN].median()),
        min_date=df[DATE_COLUMN].min().strftime("%Y-%m-%d"),
        max_date=df[DATE_COLUMN].max().strftime("%Y-%m-%d"),
        max_expense=df.loc[df[AMOUNT_COLUMN].idxmax()],
        category_summary=category_summary,
        daily_summary=daily_summary,
        monthly_summary=monthly_summary,
        top_expenses=top_expenses,
        insights=build_insights(df, category_summary, daily_summary, monthly_summary),
    )

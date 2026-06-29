from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config import (
    AMOUNT_COLUMN,
    CATEGORY_COLUMN,
    COLUMN_ALIASES,
    COMMENT_COLUMN,
    DATE_COLUMN,
    REQUIRED_COLUMNS,
)


class CsvLoadError(Exception):
    """Raised when a CSV file cannot be loaded or validated."""


def _read_csv_with_fallback(path: Path) -> pd.DataFrame:
    encodings = ("utf-8-sig", "utf-8", "cp1251")

    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as error:
            last_error = error
        except pd.errors.EmptyDataError as error:
            raise CsvLoadError("CSV-файл пустой.") from error
        except pd.errors.ParserError as error:
            raise CsvLoadError("Не удалось разобрать CSV-файл. Проверьте разделители и кавычки.") from error

    raise CsvLoadError(f"Не удалось прочитать файл. Последняя ошибка: {last_error}")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized_names = {}

    for column in df.columns:
        clean_name = str(column).strip().lower()
        normalized_names[column] = COLUMN_ALIASES.get(clean_name, clean_name)

    return df.rename(columns=normalized_names)


def _validate_required_columns(df: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        expected = ", ".join(sorted(REQUIRED_COLUMNS))
        raise CsvLoadError(f"В CSV не хватает колонок: {missing}. Ожидаемый формат: {expected}.")


def _prepare_expenses(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()

    prepared[DATE_COLUMN] = pd.to_datetime(prepared[DATE_COLUMN], errors="coerce")

    raw_amount = prepared[AMOUNT_COLUMN].astype(str)
    raw_amount = raw_amount.str.replace(" ", "", regex=False)
    raw_amount = raw_amount.str.replace(",", ".", regex=False)
    prepared[AMOUNT_COLUMN] = pd.to_numeric(raw_amount, errors="coerce")

    prepared[CATEGORY_COLUMN] = prepared[CATEGORY_COLUMN].astype(str).str.strip()
    prepared[COMMENT_COLUMN] = prepared[COMMENT_COLUMN].fillna("").astype(str).str.strip()

    invalid_date_rows = prepared[prepared[DATE_COLUMN].isna()].index.tolist()
    invalid_amount_rows = prepared[prepared[AMOUNT_COLUMN].isna()].index.tolist()
    invalid_category_rows = prepared[prepared[CATEGORY_COLUMN].eq("")].index.tolist()
    non_positive_amount_rows = prepared[prepared[AMOUNT_COLUMN] <= 0].index.tolist()

    errors = []
    if invalid_date_rows:
        errors.append(f"некорректная дата в строках: {', '.join(str(i + 2) for i in invalid_date_rows)}")
    if invalid_amount_rows:
        errors.append(f"некорректная сумма в строках: {', '.join(str(i + 2) for i in invalid_amount_rows)}")
    if invalid_category_rows:
        errors.append(f"пустая категория в строках: {', '.join(str(i + 2) for i in invalid_category_rows)}")
    if non_positive_amount_rows:
        errors.append(f"сумма должна быть больше нуля в строках: {', '.join(str(i + 2) for i in non_positive_amount_rows)}")

    if errors:
        raise CsvLoadError("Ошибки в данных: " + "; ".join(errors) + ".")

    prepared = prepared[[DATE_COLUMN, CATEGORY_COLUMN, AMOUNT_COLUMN, COMMENT_COLUMN]]
    prepared = prepared.sort_values(DATE_COLUMN).reset_index(drop=True)
    prepared["month"] = prepared[DATE_COLUMN].dt.to_period("M").astype(str)
    prepared["day"] = prepared[DATE_COLUMN].dt.strftime("%Y-%m-%d")

    return prepared


def load_expenses(path: str | Path) -> pd.DataFrame:
    csv_path = Path(path)

    if not csv_path.exists():
        raise CsvLoadError(f"Файл не найден: {csv_path}")

    if csv_path.suffix.lower() != ".csv":
        raise CsvLoadError("Файл должен быть в формате .csv")

    df = _read_csv_with_fallback(csv_path)
    df = _normalize_columns(df)
    _validate_required_columns(df)

    return _prepare_expenses(df)

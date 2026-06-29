from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "expenses.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"

DATE_COLUMN = "date"
CATEGORY_COLUMN = "category"
AMOUNT_COLUMN = "amount"
COMMENT_COLUMN = "comment"

REQUIRED_COLUMNS = {
    DATE_COLUMN,
    CATEGORY_COLUMN,
    AMOUNT_COLUMN,
    COMMENT_COLUMN,
}

COLUMN_ALIASES = {
    "дата": DATE_COLUMN,
    "date": DATE_COLUMN,
    "day": DATE_COLUMN,
    "категория": CATEGORY_COLUMN,
    "category": CATEGORY_COLUMN,
    "type": CATEGORY_COLUMN,
    "сумма": AMOUNT_COLUMN,
    "amount": AMOUNT_COLUMN,
    "price": AMOUNT_COLUMN,
    "стоимость": AMOUNT_COLUMN,
    "комментарий": COMMENT_COLUMN,
    "comment": COMMENT_COLUMN,
    "description": COMMENT_COLUMN,
    "описание": COMMENT_COLUMN,
}

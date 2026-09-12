"""
CSV ingestion pipeline for Finova.

Supports:
1. Finova dummy CSV format:
   index, date, description, notes, amount, category

2. Bank/Kaggle-style CSV format:
   Date, Category, Subcategory, Note, Amount,
   Income/Expense, Payment Mode / Mode

The pipeline:
- normalizes column names
- parses common date formats
- accepts positive transaction amounts
- derives transaction type when the CSV doesn't provide one
- uses the supplied category when available
- keeps duplicate detection
- reports the actual reason when a row is skipped
"""

from datetime import datetime
import re

import pandas as pd
from sqlalchemy.orm import Session

from app.models import Category, Transaction
from app.ml.predict import predict_category


# -------------------------------------------------------------------
# Column aliases
# -------------------------------------------------------------------

COLUMN_ALIASES = {
    "date": [
        "date",
        "transaction date",
        "txn date",
        "transaction_date",
    ],
    "description": [
        "description",
        "note",
        "notes",
        "narration",
        "transaction description",
        "remarks",
    ],
    "amount": [
        "amount",
        "transaction amount",
        "txn amount",
    ],
    "category": [
        "category",
        "transaction category",
    ],
    "txn_type": [
        "income/expense",
        "income expense",
        "transaction type",
        "txn type",
        "type",
    ],
    "payment_mode": [
        "mode",
        "payment mode",
        "payment_mode",
        "payment method",
    ],
}


DATE_FORMATS_TO_TRY = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y",
]


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _normalise_column_name(name: str) -> str:
    """Convert a CSV column name into a comparable form."""
    return re.sub(r"[^a-z0-9]+", " ", str(name).strip().lower()).strip()


def _find_column(df: pd.DataFrame, aliases: list[str]):
    """Find the first matching column from a list of aliases."""
    normalized = {
        _normalise_column_name(column): column
        for column in df.columns
    }

    for alias in aliases:
        key = _normalise_column_name(alias)

        if key in normalized:
            return normalized[key]

    return None


def _build_column_map(df: pd.DataFrame) -> dict:
    """
    Detect the actual columns present in the uploaded CSV.
    This allows both the dummy CSV and bank-style CSVs.
    """
    return {
        key: _find_column(df, aliases)
        for key, aliases in COLUMN_ALIASES.items()
    }


def _parse_date(value):
    """Parse common date formats plus Excel serial dates."""

    if value is None:
        return None

    if isinstance(value, float) and pd.isna(value):
        return None

    # Excel serial date
    if isinstance(value, (int, float)):
        try:
            return (
                pd.Timestamp("1899-12-30")
                + pd.Timedelta(days=int(value))
            ).date()
        except (ValueError, OverflowError):
            return None

    value_str = str(value).strip()

    if not value_str:
        return None

    # Common explicit formats
    for fmt in DATE_FORMATS_TO_TRY:
        try:
            return datetime.strptime(value_str, fmt).date()
        except ValueError:
            continue

    # Flexible pandas parser
    for dayfirst in (False, True):
        parsed = pd.to_datetime(
            value_str,
            errors="coerce",
            dayfirst=dayfirst,
        )

        if pd.notna(parsed):
            return parsed.date()

    return None


def _clean_amount(value):
    """
    Convert amounts such as:
        50000
        1,500
        ₹1,500
        Rs. 1500
    into float.
    """

    if value is None:
        return None

    if isinstance(value, float) and pd.isna(value):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    if not value:
        return None

    value = (
        value
        .replace(",", "")
        .replace("₹", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .strip()
    )

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalise_txn_type(value):
    """
    Normalize transaction type into the values Finova uses.
    """

    if value is None:
        return "Expense"

    value = str(value).strip().lower()

    if not value:
        return "Expense"

    if value in {
        "income",
        "credit",
        "credited",
        "deposit",
        "received",
    }:
        return "Income"

    if value in {
        "transfer-out",
        "transfer out",
        "transfer",
        "debit transfer",
    }:
        return "Transfer-Out"

    if value in {
        "expense",
        "debit",
        "debited",
        "withdrawal",
        "payment",
    }:
        return "Expense"

    return "Expense"


def _derive_txn_type(description: str, category: str) -> str:
    """
    The dummy Finova CSV does not have an Income/Expense column.

    Infer Income for obvious income categories/descriptions.
    Everything else is treated as Expense.
    """

    text = f"{description} {category}".lower()

    income_keywords = [
        "salary",
        "income",
        "credited",
        "credit",
        "received",
        "refund",
        "cashback",
        "friend transfer",
    ]

    transfer_keywords = [
        "transfer out",
        "investment transfer",
        "mutual fund",
        "ppf",
    ]

    if any(keyword in text for keyword in transfer_keywords):
        return "Transfer-Out"

    if any(keyword in text for keyword in income_keywords):
        return "Income"

    return "Expense"


def _get_or_create_category(
    db: Session,
    name: str,
    cache: dict,
) -> str:
    """Look up or create a category, cached during the upload."""

    name = (name or "Uncategorized").strip()

    if not name:
        name = "Uncategorized"

    name = name.title()

    if name in cache:
        return cache[name]

    category = (
        db.query(Category)
        .filter(Category.name == name)
        .first()
    )

    if category is None:
        category = Category(name=name)
        db.add(category)
        db.flush()

    cache[name] = category.id

    return category.id


def _is_duplicate(
    db: Session,
    user_id: str,
    txn_date,
    description: str,
    amount: float,
    txn_type: str,
) -> bool:
    """
    Check whether the same transaction already exists for this user.

    Duplicate definition:
    same user + date + description + amount + transaction type
    """

    existing = (
        db.query(Transaction.id)
        .filter(
            Transaction.user_id == user_id,
            Transaction.txn_date == txn_date,
            Transaction.description == description,
            Transaction.amount == amount,
            Transaction.txn_type == txn_type,
        )
        .first()
    )

    return existing is not None


# -------------------------------------------------------------------
# Main ingestion function
# -------------------------------------------------------------------

def ingest_csv(
    db: Session,
    user_id: str,
    file_bytes: bytes,
) -> dict:
    """
    Parse an uploaded CSV and insert valid transactions.
    """

    df = pd.read_csv(
        pd.io.common.BytesIO(file_bytes)
    )

    rows_received = len(df)
    rows_inserted = 0
    duplicates_skipped = 0
    skipped_reasons = []

    category_cache = {}

    column_map = _build_column_map(df)

    # Date and amount are mandatory.
    if column_map["date"] is None:
        raise ValueError(
            "CSV must contain a date column."
        )

    if column_map["amount"] is None:
        raise ValueError(
            "CSV must contain an amount column."
        )

    # Description is optional.
    # If unavailable, use a safe placeholder.
    description_column = column_map["description"]

    category_column = column_map["category"]
    txn_type_column = column_map["txn_type"]
    payment_mode_column = column_map["payment_mode"]

    for idx, row in df.iterrows():

        # -----------------------------------------------------------
        # Date
        # -----------------------------------------------------------

        raw_date = row.get(column_map["date"])

        txn_date = _parse_date(raw_date)

        if txn_date is None:
            skipped_reasons.append(
                f"row {idx}: unparseable date "
                f"(raw value: {raw_date!r})"
            )
            continue

        # -----------------------------------------------------------
        # Amount
        # -----------------------------------------------------------

        raw_amount = row.get(column_map["amount"])

        amount = _clean_amount(raw_amount)

        if amount is None:
            skipped_reasons.append(
                f"row {idx}: unparseable amount "
                f"(raw value: {raw_amount!r})"
            )
            continue

        if amount <= 0:
            skipped_reasons.append(
                f"row {idx}: non-positive amount "
                f"(raw value: {raw_amount!r})"
            )
            continue

        # -----------------------------------------------------------
        # Description
        # -----------------------------------------------------------

        if description_column is not None:
            description = str(
                row.get(description_column, "")
            ).strip()
        else:
            description = ""

        if not description or description.lower() == "nan":
            description = "(no description)"

        # -----------------------------------------------------------
        # Category
        # -----------------------------------------------------------

        supplied_category = None

        if category_column is not None:
            value = row.get(category_column)

            if value is not None:
                supplied_category = str(value).strip()

                if (
                    not supplied_category
                    or supplied_category.lower() == "nan"
                ):
                    supplied_category = None

        # -----------------------------------------------------------
        # Transaction type
        # -----------------------------------------------------------

        if txn_type_column is not None:
            raw_txn_type = row.get(txn_type_column)

            txn_type = _normalise_txn_type(
                raw_txn_type
            )
        else:
            txn_type = _derive_txn_type(
                description,
                supplied_category or "",
            )

        # -----------------------------------------------------------
        # Category prediction
        # -----------------------------------------------------------

        if supplied_category:
            category_name = supplied_category
        else:
            try:
                prediction = predict_category(
                    description,
                    db=db,
                    user_id=user_id,
                )

                if isinstance(prediction, dict):
                    category_name = prediction.get(
                        "category",
                        "Needs Review",
                    )
                else:
                    category_name = str(prediction)

            except Exception:
                category_name = "Needs Review"

        if not category_name:
            category_name = "Needs Review"

        category_id = _get_or_create_category(
            db,
            category_name,
            category_cache,
        )

        # -----------------------------------------------------------
        # Duplicate detection
        # -----------------------------------------------------------

        if _is_duplicate(
            db=db,
            user_id=user_id,
            txn_date=txn_date,
            description=description,
            amount=amount,
            txn_type=txn_type,
        ):
            duplicates_skipped += 1
            continue

        # -----------------------------------------------------------
        # Payment mode
        # -----------------------------------------------------------

        payment_mode = None

        if payment_mode_column is not None:
            value = row.get(payment_mode_column)

            if value is not None:
                value = str(value).strip()

                if value and value.lower() != "nan":
                    payment_mode = value

        # -----------------------------------------------------------
        # Create transaction
        # -----------------------------------------------------------

        transaction = Transaction(
            user_id=user_id,
            txn_date=txn_date,
            description=description,
            amount=amount,
            txn_type=txn_type,
            category_id=category_id,
            payment_mode=payment_mode,
        )

        db.add(transaction)

        rows_inserted += 1

    db.commit()

    return {
        "rows_received": rows_received,
        "rows_inserted": rows_inserted,
        "duplicates_skipped": duplicates_skipped,
        "rows_skipped": len(skipped_reasons),
        "skipped_reasons": skipped_reasons[:50],
    }
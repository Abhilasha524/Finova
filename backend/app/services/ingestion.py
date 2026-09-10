"""
CSV ingestion pipeline.

Assumed source columns (Kaggle "Daily Transactions Dataset" shape):
    Date, Category, Subcategory, Note, Amount, Income/Expense, Payment Mode

Handles, in order: invalid rows (bad date/amount) -> rows_skipped;
duplicate rows (already in the DB for this user, or repeated within the
same uploaded file) -> duplicates_skipped; everything else -> rows_inserted.
"""
from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session

from app.models import Category, Transaction

COLUMN_MAP = {
    "date": "Date",
    "category": "Category",
    "note": "Note",
    "amount": "Amount",
    "txn_type": "Income/Expense",
    "payment_mode": "Mode",
}

DATE_FORMATS_TO_TRY = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]


def _parse_date(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    if isinstance(value, (int, float)):
        try:
            return (pd.Timestamp("1899-12-30") + pd.Timedelta(days=int(value))).date()
        except (ValueError, OverflowError):
            return None

    value_str = str(value).strip()
    if not value_str:
        return None

    for fmt in DATE_FORMATS_TO_TRY:
        try:
            return datetime.strptime(value_str, fmt).date()
        except ValueError:
            continue

    for dayfirst in (False, True):
        parsed = pd.to_datetime(value_str, errors="coerce", dayfirst=dayfirst)
        if pd.notna(parsed):
            return parsed.date()

    return None


def _normalize_txn_type(raw: str) -> str:
    raw = (raw or "").strip().lower()
    if raw.startswith("income"):
        return "Income"
    if raw.startswith("expense"):
        return "Expense"
    if "transfer" in raw:
        return "Transfer-Out" if "out" in raw else "Transfer-In"
    return "Other"


def _get_or_create_category(db: Session, name: str, cache: dict) -> str:
    name = (name or "Uncategorized").strip().title()
    if name in cache:
        return cache[name]

    category = db.query(Category).filter(Category.name == name).first()
    if category is None:
        category = Category(name=name)
        db.add(category)
        db.flush()

    cache[name] = category.id
    return category.id


def ingest_csv(db: Session, user_id: str, file_bytes: bytes) -> dict:
    df = pd.read_csv(pd.io.common.BytesIO(file_bytes))

    rows_received = len(df)
    rows_inserted = 0
    duplicates_skipped = 0
    skipped_reasons: list[str] = []
    duplicate_reasons: list[str] = []
    category_cache: dict[str, str] = {}

    # Load this user's existing transaction "identity" keys ONCE, up front,
    # instead of one database query per row (which would be a slow N+1
    # pattern on a 2000+ row file). Each tuple is already hashable.
    existing_rows = (
        db.query(
            Transaction.txn_date,
            Transaction.description,
            Transaction.amount,
            Transaction.txn_type,
            Transaction.payment_mode,
        )
        .filter(Transaction.user_id == user_id)
        .all()
    )
    seen_keys = set(existing_rows)

    for idx, row in df.iterrows():
        txn_date = _parse_date(row.get(COLUMN_MAP["date"]))
        amount_raw = row.get(COLUMN_MAP["amount"])
        description = str(row.get(COLUMN_MAP["note"], "")).strip()
        txn_type_raw = str(row.get(COLUMN_MAP["txn_type"], "")).strip()

        if txn_date is None:
            raw_date = row.get(COLUMN_MAP["date"])
            skipped_reasons.append(f"row {idx}: unparseable date (raw value: {raw_date!r})")
            continue
        try:
            amount = float(amount_raw)
        except (TypeError, ValueError):
            skipped_reasons.append(f"row {idx}: unparseable amount '{amount_raw}'")
            continue
        if amount <= 0:
            skipped_reasons.append(f"row {idx}: non-positive amount")
            continue
        if not description:
            description = "(no description)"

        txn_type = _normalize_txn_type(txn_type_raw)
        payment_mode = str(row.get(COLUMN_MAP["payment_mode"], "")).strip() or None

        key = (txn_date, description, amount, txn_type, payment_mode)
        if key in seen_keys:
            duplicates_skipped += 1
            if len(duplicate_reasons) < 20:
                duplicate_reasons.append(
                    f"row {idx}: duplicate of an existing transaction "
                    f"({txn_date}, '{description}', {amount}, {txn_type})"
                )
            continue

        category_name = row.get(COLUMN_MAP["category"], "Uncategorized")
        category_id = _get_or_create_category(db, category_name, category_cache)

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
        seen_keys.add(key)  # catches a repeat of this same row later in the SAME file
        rows_inserted += 1

    db.commit()

    return {
        "rows_received": rows_received,
        "rows_inserted": rows_inserted,
        "duplicates_skipped": duplicates_skipped,
        "rows_skipped": len(skipped_reasons),
        "skipped_reasons": skipped_reasons[:50],
        "duplicate_reasons": duplicate_reasons,
    }
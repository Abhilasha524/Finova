"""
Prepares the monthly total-expense time series used for forecasting.

DESIGN DECISION 1: "Money Transfer" transactions are excluded from this series.
Unlike routine spending (Food, Transportation, Subscriptions), money transfers
are lumpy, one-off outflows to other people - closer in nature to the
Transfer-Out (investment) transactions already excluded from "Expense"
totals back in Phase 1 than to recurring consumption. Including them would
inject sudden, unpredictable spikes into the series that no time-series
model could learn a meaningful pattern from. This is a deliberate scope
decision, stated here explicitly, not an oversight.

DESIGN DECISION 2: a likely-partial trailing month is detected and dropped.
If the most recent transaction in the dataset falls well before the end of
its month, that almost certainly means data collection stopped mid-month -
not that real spending genuinely crashed to near-zero. Treating a partial
month as if it were a complete one would corrupt both training and honest
evaluation of the forecaster.
"""
import pandas as pd
from sqlalchemy.orm import Session

from app.models import Category, Transaction

EXCLUDED_CATEGORIES = {"Money Transfer"}
PARTIAL_MONTH_DAY_THRESHOLD = 25  # if the last transaction falls before this day of the month


def get_monthly_expense_series(db: Session, user_id: str) -> pd.Series:
    rows = (
        db.query(Transaction.amount, Transaction.txn_date, Category.name.label("category"))
        .join(Category, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == user_id, Transaction.txn_type == "Expense")
        .all()
    )
    df = pd.DataFrame(rows, columns=["amount", "txn_date", "category"])
    if df.empty:
        return pd.Series(dtype=float)

    df = df[~df["category"].isin(EXCLUDED_CATEGORIES)]
    df["txn_date"] = pd.to_datetime(df["txn_date"])

    last_date = df["txn_date"].max()
    if last_date.day < PARTIAL_MONTH_DAY_THRESHOLD:
        cutoff = last_date.replace(day=1)
        dropped_count = int((df["txn_date"] >= cutoff).sum())
        print(
            f"[forecast_data] Dropping likely PARTIAL final month "
            f"{cutoff.strftime('%Y-%m')}: last transaction on {last_date.date()} "
            f"(only day {last_date.day} of the month) - excluding {dropped_count} "
            f"transactions so an incomplete month isn't mistaken for a real low-spend month."
        )
        df = df[df["txn_date"] < cutoff]

    df["month"] = df["txn_date"].dt.to_period("M")
    monthly = df.groupby("month")["amount"].sum().sort_index()
    monthly.index = monthly.index.to_timestamp()
    return monthly
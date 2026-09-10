"""
Spending analytics - pure pandas aggregation, no ML here. Computes totals,
category breakdown, and monthly trend for one user's transactions.
"""
import pandas as pd
from sqlalchemy.orm import Session

from app.models import Category, Transaction


def get_analytics_summary(db: Session, user_id: str) -> dict:
    rows = (
        db.query(
            Transaction.amount,
            Transaction.txn_type,
            Transaction.txn_date,
            Category.name.label("category"),
        )
        .join(Category, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == user_id)
        .all()
    )

    df = pd.DataFrame(rows, columns=["amount", "txn_type", "txn_date", "category"])
    if df.empty:
        return {
            "total_income": 0.0,
            "total_expense": 0.0,
            "total_transfer_out": 0.0,
            "net_savings": 0.0,
            "category_breakdown": [],
            "monthly_trend": [],
        }

    total_income = float(df.loc[df["txn_type"] == "Income", "amount"].sum())
    total_expense = float(df.loc[df["txn_type"] == "Expense", "amount"].sum())
    total_transfer_out = float(df.loc[df["txn_type"] == "Transfer-Out", "amount"].sum())
    net_savings = total_income - total_expense - total_transfer_out

    expense_df = df[df["txn_type"] == "Expense"].copy()

    category_group = (
        expense_df.groupby("category")["amount"]
        .agg(["sum", "count"])
        .reset_index()
        .sort_values("sum", ascending=False)
    )
    category_breakdown = [
        {
            "category": row["category"],
            "total_amount": float(row["sum"]),
            "transaction_count": int(row["count"]),
        }
        for _, row in category_group.iterrows()
    ]

    expense_df["month"] = pd.to_datetime(expense_df["txn_date"]).dt.strftime("%Y-%m")
    monthly_group = (
        expense_df.groupby("month")["amount"].sum().reset_index().sort_values("month")
    )
    monthly_trend = [
        {"month": row["month"], "total_expense": float(row["amount"])}
        for _, row in monthly_group.iterrows()
    ]

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_transfer_out": total_transfer_out,
        "net_savings": net_savings,
        "category_breakdown": category_breakdown,
        "monthly_trend": monthly_trend,
    }
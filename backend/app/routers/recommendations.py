from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction, User
from app.auth import get_current_user


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/")
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )

    if not transactions:
        return {
            "recommendations": [
                "Upload transactions to receive personalized saving recommendations."
            ]
        }

    expenses = [
        t for t in transactions
        if t.txn_type == "Expense"
    ]

    if not expenses:
        return {
            "recommendations": [
                "No expense data is available yet. Add some transactions to receive personalized recommendations."
            ]
        }

    recommendations = []

    # Total spending
    total_expense = sum(t.amount for t in expenses)

    # Category-wise spending
    category_spending = {}

    for t in expenses:
        category_name = "Uncategorized"

        if t.category:
            category_name = t.category.name

        category_spending[category_name] = (
            category_spending.get(category_name, 0) + t.amount
        )

    # Biggest spending category
    if category_spending:
        biggest_category = max(
            category_spending,
            key=category_spending.get
        )

        biggest_amount = category_spending[biggest_category]

        if total_expense > 0:
            biggest_ratio = biggest_amount / total_expense
        else:
            biggest_ratio = 0

        if biggest_ratio > 0.30:
            recommendations.append(
                f"Your highest spending category is "
                f"{biggest_category}. Consider reducing spending in this "
                f"category because it accounts for "
                f"{biggest_ratio * 100:.1f}% of your total expenses."
            )

    # Weekend spending
    weekend_expense = sum(
        t.amount
        for t in expenses
        if t.txn_date.weekday() >= 5
    )

    weekend_ratio = (
        weekend_expense / total_expense
        if total_expense > 0
        else 0
    )

    if weekend_ratio > 0.30:
        recommendations.append(
            f"About {weekend_ratio * 100:.1f}% of your spending "
            "happens on weekends. Setting a weekend spending limit "
            "could help improve your savings."
        )

    # Recurring expenses
    recurring_expense = sum(
        t.amount
        for t in expenses
        if t.is_recurring
    )

    recurring_ratio = (
        recurring_expense / total_expense
        if total_expense > 0
        else 0
    )

    if recurring_ratio > 0.30:
        recommendations.append(
            f"Recurring expenses account for "
            f"{recurring_ratio * 100:.1f}% of your spending. "
            "Reviewing subscriptions and other recurring payments "
            "may help reduce unnecessary expenses."
        )

    # General saving recommendation
    if total_expense > 0:
        recommended_saving = total_expense * 0.10

        recommendations.append(
            f"Based on your current spending, try setting aside "
            f"approximately ₹{recommended_saving:,.2f} as a "
            "10% savings target."
        )

    if not recommendations:
        recommendations.append(
            "Your current spending pattern looks relatively balanced. "
            "Continue monitoring your expenses and maintain a regular "
            "saving habit."
        )

    return {
        "recommendations": recommendations
    }
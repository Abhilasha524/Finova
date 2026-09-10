from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Goal, User, Transaction
from app.schemas import GoalCreate, GoalOut
from app.auth import get_current_user


router = APIRouter(prefix="/goals", tags=["Goals"])


def calculate_goal_data(goal, db, current_user):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )

    total_income = sum(
        t.amount for t in transactions
        if t.txn_type == "Income"
    )

    total_expense = sum(
        t.amount for t in transactions
        if t.txn_type == "Expense"
    )

    total_transfer_out = sum(
        t.amount for t in transactions
        if t.txn_type == "Transfer-Out"
    )

    current_savings = max(
        0,
        total_income - total_expense - total_transfer_out
    )

    remaining_amount = max(
        0,
        goal.target_amount - current_savings
    )

    if goal.target_amount > 0:
        progress_percent = min(
            100,
            (current_savings / goal.target_amount) * 100
        )
    else:
        progress_percent = 0

    days_remaining = (goal.target_date - date.today()).days
    months_remaining = max(1, days_remaining / 30)

    required_monthly_saving = (
        remaining_amount / months_remaining
    )

    return {
        "id": str(goal.id),
        "title": goal.title,
        "target_amount": goal.target_amount,
        "target_date": goal.target_date,
        "current_savings": round(current_savings, 2),
        "progress_percent": round(progress_percent, 2),
        "remaining_amount": round(remaining_amount, 2),
        "required_monthly_saving": round(required_monthly_saving, 2),
    }


@router.post("/", response_model=GoalOut)
def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_goal = Goal(
        user_id=current_user.id,
        title=goal.title,
        target_amount=goal.target_amount,
        target_date=goal.target_date,
    )

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return calculate_goal_data(new_goal, db, current_user)


@router.get("/", response_model=list[GoalOut])
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goals = (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id)
        .order_by(Goal.target_date)
        .all()
    )

    return [
        calculate_goal_data(goal, db, current_user)
        for goal in goals
    ]


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = (
        db.query(Goal)
        .filter(
            Goal.id == goal_id,
            Goal.user_id == current_user.id,
        )
        .first()
    )

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Goal not found"
        )

    db.delete(goal)
    db.commit()

    return {"message": "Goal deleted successfully"}
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction, User, Goal
from app.schemas import ChatRequest, ChatResponse
from app.auth import get_current_user


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = request.message.lower().strip()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )

    # ---------------------------------------------------------
    # BASIC CONVERSATION
    # ---------------------------------------------------------

    greetings = [
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "good morning",
        "good afternoon",
        "good evening",
    ]

    if message in greetings:
        return {
            "answer": "Hello! 👋 I'm your financial assistant. I can help you understand your spending, income, savings, goals, and financial behaviour."
        }

    if (
        "how are you" in message
        or "how r you" in message
        or "how are u" in message
    ):
        return {
            "answer": "I'm doing great! 😊 I'm ready to help you understand your finances."
        }

    if (
        message in ["thanks", "thank you", "thx", "thankyou"]
        or "thanks for helping" in message
    ):
        return {
            "answer": "You're welcome! 😊 I'm always happy to help with your finances."
        }

    if message in ["bye", "goodbye", "see you", "see ya"]:
        return {
            "answer": "Goodbye! 👋 Keep an eye on your spending and savings. See you next time!"
        }

    if (
        message == "sad"
        or "i am sad" in message
        or "i'm sad" in message
        or "feeling sad" in message
        or "feel sad" in message
        or "not feeling good" in message
        or "feeling bad" in message
    ):
        return {
            "answer": "I'm sorry you're feeling that way. 💚 Take a little break and be kind to yourself. If you'd like, we can also look at your finances together and see if there's anything you can make easier."
        }

    if (
        "what can you do" in message
        or "what do you do" in message
        or "help me" in message
        or "how can you help" in message
    ):
        return {
            "answer": "I can help you with your financial data. You can ask me about your total income, expenses, savings, transfers, biggest spending category, transaction count, financial persona, and goals."
        }

    # ---------------------------------------------------------
    # NO TRANSACTION DATA
    # ---------------------------------------------------------

    if not transactions:
        return {
            "answer": "I don't have any transaction data yet. Please upload your transactions CSV first."
        }

    # ---------------------------------------------------------
    # BASIC FINANCIAL CALCULATIONS
    # ---------------------------------------------------------

    income = sum(
        t.amount for t in transactions
        if t.txn_type == "Income"
    )

    expense = sum(
        t.amount for t in transactions
        if t.txn_type == "Expense"
    )

    transfer_out = sum(
        t.amount for t in transactions
        if t.txn_type == "Transfer-Out"
    )

    savings = income - expense - transfer_out

    # ---------------------------------------------------------
    # TOTAL EXPENSE
    # ---------------------------------------------------------

    if (
        "how much did i spend" in message
        or "total expense" in message
        or "total spending" in message
        or "how much have i spent" in message
    ):
        return {
            "answer": f"Your total expense is ₹{expense:,.2f}."
        }

    # ---------------------------------------------------------
    # TOTAL INCOME
    # ---------------------------------------------------------

    if (
        "how much did i earn" in message
        or "total income" in message
        or "my income" in message
        or "how much income" in message
    ):
        return {
            "answer": f"Your total income is ₹{income:,.2f}."
        }

    # ---------------------------------------------------------
    # NET SAVINGS
    # ---------------------------------------------------------

    if (
        "how much did i save" in message
        or "how much have i saved" in message
        or "my savings" in message
        or "net savings" in message
    ):
        if savings >= 0:
            answer = (
                f"Your current net savings are ₹{savings:,.2f}."
            )
        else:
            answer = (
                f"Your current net savings are negative "
                f"₹{abs(savings):,.2f}. Your expenses and transfers "
                f"are higher than your income."
            )

        return {"answer": answer}

    # ---------------------------------------------------------
    # TRANSFERS
    # ---------------------------------------------------------

    if (
        "transfer" in message
        and ("how much" in message or "total" in message)
    ):
        return {
            "answer": (
                f"Your total Transfer-Out amount is "
                f"₹{transfer_out:,.2f}."
            )
        }

    # ---------------------------------------------------------
    # BIGGEST EXPENSE CATEGORY
    # ---------------------------------------------------------

    if (
        "biggest expense category" in message
        or "highest expense category" in message
        or "most expensive category" in message
        or "spend the most" in message
    ):
        category_totals = {}

        for t in transactions:
            if t.txn_type != "Expense":
                continue

            category_name = (
                t.category.name
                if t.category
                else "Uncategorized"
            )

            category_totals[category_name] = (
                category_totals.get(category_name, 0)
                + t.amount
            )

        if not category_totals:
            return {
                "answer": "I could not find categorized expense data."
            }

        top_category = max(
            category_totals,
            key=category_totals.get
        )

        top_amount = category_totals[top_category]

        return {
            "answer": (
                f"Your biggest expense category is "
                f"{top_category}, with total spending of "
                f"₹{top_amount:,.2f}."
            )
        }

    # ---------------------------------------------------------
    # TRANSACTION COUNT
    # ---------------------------------------------------------

    if (
        "how many transactions" in message
        or "number of transactions" in message
        or "transaction count" in message
    ):
        return {
            "answer": (
                f"You currently have "
                f"{len(transactions)} transactions."
            )
        }

    # ---------------------------------------------------------
    # FINANCIAL PERSONA
    # ---------------------------------------------------------

    if (
        "financial persona" in message
        or "my persona" in message
        or "spending persona" in message
    ):
        expenses = [
            t for t in transactions
            if t.txn_type == "Expense"
        ]

        if not expenses:
            return {
                "answer": (
                    "There is not enough expense data to "
                    "determine your financial persona."
                )
            }

        monthly_spending = {}

        for t in expenses:
            month = t.txn_date.strftime("%Y-%m")

            monthly_spending[month] = (
                monthly_spending.get(month, 0)
                + t.amount
            )

        values = list(monthly_spending.values())

        if len(values) > 1:
            average = sum(values) / len(values)

            variance = sum(
                (value - average) ** 2
                for value in values
            ) / len(values)

            volatility = variance ** 0.5
        else:
            volatility = 0

        weekend_expense = sum(
            t.amount
            for t in expenses
            if t.txn_date.weekday() >= 5
        )

        total_expense = sum(
            t.amount for t in expenses
        )

        weekend_ratio = (
            weekend_expense / total_expense
            if total_expense > 0
            else 0
        )

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

        if volatility > 50000:
            persona = "High-Variance Spender"

        elif weekend_ratio > 0.35:
            persona = "Weekend Spender"

        elif recurring_ratio > 0.40:
            persona = "Recurring-Expense Heavy"

        else:
            persona = "Balanced Spender"

        return {
            "answer": (
                f"Your current financial persona is "
                f"{persona}."
            )
        }

    # ---------------------------------------------------------
    # FINANCIAL GOALS
    # ---------------------------------------------------------

    if (
        "my goal" in message
        or "my goals" in message
        or "financial goal" in message
    ):
        goals = (
            db.query(Goal)
            .filter(Goal.user_id == current_user.id)
            .order_by(Goal.target_date)
            .all()
        )

        if not goals:
            return {
                "answer": (
                    "You don't have any financial goals yet."
                )
            }

        goal = goals[0]

        remaining = max(
            0,
            goal.target_amount - max(0, savings)
        )

        days_remaining = (
            goal.target_date - date.today()
        ).days

        months_remaining = max(
            1,
            days_remaining / 30
        )

        monthly_required = (
            remaining / months_remaining
        )

        return {
            "answer": (
                f"Your goal '{goal.title}' has a target of "
                f"₹{goal.target_amount:,.2f}. You need "
                f"approximately ₹{monthly_required:,.2f} per "
                f"month to reach it by {goal.target_date}."
            )
        }

    # ---------------------------------------------------------
    # FRIENDLY FALLBACK
    # ---------------------------------------------------------

    return {
        "answer": (
            "I'm here to help with your finances 😊 "
            "You can ask me things like how much you spent, "
            "your income, net savings, biggest expense category, "
            "financial persona, transaction count, or financial goals."
        )
    }
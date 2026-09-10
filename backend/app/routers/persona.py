from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from app.database import get_db
from app.models import Transaction, User
from app.schemas import PersonaOut
from app.auth import get_current_user

router = APIRouter(prefix="/persona", tags=["Persona"])


@router.get("/", response_model=PersonaOut)
def get_persona(
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
            "persona": "No Data",
            "description": "Upload transactions to analyze your financial behaviour.",
            "spending_volatility": 0,
            "category_diversity": 0,
            "weekend_spending_ratio": 0,
            "recurring_expense_ratio": 0,
        }

    expenses = [
        t for t in transactions
        if t.txn_type == "Expense"
    ]

    if not expenses:
        return {
            "persona": "No Spending Data",
            "description": "There is not enough expense data to determine a financial persona.",
            "spending_volatility": 0,
            "category_diversity": 0,
            "weekend_spending_ratio": 0,
            "recurring_expense_ratio": 0,
        }

    # Monthly behavioural features
    monthly_data = {}

    for t in expenses:
        month = t.txn_date.strftime("%Y-%m")

        if month not in monthly_data:
            monthly_data[month] = {
                "spending": 0,
                "categories": set(),
                "weekend_spending": 0,
                "recurring_spending": 0,
            }

        monthly_data[month]["spending"] += t.amount

        if t.category_id:
            monthly_data[month]["categories"].add(str(t.category_id))

        if t.txn_date.weekday() >= 5:
            monthly_data[month]["weekend_spending"] += t.amount

        if t.is_recurring:
            monthly_data[month]["recurring_spending"] += t.amount

    # Overall spending volatility
    monthly_spending = [
        data["spending"]
        for data in monthly_data.values()
    ]

    if len(monthly_spending) > 1:
        average = sum(monthly_spending) / len(monthly_spending)

        variance = sum(
            (value - average) ** 2
            for value in monthly_spending
        ) / len(monthly_spending)

        spending_volatility = variance ** 0.5
    else:
        spending_volatility = 0

    # Overall category diversity
    categories = set()

    for t in expenses:
        if t.category_id:
            categories.add(str(t.category_id))

    category_diversity = len(categories)

    # Overall weekend spending ratio
    total_expense = sum(t.amount for t in expenses)

    weekend_expense = sum(
        t.amount
        for t in expenses
        if t.txn_date.weekday() >= 5
    )

    weekend_spending_ratio = (
        weekend_expense / total_expense
        if total_expense > 0
        else 0
    )

    # Overall recurring expense ratio
    recurring_expense = sum(
        t.amount
        for t in expenses
        if t.is_recurring
    )

    recurring_expense_ratio = (
        recurring_expense / total_expense
        if total_expense > 0
        else 0
    )

    # Prepare monthly data for K-Means
    feature_rows = []
    months = sorted(monthly_data.keys())

    for month in months:
        data = monthly_data[month]

        spending = data["spending"]

        weekend_ratio = (
            data["weekend_spending"] / spending
            if spending > 0
            else 0
        )

        recurring_ratio = (
            data["recurring_spending"] / spending
            if spending > 0
            else 0
        )

        feature_rows.append([
            spending,
            len(data["categories"]),
            weekend_ratio,
            recurring_ratio,
        ])

    # Apply K-Means when enough monthly data is available
    if len(feature_rows) >= 3:
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_rows)

        kmeans = KMeans(
            n_clusters=3,
            random_state=42,
            n_init=10
        )

        cluster_labels = kmeans.fit_predict(scaled_features)

        # Use the latest month to determine the current persona
        latest_cluster = cluster_labels[-1]

        cluster_center = kmeans.cluster_centers_[latest_cluster]

        # Feature indexes:
        # 0 = spending
        # 1 = category diversity
        # 2 = weekend spending ratio
        # 3 = recurring expense ratio

        spending_score = cluster_center[0]
        weekend_score = cluster_center[2]
        recurring_score = cluster_center[3]

        behaviour_scores = {
            "High-Spending Month": spending_score,
            "Weekend Spender": weekend_score,
            "Recurring-Expense Heavy": recurring_score,
        }

        dominant_behaviour = max(
            behaviour_scores,
            key=behaviour_scores.get
        )

        dominant_score = behaviour_scores[dominant_behaviour]

        # Only assign a specific persona when the cluster
        # is above average for at least one behaviour.
        if dominant_score > 0:
            persona = dominant_behaviour

            if persona == "High-Spending Month":
                description = (
                    "Your recent month belongs to a cluster with "
                    "relatively high spending compared with your other months."
                )

            elif persona == "Weekend Spender":
                description = (
                    "Your recent month belongs to a cluster with "
                    "a relatively high share of weekend spending."
                )

            else:
                description = (
                    "Your recent month belongs to a cluster with "
                    "a relatively high share of recurring expenses."
                )

        else:
            persona = "Balanced Spender"
            description = (
                "Your recent spending pattern is relatively balanced "
                "compared with your other months."
            )

    else:
        persona = "Balanced Spender"
        description = (
            "There is not enough monthly data for detailed clustering, "
            "so your spending behaviour is currently classified as balanced."
        )

    return {
        "persona": persona,
        "description": description,
        "spending_volatility": round(spending_volatility, 2),
        "category_diversity": category_diversity,
        "weekend_spending_ratio": round(weekend_spending_ratio, 4),
        "recurring_expense_ratio": round(recurring_expense_ratio, 4),
    }
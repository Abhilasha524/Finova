"""
Anomaly detection using Isolation Forest, scoped to one user's Expense
transactions at a time.

WHY features are built this way:
Raw amount alone isn't enough - Rs. 5000 is normal for "Rent" but wildly
unusual for "Snacks". So each transaction's amount is compared against the
mean/std of ITS OWN category for this user, producing a z-score. That
z-score, plus raw amount and day-of-week, are the features fed to the model.
This is also what makes the explanation possible - z-score tells us WHY
something looks unusual, not just THAT it does.

WHY contamination=0.05:
Isolation Forest needs to be told roughly what fraction of the data is
expected to be anomalous. There's no ground truth to calibrate this against,
so 5% is used as a standard, commonly-cited default assumption - not a
measured value. This should be stated plainly if asked, not hidden.
"""
import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

from app.models import AnomalyFlag, Category, Transaction

CONTAMINATION = 0.05


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    category_stats = df.groupby("category")["amount"].agg(["mean", "std"]).reset_index()
    category_stats["std"] = category_stats["std"].fillna(0).replace(0, 1e-6)
    df = df.merge(category_stats, on="category", how="left")
    df["amount_zscore"] = (df["amount"] - df["mean"]) / df["std"]
    df["day_of_week"] = pd.to_datetime(df["txn_date"]).dt.dayofweek
    return df


def detect_anomalies(db: Session, user_id: str) -> list[dict]:
    rows = (
        db.query(
            Transaction.id,
            Transaction.amount,
            Transaction.txn_date,
            Category.name.label("category"),
        )
        .join(Category, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == user_id, Transaction.txn_type == "Expense")
        .all()
    )

    if len(rows) < 20:
        return []  # not enough data for the model to learn a meaningful "normal" pattern

    df = pd.DataFrame(rows, columns=["id", "amount", "txn_date", "category"])
    df = _build_features(df)

    features = df[["amount", "amount_zscore", "day_of_week"]].fillna(0)

    model = IsolationForest(contamination=CONTAMINATION, random_state=42)
    df["is_anomaly"] = model.fit_predict(features)  # -1 = anomaly, 1 = normal
    df["raw_score"] = model.decision_function(features)  # lower = more anomalous in sklearn's convention

    flagged = df[df["is_anomaly"] == -1]

    results = []
    for _, row in flagged.iterrows():
        if abs(row["amount_zscore"]) > 2:
            direction = "higher" if row["amount_zscore"] > 0 else "lower"
            reason = (
                f"Amount is unusually {direction} than this user's typical "
                f"'{row['category']}' transaction (z-score: {row['amount_zscore']:.1f})."
            )
        else:
            reason = "Statistically unusual pattern compared to this user's other transactions."

        results.append(
            {
                "transaction_id": row["id"],
                "reason": reason,
                # sign flipped so a HIGHER number means MORE anomalous - more intuitive to read
                "anomaly_score": float(-row["raw_score"]),
            }
        )

    return results


def save_anomalies(db: Session, user_id: str, anomalies: list[dict]) -> int:
    # Clear this user's previous flags before re-inserting, so re-running
    # detection doesn't pile up duplicate flags on every call.
    txn_ids = [t.id for t in db.query(Transaction.id).filter(Transaction.user_id == user_id).all()]
    if txn_ids:
        db.query(AnomalyFlag).filter(AnomalyFlag.transaction_id.in_(txn_ids)).delete(
            synchronize_session=False
        )

    for a in anomalies:
        db.add(
            AnomalyFlag(
                transaction_id=a["transaction_id"],
                reason=a["reason"],
                anomaly_score=a["anomaly_score"],
            )
        )
    db.commit()
    return len(anomalies)

def get_saved_anomalies(db: Session, user_id: str) -> list[dict]:
    """
    Reads back the anomalies already saved by a previous /anomalies/detect
    call - does NOT rerun Isolation Forest. Joins in transaction details
    (description, amount, category) so the frontend can render a useful
    table without a second round-trip to /transactions/.
    """
    rows = (
        db.query(
            AnomalyFlag.transaction_id,
            AnomalyFlag.reason,
            AnomalyFlag.anomaly_score,
            Transaction.description,
            Transaction.amount,
            Transaction.txn_date,
            Category.name.label("category"),
        )
        .join(Transaction, AnomalyFlag.transaction_id == Transaction.id)
        .join(Category, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == user_id)
        .order_by(AnomalyFlag.anomaly_score.desc())
        .all()
    )

    return [
        {
            "transaction_id": r.transaction_id,
            "description": r.description,
            "amount": r.amount,
            "txn_date": r.txn_date,
            "category": r.category,
            "reason": r.reason,
            "anomaly_score": r.anomaly_score,
        }
        for r in rows
    ]
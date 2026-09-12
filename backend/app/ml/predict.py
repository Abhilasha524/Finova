"""
Hybrid transaction categorization.

Priority:
1. User-learned merchant rules
2. Built-in merchant rules
3. ML model
4. Needs Review for low-confidence predictions
"""

import os

import joblib

from app.database import SessionLocal
from app.models import LearnedMerchantRule
from app.ml.merchant_rules import (
    extract_merchant_pattern,
    get_rule_category,
)


CONFIDENCE_THRESHOLD = 0.50

_ARTIFACT_DIR = os.path.join(
    os.path.dirname(__file__),
    "artifacts",
)

_vectorizer = None
_model = None
_model_name = None


def _load():
    global _vectorizer, _model, _model_name

    if _model is not None:
        return

    vec_path = os.path.join(
        _ARTIFACT_DIR,
        "vectorizer.joblib",
    )

    model_path = os.path.join(
        _ARTIFACT_DIR,
        "categorizer_model.joblib",
    )

    name_path = os.path.join(
        _ARTIFACT_DIR,
        "model_name.joblib",
    )

    if not (
        os.path.exists(vec_path)
        and os.path.exists(model_path)
    ):
        raise FileNotFoundError(
            "No trained model found. Run "
            "'python -m app.ml.train_categorizer' "
            "from the backend folder first, then restart "
            "the server."
        )

    _vectorizer = joblib.load(vec_path)
    _model = joblib.load(model_path)

    _model_name = (
        joblib.load(name_path)
        if os.path.exists(name_path)
        else "unknown"
    )


def _get_learned_category(
    description: str,
    user_id: str | None,
):
    """
    Check whether this user has previously corrected
    a similar merchant.
    """

    if not user_id:
        return None

    merchant_pattern = extract_merchant_pattern(
        description
    )

    if not merchant_pattern:
        return None

    db = SessionLocal()

    try:
        rules = (
            db.query(LearnedMerchantRule)
            .filter(
                LearnedMerchantRule.user_id == user_id
            )
            .all()
        )

        for rule in rules:
            if (
                rule.merchant_pattern.upper()
                == merchant_pattern.upper()
            ):
                return rule.category

        return None

    finally:
        db.close()


def predict_category(
    description: str,
    user_id: str | None = None,
) -> dict:
    """
    Categorize a transaction using the hybrid approach.

    Priority:

    User-learned rule
        ↓
    Built-in merchant rule
        ↓
    ML model
        ↓
    Needs Review
    """

    description = (description or "").strip()

    if not description:
        return {
            "predicted_category": "Needs Review",
            "confidence": None,
            "model_used": "None",
        }

    # ---------------------------------------------------------
    # Step 1: User-learned merchant rule
    # ---------------------------------------------------------

    learned_category = _get_learned_category(
        description,
        user_id,
    )

    if learned_category:
        return {
            "predicted_category": learned_category,
            "confidence": 1.0,
            "model_used": "Learned Merchant Rule",
        }

    # ---------------------------------------------------------
    # Step 2: Built-in merchant rule
    # ---------------------------------------------------------

    rule_category = get_rule_category(description)

    if rule_category:
        return {
            "predicted_category": rule_category,
            "confidence": 1.0,
            "model_used": "Merchant Rule",
        }

    # ---------------------------------------------------------
    # Step 3: ML model
    # ---------------------------------------------------------

    _load()

    features = _vectorizer.transform([description])

    predicted = _model.predict(features)[0]

    confidence = None

    if hasattr(_model, "predict_proba"):
        probabilities = _model.predict_proba(features)[0]
        confidence = float(max(probabilities))

    # ---------------------------------------------------------
    # Step 4: Low-confidence prediction
    # ---------------------------------------------------------

    if (
        confidence is not None
        and confidence < CONFIDENCE_THRESHOLD
    ):
        predicted = "Needs Review"

    return {
        "predicted_category": predicted,
        "confidence": confidence,
        "model_used": _model_name,
    }
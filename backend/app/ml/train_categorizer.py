"""
Phase 2 - Expense categorization model.

Trains a text classifier that reads a transaction's description (the "Note"
field) and predicts its Category (Food, Travel, Bills, etc).

WHY two models are trained and compared, not just one:
The project spec explicitly requires a justified choice between approaches,
not an assumed one. So this script trains BOTH Logistic Regression and
Naive Bayes on the same data, evaluates both honestly, and picks whichever
one actually scores better - with printed numbers you can defend in a viva.

WHY only "Expense" transactions are used:
Income rows and Transfer-Out rows don't have meaningful spending categories
(their "categories" are things like "From Family" or mutual fund names -
see the Transfer-Out fix from earlier). Training on those would teach the
model garbage. Only Expense rows have real category labels worth learning.

WHY the train/test split is by date, not random:
Transactions are time-ordered. A random split can let information from
"the future" leak into training (e.g. training on a December transaction
then testing on a November one). Splitting by date - train on the first
80% chronologically, test on the last 20% - is the honest way to simulate
"can this model categorize NEW transactions it hasn't seen."

Run this from the backend/ folder with the virtual environment active:
    python -m app.ml.train_categorizer
"""
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.naive_bayes import MultinomialNB

from app.database import SessionLocal
from app.models import Category, Transaction

ARTIFACT_DIR = "app/ml/artifacts"
MIN_SAMPLES_PER_CATEGORY = 15  # categories with fewer examples than this are too rare to learn


def load_training_data() -> pd.DataFrame:
    """Pulls Expense transactions with their category names directly from Postgres."""
    db = SessionLocal()
    try:
        rows = (
            db.query(Transaction.description, Transaction.txn_date, Category.name)
            .join(Category, Transaction.category_id == Category.id)
            .filter(Transaction.txn_type == "Expense")
            .all()
        )
    finally:
        db.close()

    df = pd.DataFrame(rows, columns=["description", "txn_date", "category"])
    print(f"Loaded {len(df)} Expense transactions with category labels from the database.")
    return df


def clean_and_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Drops categories that are too rare to meaningfully train or evaluate on."""
    before = len(df)
    counts = df["category"].value_counts()
    rare_categories = counts[counts < MIN_SAMPLES_PER_CATEGORY].index.tolist()
    if rare_categories:
        print(
            f"Dropping {len(rare_categories)} categories with fewer than "
            f"{MIN_SAMPLES_PER_CATEGORY} examples (too rare to learn or evaluate honestly): "
            f"{rare_categories}"
        )
    df = df[~df["category"].isin(rare_categories)]
    print(f"Kept {len(df)} of {before} rows after filtering rare categories.")
    return df


def time_based_split(df: pd.DataFrame, test_fraction: float = 0.2):
    """Splits chronologically: oldest 80% -> train, most recent 20% -> test.
    This is NOT a random split - see the module docstring for why."""
    df = df.sort_values("txn_date").reset_index(drop=True)
    split_index = int(len(df) * (1 - test_fraction))
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]
    print(
        f"Time-based split: {len(train_df)} train rows "
        f"(up to {train_df['txn_date'].max()}), "
        f"{len(test_df)} test rows (from {test_df['txn_date'].min()} onward)."
    )
    return train_df, test_df


def train_and_evaluate(train_df: pd.DataFrame, test_df: pd.DataFrame):
    vectorizer = TfidfVectorizer(lowercase=True,stop_words="english",max_features=3000,ngram_range=(1, 2))
    X_train = vectorizer.fit_transform(train_df["description"])
    X_test = vectorizer.transform(test_df["description"])
    y_train = train_df["category"]
    y_test = test_df["category"]

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Naive Bayes": MultinomialNB(),
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        accuracy = accuracy_score(y_test, predictions)
        weighted_f1 = f1_score(y_test, predictions, average="weighted", zero_division=0)

        print("\n" + "=" * 70)
        print(f"{name}")
        print("=" * 70)
        print(f"Accuracy:            {accuracy:.4f}")
        print(f"Weighted F1 score:   {weighted_f1:.4f}")
        print("\nPer-category performance:")
        print(classification_report(y_test, predictions, zero_division=0))

        results[name] = {
            "model": model,
            "accuracy": accuracy,
            "weighted_f1": weighted_f1,
        }

    return vectorizer, results


def pick_and_save_winner(vectorizer, results: dict):
    """Picks whichever model scored higher on weighted F1 (not raw accuracy -
    F1 accounts for class imbalance, which matters here since some categories
    like 'Food' will naturally have far more examples than 'Festivals')."""
    winner_name = max(results, key=lambda name: results[name]["weighted_f1"])
    winner = results[winner_name]

    print("\n" + "=" * 70)
    print("COMPARISON RESULT")
    print("=" * 70)
    for name, r in results.items():
        marker = "  <-- SELECTED" if name == winner_name else ""
        print(f"{name}: accuracy={r['accuracy']:.4f}, weighted_f1={r['weighted_f1']:.4f}{marker}")

    print(
        f"\nSelected '{winner_name}' because it has the higher weighted F1 score "
        f"({winner['weighted_f1']:.4f} vs the alternative). Weighted F1 was used "
        f"instead of plain accuracy because some categories have far fewer examples "
        f"than others, and accuracy alone can be misleadingly high just by predicting "
        f"the most common category every time."
    )

    import os

    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    joblib.dump(vectorizer, f"{ARTIFACT_DIR}/vectorizer.joblib")
    joblib.dump(winner["model"], f"{ARTIFACT_DIR}/categorizer_model.joblib")
    joblib.dump(winner_name, f"{ARTIFACT_DIR}/model_name.joblib")
    print(f"\nSaved winning model and vectorizer to {ARTIFACT_DIR}/ for later use in the API.")


def main():
    df = load_training_data()
    if len(df) < 30:
        print(
            "WARNING: very little training data available. Results below may not "
            "be meaningful yet - re-check that your CSV upload actually succeeded."
        )
        return

    df = clean_and_filter(df)
    train_df, test_df = time_based_split(df)
    vectorizer, results = train_and_evaluate(train_df, test_df)
    pick_and_save_winner(vectorizer, results)


if __name__ == "__main__":
    main()
"""
Phase 4 - Expense forecasting, v2.

CHANGE FROM v1: v1 trained only Holt-Winters with 12-month seasonality and
got a poor result (88.9% relative MAE) - traced to two causes: (1) a likely
partial trailing month corrupting the data (now fixed in forecast_data.py),
and (2) 12-month seasonality being genuinely unreliable to estimate from
only ~3 years of data (too many parameters for too little data).

This version compares FOUR candidates honestly on the same held-out months
and saves whichever one actually wins - including the possibility that a
naive baseline wins. That is a legitimate, reportable outcome, not a
failure: "our tested Holt-Winters models did not outperform a simple
last-value baseline given ~3 years of data" is a defensible viva statement.
Blindly tuning parameters until a number looks good would not be.

Run from backend/ folder with (venv) active:
    python -m app.ml.train_forecaster
"""
import os

import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from app.database import SessionLocal
from app.ml.forecast_baselines import NaiveLastValueForecaster, NaiveMovingAverageForecaster
from app.models import User
from app.services.forecast_data import get_monthly_expense_series

ARTIFACT_DIR = "app/ml/artifacts"
TEST_MONTHS = 6
MIN_MONTHS_REQUIRED = 18
MOVING_AVERAGE_WINDOW = 3


def _get_first_user_id(db):
    user = db.query(User).first()
    if user is None:
        raise RuntimeError("No user found in the database - register one first.")
    return user.id


def _build_candidates(train, allow_seasonal: bool) -> dict:
    """Returns {name: fitted_model_or_baseline}, each exposing .forecast(periods)."""
    candidates = {}

    candidates["Naive - Last Value"] = NaiveLastValueForecaster(last_value=float(train.iloc[-1]))

    window = min(MOVING_AVERAGE_WINDOW, len(train))
    candidates["Naive - Moving Average"] = NaiveMovingAverageForecaster(
        average_value=float(train.iloc[-window:].mean()), window=window
    )

    candidates["Holt-Winters - Trend Only"] = ExponentialSmoothing(
        train, trend="add", seasonal=None
    ).fit()

    if allow_seasonal:
        candidates["Holt-Winters - Trend + Seasonal(12)"] = ExponentialSmoothing(
            train, trend="add", seasonal="add", seasonal_periods=12
        ).fit()

    return candidates


def main():
    db = SessionLocal()
    try:
        series = get_monthly_expense_series(db, user_id=_get_first_user_id(db))
    finally:
        db.close()

    print(
        f"\nUsable months after cleaning: {len(series)} "
        f"({series.index.min().strftime('%Y-%m')} to {series.index.max().strftime('%Y-%m')})."
    )

    if len(series) < MIN_MONTHS_REQUIRED:
        print(
            f"WARNING: only {len(series)} months available - need at least "
            f"{MIN_MONTHS_REQUIRED} for a meaningful forecast. Stopping."
        )
        return

    train = series.iloc[:-TEST_MONTHS]
    test = series.iloc[-TEST_MONTHS:]
    print(f"Train: {len(train)} months, Test (held out, real values): {len(test)} months.\n")

    allow_seasonal = len(train) >= 24
    if not allow_seasonal:
        print(
            "Skipping the seasonal Holt-Winters candidate: fewer than 24 training "
            "months available, not enough repeated cycles to estimate 12 seasonal "
            "indices reliably.\n"
        )

    candidates = _build_candidates(train, allow_seasonal)

    print("=" * 78)
    print("CANDIDATE COMPARISON (evaluated on the same held-out real months)")
    print("=" * 78)

    scored = []
    for name, candidate in candidates.items():
        predictions = candidate.forecast(TEST_MONTHS)
        predictions.index = test.index  # align for comparison/printing

        mae = mean_absolute_error(test, predictions)
        rmse = np.sqrt(mean_squared_error(test, predictions))
        mae_pct = 100 * mae / test.mean()

        print(f"\n{name}")
        print("-" * len(name))
        for date, actual, predicted in zip(test.index, test.values, predictions.values):
            print(f"  {date.strftime('%Y-%m')}: actual={actual:,.2f}  predicted={predicted:,.2f}")
        print(f"  MAE: {mae:,.2f}   RMSE: {rmse:,.2f}   MAE as % of avg: {mae_pct:.1f}%")

        scored.append((name, mae, candidate))

    scored.sort(key=lambda x: x[1])
    winner_name, winner_mae, _ = scored[0]

    print("\n" + "=" * 78)
    print("RESULT")
    print("=" * 78)
    for name, mae, _ in scored:
        marker = "  <-- SELECTED (lowest MAE)" if name == winner_name else ""
        print(f"{name}: MAE={mae:,.2f}{marker}")

    if "Naive" in winner_name:
        print(
            f"\nHonest finding: the naive baseline '{winner_name}' outperformed both "
            f"Holt-Winters variants on held-out data. This means ~{len(series)} months "
            f"of history is not enough for trend/seasonality modeling to add real value "
            f"here - the naive approach is the more honest choice, not a fallback to be "
            f"ashamed of. State this plainly if asked in a viva."
        )
    else:
        print(f"\n'{winner_name}' outperformed the naive baselines - a real, earned result.")

    # Refit the WINNING approach type on the full series (train+test) so the
    # saved model uses all available real data to forecast the actual future.
    if winner_name == "Naive - Last Value":
        final_model = NaiveLastValueForecaster(last_value=float(series.iloc[-1]))
    elif winner_name == "Naive - Moving Average":
        window = min(MOVING_AVERAGE_WINDOW, len(series))
        final_model = NaiveMovingAverageForecaster(
            average_value=float(series.iloc[-window:].mean()), window=window
        )
    elif winner_name == "Holt-Winters - Trend Only":
        final_model = ExponentialSmoothing(series, trend="add", seasonal=None).fit()
    else:
        final_model = ExponentialSmoothing(
            series, trend="add", seasonal="add", seasonal_periods=12
        ).fit()

    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    joblib.dump(final_model, f"{ARTIFACT_DIR}/forecaster_model.joblib")
    joblib.dump(series.index.max(), f"{ARTIFACT_DIR}/forecaster_last_date.joblib")
    joblib.dump(winner_name, f"{ARTIFACT_DIR}/forecaster_method_name.joblib")
    print(f"\nSaved '{winner_name}' as the production forecasting model to {ARTIFACT_DIR}/.")


if __name__ == "__main__":
    main()
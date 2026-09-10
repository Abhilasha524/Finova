"""
Loads the trained forecasting model and produces future month predictions.
"""
import os

import joblib
import pandas as pd

_ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

_model = None
_last_date = None


def _load():
    global _model, _last_date
    if _model is not None:
        return
    model_path = os.path.join(_ARTIFACT_DIR, "forecaster_model.joblib")
    date_path = os.path.join(_ARTIFACT_DIR, "forecaster_last_date.joblib")
    if not (os.path.exists(model_path) and os.path.exists(date_path)):
        raise FileNotFoundError(
            "No trained forecasting model found. Run "
            "'python -m app.ml.train_forecaster' from the backend folder first."
        )
    _model = joblib.load(model_path)
    _last_date = joblib.load(date_path)


def forecast_next_months(months: int = 3) -> list[dict]:
    _load()
    predictions = _model.forecast(months)
    future_dates = pd.date_range(start=_last_date, periods=months + 1, freq="MS")[1:]
    return [
        {"month": date.strftime("%Y-%m"), "predicted_expense": float(max(0, value))}
        for date, value in zip(future_dates, predictions.values)
    ]
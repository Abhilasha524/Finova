"""
Loads the trained categorization model (saved by train_categorizer.py) and
exposes a simple predict_category() function for the API to call.

The model is loaded ONCE, the first time it's needed, and reused after that -
not reloaded from disk on every request, which would be slow.
"""
import os

import joblib

_ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

_vectorizer = None
_model = None
_model_name = None


def _load():
    global _vectorizer, _model, _model_name
    if _model is not None:
        return  # already loaded, nothing to do

    vec_path = os.path.join(_ARTIFACT_DIR, "vectorizer.joblib")
    model_path = os.path.join(_ARTIFACT_DIR, "categorizer_model.joblib")
    name_path = os.path.join(_ARTIFACT_DIR, "model_name.joblib")

    if not (os.path.exists(vec_path) and os.path.exists(model_path)):
        raise FileNotFoundError(
            "No trained model found. Run 'python -m app.ml.train_categorizer' "
            "from the backend folder first, then restart the server."
        )

    _vectorizer = joblib.load(vec_path)
    _model = joblib.load(model_path)
    _model_name = joblib.load(name_path) if os.path.exists(name_path) else "unknown"


def predict_category(description: str) -> dict:
    """Returns the predicted category for a raw transaction description,
    plus a confidence score when the underlying model supports it."""
    _load()

    features = _vectorizer.transform([description])
    predicted = _model.predict(features)[0]

    confidence = None
    if hasattr(_model, "predict_proba"):
        probabilities = _model.predict_proba(features)[0]
        confidence = float(max(probabilities))

    return {
        "predicted_category": predicted,
        "confidence": confidence,
        "model_used": _model_name,
    }
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import get_current_user
from app.ml.predict import predict_category
from app.models import User

router = APIRouter(prefix="/categorize", tags=["categorization"])


class CategorizeRequest(BaseModel):
    description: str


class CategorizeResponse(BaseModel):
    predicted_category: str
    confidence: Optional[float] = None
    model_used: str


@router.post("/", response_model=CategorizeResponse)
def categorize(
    payload: CategorizeRequest,
    current_user: User = Depends(get_current_user),
):
    if not payload.description.strip():
        raise HTTPException(status_code=400, detail="description cannot be empty")

    try:
        result = predict_category(payload.description)
    except FileNotFoundError as e:
        # Model hasn't been trained yet - this is a clear, actionable error,
        # not a silent 500 crash.
        raise HTTPException(status_code=503, detail=str(e))

    return result
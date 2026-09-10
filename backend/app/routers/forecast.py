from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import get_current_user
from app.ml.forecast_predict import forecast_next_months
from app.models import User
from app.schemas import ForecastResponse

router = APIRouter(prefix="/forecast", tags=["forecasting"])


@router.get("/", response_model=ForecastResponse)
def get_forecast(
    months: int = Query(default=3, ge=1, le=12),
    current_user: User = Depends(get_current_user),
):
    try:
        predictions = forecast_next_months(months)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"forecast": predictions}
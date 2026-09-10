from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.ml.anomaly import detect_anomalies, get_saved_anomalies, save_anomalies
from app.models import User
from app.schemas import AnomalyDetectionSummary, AnomalyListResponse

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.post("/detect", response_model=AnomalyDetectionSummary)
def run_anomaly_detection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    anomalies = detect_anomalies(db, current_user.id)
    save_anomalies(db, current_user.id, anomalies)
    return {"anomalies_found": len(anomalies), "anomalies": anomalies}


@router.get("/", response_model=AnomalyListResponse)
def list_saved_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    anomalies = get_saved_anomalies(db, current_user.id)
    return {"count": len(anomalies), "anomalies": anomalies}
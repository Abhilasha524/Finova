from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Transaction, User
from app.schemas import TransactionOut, UploadSummary
from app.services.ingestion import ingest_csv

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/upload", response_model=UploadSummary)
async def upload_transactions(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported right now")

    file_bytes = await file.read()
    summary = ingest_csv(db, user_id=current_user.id, file_bytes=file_bytes)
    return summary


@router.get("/", response_model=list[TransactionOut])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.txn_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # .category is an existing SQLAlchemy relationship (see models.py) - this
    # does not run a new hand-written query, it just reads the already-joined
    # related row per transaction.
    return [
        TransactionOut(
            id=t.id,
            txn_date=t.txn_date,
            description=t.description,
            amount=t.amount,
            txn_type=t.txn_type,
            category_id=t.category_id,
            category=t.category.name if t.category else None,
            is_recurring=t.is_recurring,
            payment_mode=t.payment_mode,
        )
        for t in transactions
    ]

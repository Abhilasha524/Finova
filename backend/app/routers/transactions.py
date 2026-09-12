from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db

from app.models import (
    Category,
    LearnedMerchantRule,
    Transaction,
    User,
)

from app.schemas import (
    TransactionOut,
    UploadSummary,
    TransactionCategoryUpdate,
)

from app.services.ingestion import ingest_csv

from app.ml.merchant_rules import (
    extract_merchant_pattern,
)


router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.post(
    "/upload",
    response_model=UploadSummary,
)
async def upload_transactions(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported right now",
        )

    file_bytes = await file.read()

    summary = ingest_csv(
        db,
        user_id=current_user.id,
        file_bytes=file_bytes,
    )

    return summary


@router.get(
    "/",
    response_model=list[TransactionOut],
)
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id
        )
        .order_by(
            Transaction.txn_date.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        TransactionOut(
            id=t.id,
            txn_date=t.txn_date,
            description=t.description,
            amount=t.amount,
            txn_type=t.txn_type,
            category_id=t.category_id,
            category=(
                t.category.name
                if t.category
                else None
            ),
            is_recurring=t.is_recurring,
            payment_mode=t.payment_mode,
        )
        for t in transactions
    ]


@router.patch(
    "/{transaction_id}/category",
    response_model=TransactionOut,
)
def update_transaction_category(
    transaction_id: str,
    payload: TransactionCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ---------------------------------------------------------
    # Find transaction belonging to current user
    # ---------------------------------------------------------

    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    # ---------------------------------------------------------
    # Validate category
    # ---------------------------------------------------------

    category_name = payload.category.strip().title()

    if not category_name:
        raise HTTPException(
            status_code=400,
            detail="Category cannot be empty",
        )

    # ---------------------------------------------------------
    # Get existing category or create it
    # ---------------------------------------------------------

    category = (
        db.query(Category)
        .filter(
            Category.name == category_name
        )
        .first()
    )

    if category is None:
        category = Category(
            name=category_name
        )

        db.add(category)
        db.flush()

    # ---------------------------------------------------------
    # Update transaction
    # ---------------------------------------------------------

    transaction.category_id = category.id

    # ---------------------------------------------------------
    # Learn from user's correction
    # ---------------------------------------------------------

    merchant_pattern = extract_merchant_pattern(
        transaction.description
    )

    if merchant_pattern:
        existing_rule = (
            db.query(LearnedMerchantRule)
            .filter(
                LearnedMerchantRule.user_id
                == current_user.id,
                LearnedMerchantRule.merchant_pattern
                == merchant_pattern,
            )
            .first()
        )

        if existing_rule:
            existing_rule.category = category_name

        else:
            learned_rule = LearnedMerchantRule(
                user_id=current_user.id,
                merchant_pattern=merchant_pattern,
                category=category_name,
            )

            db.add(learned_rule)

    # ---------------------------------------------------------
    # Save transaction + learned rule
    # ---------------------------------------------------------

    db.commit()
    db.refresh(transaction)

    return TransactionOut(
        id=transaction.id,
        txn_date=transaction.txn_date,
        description=transaction.description,
        amount=transaction.amount,
        txn_type=transaction.txn_type,
        category_id=transaction.category_id,
        category=(
            transaction.category.name
            if transaction.category
            else None
        ),
        is_recurring=transaction.is_recurring,
        payment_mode=transaction.payment_mode,
    )
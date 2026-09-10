from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TransactionOut(BaseModel):
    id: str
    txn_date: date
    description: str
    amount: float
    txn_type: str
    category_id: Optional[str] = None
    category: Optional[str] = None
    is_recurring: bool
    payment_mode: Optional[str] = None

    class Config:
        from_attributes = True


class UploadSummary(BaseModel):
    rows_received: int
    rows_inserted: int
    duplicates_skipped: int
    rows_skipped: int
    skipped_reasons: list[str]
    duplicate_reasons: list[str]

class CategoryBreakdown(BaseModel):
    category: str
    total_amount: float
    transaction_count: int


class MonthlyTrendPoint(BaseModel):
    month: str
    total_expense: float


class AnalyticsSummary(BaseModel):
    total_income: float
    total_expense: float
    total_transfer_out: float
    net_savings: float
    category_breakdown: list[CategoryBreakdown]
    monthly_trend: list[MonthlyTrendPoint]


class AnomalyOut(BaseModel):
    transaction_id: str
    reason: str
    anomaly_score: float


class AnomalyDetectionSummary(BaseModel):
    anomalies_found: int
    anomalies: list[AnomalyOut]

class ForecastPoint(BaseModel):
    month: str
    predicted_expense: float


class ForecastResponse(BaseModel):
    forecast: list[ForecastPoint]

class AnomalyDetailOut(BaseModel):
    transaction_id: str
    description: str
    amount: float
    txn_date: date
    category: str
    reason: str
    anomaly_score: float


class AnomalyListResponse(BaseModel):
    count: int
    anomalies: list[AnomalyDetailOut]
class GoalCreate(BaseModel):
    title: str
    target_amount: float
    target_date: date


class GoalOut(BaseModel):
    id: str
    title: str
    target_amount: float
    target_date: date
    current_savings: float
    progress_percent: float
    remaining_amount: float
    required_monthly_saving: float

    class Config:
        from_attributes = True

class PersonaOut(BaseModel):
    persona: str
    description: str
    spending_volatility: float
    category_diversity: int
    weekend_spending_ratio: float
    recurring_expense_ratio: float

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
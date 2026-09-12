import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    String,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    transactions = relationship("Transaction", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    learned_merchant_rules = relationship(
        "LearnedMerchantRule",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False)

    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    txn_date = Column(Date, nullable=False, index=True)

    # Raw text used for NLP categorization
    description = Column(String, nullable=False)

    amount = Column(Float, nullable=False)

    # "Income", "Expense", or "Transfer-Out"
    txn_type = Column(String, nullable=False)

    category_id = Column(
        UUID(as_uuid=False),
        ForeignKey("categories.id"),
        nullable=True,
    )

    is_recurring = Column(Boolean, default=False)
    payment_mode = Column(String, nullable=True)

    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    anomaly_flag = relationship(
        "AnomalyFlag",
        back_populates="transaction",
        uselist=False,
    )


class AnomalyFlag(Base):
    __tablename__ = "anomaly_flags"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    transaction_id = Column(
        UUID(as_uuid=False),
        ForeignKey("transactions.id"),
        nullable=False,
        unique=True,
    )

    # Human-readable explanation, not just a score
    reason = Column(String, nullable=False)

    anomaly_score = Column(Float, nullable=False)

    transaction = relationship(
        "Transaction",
        back_populates="anomaly_flag",
    )


class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
    )

    title = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    target_date = Column(Date, nullable=False)

    user = relationship("User", back_populates="goals")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
    )

    message = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="alerts")


class LearnedMerchantRule(Base):
    """
    Stores merchant/category corrections made by a user.

    Example:
        merchant_pattern = "ABC STORE"
        category = "Food"

    The rule belongs to a specific user so that corrections from one
    Finova user do not affect another user's categorization.
    """

    __tablename__ = "learned_merchant_rules"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        default=gen_uuid,
    )

    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    merchant_pattern = Column(
        String,
        nullable=False,
        index=True,
    )

    category = Column(
        String,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )

    user = relationship(
        "User",
        back_populates="learned_merchant_rules",
    )
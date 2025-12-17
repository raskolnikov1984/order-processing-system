# payment-service/src/payment_service/models/database.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class PaymentSQL(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, nullable=False, index=True)
    payment_id = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="PROCESSED")
    retry_count = Column(Integer, default=0)
    gateway_response = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

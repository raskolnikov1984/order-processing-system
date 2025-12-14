from sqlalchemy import Column, String, Integer, Numeric, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class OrderSQL(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=True)
    status = Column(String, default="PENDING", nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OrderItemSQL(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, nullable=False)
    product_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

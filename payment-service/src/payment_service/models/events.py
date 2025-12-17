# payment-service/src/payment_service/events/models.py
from pydantic import BaseModel, Field
from datetime import datetime, UTC
from enum import Enum


class EventType(str, Enum):
    ORDER_CREATED = "OrderCreated"
    INVENTORY_RESERVED = "InventoryReserved"
    INVENTORY_UNAVAILABLE = "InventoryUnavailable"
    PAYMENT_PROCESSED = "PaymentProcessed"
    PAYMENT_FAILED = "PaymentFailed"
    ORDER_COMPLETED = "OrderCompleted"


class Item(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float


class InventoryReservedEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp: str
    order_id: str
    reservation_id: str
    total_amount: float


class PaymentProcessedEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.now(UTC)}")
    event_type: EventType = EventType.PAYMENT_PROCESSED
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    order_id: str
    payment_id: str
    amount: float


class PaymentFailedEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.now(UTC)}")
    event_type: EventType = EventType.PAYMENT_FAILED
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    order_id: str
    amount: float
    reason: str
    retry_count: int = 0

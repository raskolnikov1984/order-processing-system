from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, UTC
from enum import Enum

from .schemas import Item


class EventType(str, Enum):
    ORDER_CREATED = "OrderCreated"
    ORDER_CONFIRMED = "OrderConfirmed"
    ORDER_CANCELLED = "OrderCancelled"
    INVENTORY_RESERVED = "InventoryReserved"
    INVENTORY_UNAVAILABLE = "InventoryUnavailable"
    PAYMENT_PROCESSED = "PaymentProcessed"
    PAYMENT_FAILED = "PaymentFailed"
    ORDER_COMPLETED = "OrderCompleted"


class OrderCreatedEvent(BaseModel):
    event_id: str = Field(
        default_factory=lambda: f"evt_{datetime.now(UTC)}"
    )
    event_type: EventType = EventType.ORDER_CREATED
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC))
    order_id: str
    customer_id: str
    customer_email: str
    items: List[Item]
    total_amount: float

    class ConfigDict:
        use_enum_values = True


class InventoryReservedEvent(BaseModel):
    event_id: str = Field(
        default_factory=lambda: f"evt_{datetime.now(UTC)}"
    )
    event_type: EventType = EventType.INVENTORY_RESERVED
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC))
    order_id: str
    reservation_id: str


class InventoryUnavailableEvent(BaseModel):
    event_id: str = Field(
        default_factory=lambda: f"evt_{datetime.now(UTC)}"
    )
    event_type: EventType = EventType.INVENTORY_UNAVAILABLE
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC))
    order_id: str
    reason: str


class OrderConfirmedEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.now(UTC)}")
    event_type: EventType = EventType.ORDER_CONFIRMED
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    order_id: str
    reservation_id: str


class OrderCompletedEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.now(UTC)}")
    event_type: EventType = EventType.ORDER_COMPLETED
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    order_id: str


class OrderCancelledEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.now(UTC)}")
    event_type: EventType = EventType.ORDER_CANCELLED
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    order_id: str
    cancellation_reason: str


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

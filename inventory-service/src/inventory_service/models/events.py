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
    total_amount: float


class InventoryUnavailableEvent(BaseModel):
    event_id: str = Field(
        default_factory=lambda: f"evt_{datetime.now(UTC)}"
    )
    event_type: EventType = EventType.INVENTORY_UNAVAILABLE
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC))
    order_id: str
    reason: str

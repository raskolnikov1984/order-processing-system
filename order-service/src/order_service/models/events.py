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
    event_id: str
    event_type: EventType = EventType.INVENTORY_RESERVED
    timestamp: datetime
    order_id: str
    reservation_id: str
    items_reserved: List[Item]


class PaymentProcessedeEvent:
    pass


class PaymentFailedEvent:
    pass

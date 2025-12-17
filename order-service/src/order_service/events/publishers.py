from src.order_service.models.events import (
    OrderConfirmedEvent,
    OrderCancelledEvent)
from src.order_service.api.dependencies import get_rabbitmq_client
from src.order_service.models.events import OrderCreatedEvent


async def publish_order_created(event: OrderCreatedEvent) -> None:
    """Publica evento de orden creada"""
    client = get_rabbitmq_client()

    await client.publish_event(
        routing_key="order.created",
        event=event
    )


async def publish_order_confirmed(event: OrderConfirmedEvent) -> None:
    """Publica orden confirmada (para notificaciones)"""
    client = get_rabbitmq_client()
    await client.publish_event(
        routing_key="order.confirmed",
        event=event
    )


async def publish_order_cancelled(event: OrderCancelledEvent) -> None:
    """Publica orden cancelada (para liberar inventario/notificaciones)"""
    client = get_rabbitmq_client()
    await client.publish_event(
        routing_key="order.cancelled",
        event=event
    )

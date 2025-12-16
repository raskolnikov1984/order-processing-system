from src.inventory_service.models.events import OrderCreatedEvent
from src.inventory_service.api.dependencies import get_rabbitmq_client


async def publish_order_created(event: OrderCreatedEvent) -> None:
    """Publica evento de orden creada"""
    client = get_rabbitmq_client()

    await client.publish_event(
        routing_key="order.created",
        event=event
    )

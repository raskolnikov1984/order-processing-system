from src.inventory_service.models.events import (
    InventoryReservedEvent, InventoryUnavailableEvent)
from src.inventory_service.api.dependencies import get_rabbitmq_client


async def publish_inventory_reserved(event: InventoryReservedEvent) -> None:
    client = get_rabbitmq_client()
    await client.publish_event(
        routing_key="inventory.reserved",
        event=event
    )


async def publish_inventory_unavailable(
        event: InventoryUnavailableEvent) -> None:
    """Publica evento cuando no hay inventario suficiente"""
    client = get_rabbitmq_client()
    await client.publish_event(
        routing_key="inventory.unavailable",
        event=event
    )

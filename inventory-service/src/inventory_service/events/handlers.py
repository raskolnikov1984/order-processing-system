from src.inventory_service.models.events import (
    OrderCreatedEvent,
    InventoryUnavailableEvent,
    InventoryReservedEvent,
)
from src.inventory_service.events.publishers import (
    publish_inventory_reserved, publish_inventory_unavailable)
from src.inventory_service.events.router import event_router
from src.inventory_service.logger import logger
from src.inventory_service.api.dependencies import get_inventory_service


@event_router.register_decorator("OrderCreated")
async def handle_order_created(event_data: dict):
    """Maneja creación de orden: reserva inventario o emite fallo"""
    logger.info(f"📦 OrderCreated recibido: {event_data['order_id']}")

    order_event = OrderCreatedEvent(**event_data)

    service = get_inventory_service()

    success, error_message = await service.reserve_inventory(order_event)

    if success:
        logger.info(f"Inventario reservado para orden {order_event.order_id}")
        reserved_event = InventoryReservedEvent(
            order_id=order_event.order_id,
            total_amount=order_event.total_amount,
            reservation_id=f"res_{order_event.order_id}"
        )
        await publish_inventory_reserved(reserved_event)
    else:
        logger.error(f"❌ Inventario NO disponible: {error_message}")

        unavailable_event = InventoryUnavailableEvent(
            order_id=order_event.order_id,
            reason=error_message
        )
        await publish_inventory_unavailable(unavailable_event)


@event_router.register_decorator("InventoryReserved")
async def handle_inventory_reserved(event_data: dict):
    """Maneja orden cancelada: libera inventario"""
    logger.warning(f"InventoryReserved: {event_data['order_id']}")


@event_router.register_decorator("InventoryUnavailable")
async def handle_inventory_unavailable(event_data: dict):
    """Maneja orden cancelada: libera inventario"""
    logger.warning(f"InventoryUnavailable: {event_data['order_id']}")


@event_router.register_decorator("OrderCancelled")
async def handle_order_cancelled(event_data: dict):
    """Maneja orden cancelada: libera inventario"""
    logger.warning(f"OrderCancelled: {event_data['order_id']}")


@event_router.register_decorator("InventoryChecked")
async def handle_inventory_checked(event_data: dict):
    """Verifica la Disponibilidad del Inventario"""
    logger.info(f"InventoryChecked: {event_data}")


# Para funciones que no puedas decorar directamente
# def handle_inventory_checked(event_data: dict):
#     """Handler síncrono (también soportado)"""
#     logger.info(f"InventoryChecked: {event_data}")
#     # Lógica aquí


# event_router.register("InventoryChecked", handle_inventory_checked)

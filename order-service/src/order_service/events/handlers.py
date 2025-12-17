from src.order_service.events.router import event_router
from src.order_service.api.dependencies import get_order_service
from src.order_service.models.events import (
    InventoryReservedEvent,
    InventoryUnavailableEvent,
    OrderConfirmedEvent,
    OrderCancelledEvent,
    OrderCompletedEvent,
    PaymentProcessedEvent,
    PaymentFailedEvent,
)
from src.order_service.events.publishers import (
    publish_order_confirmed,
    publish_order_completed,
    publish_order_cancelled)
from src.order_service.logger import logger


@event_router.register_decorator("InventoryReserved")
async def handle_inventory_reserved(event_data: dict):
    """
    ✅ Se ejecuta en ORDER SERVICE cuando inventario está reservado
    """
    logger.info(f"InventoryReserved recibido: {event_data['order_id']}")

    event = InventoryReservedEvent(**event_data)
    service = get_order_service()

    await service.confirm_order(int(event.order_id))

    confirmed_event = OrderConfirmedEvent(
        order_id=event.order_id,
        reservation_id=event.reservation_id
    )
    await publish_order_confirmed(confirmed_event)


@event_router.register_decorator("InventoryUnavailable")
async def handle_inventory_unavailable(event_data: dict):
    """
    ❌ Se ejecuta en ORDER SERVICE cuando inventario NO está disponible
    """
    logger.error(f"❌ InventoryUnavailable: {event_data['order_id']}")

    event = InventoryUnavailableEvent(**event_data)
    service = get_order_service()

    await service.cancel_order(
        event.order_id,
        reason=event.reason
    )

    cancelled_event = OrderCancelledEvent(
        order_id=event.order_id,
        cancellation_reason=event.reason
    )
    await publish_order_cancelled(cancelled_event)


@event_router.register_decorator("PaymentProcessed")
async def handle_payment_processed(event_data: dict) -> None:
    """Maneja evento de pago exitoso"""
    logger.info(f"Pago procesado: {event_data}")

    event = PaymentProcessedEvent(**event_data)
    service = get_order_service()

    await service.process_order(
        event.order_id
    )

    completed_event = OrderCompletedEvent(
        order_id=event.order_id
    )

    await publish_order_completed(completed_event)


@event_router.register_decorator("PaymentFailed")
async def handle_payment_failed(event_data: dict) -> None:
    """Maneja evento de pago fallido"""
    logger.error(
        f"❌ Pago fallido: {event_data}")

    event = PaymentFailedEvent(**event_data)
    service = get_order_service()

    await service.process_failed_order(
        event.order_id,
        reason=event.reason
    )

import asyncio
from src.payment_service.models.events import (
    InventoryReservedEvent,
    PaymentProcessedEvent,
    PaymentFailedEvent
)
from src.payment_service.events.publishers import (
    publish_payment_processed,
    publish_payment_failed
)
from src.payment_service.events.router import event_router
from src.payment_service.logger import logger
from src.payment_service.api.dependencies import payment_processor


@event_router.register_decorator("InventoryReserved")
async def handle_inventory_reserved(event_data: dict):
    """
    Procesa pago simulado con 80% éxito y retry logic.
    """
    logger.info(f"InventoryReserved recibido: {event_data['order_id']}")

    try:
        event = InventoryReservedEvent(**event_data)
        max_retries = 3
        retry_count = 0

        while retry_count <= max_retries:
            success, payment_id, error = await payment_processor.process(
                order_id=event.order_id,
                amount=event.total_amount,
                retry_count=retry_count
            )

            if success:
                processed_event = PaymentProcessedEvent(
                    order_id=event.order_id,
                    payment_id=payment_id,
                    amount=event.total_amount
                )
                await publish_payment_processed(processed_event)
                logger.info(f"Pago procesado y publicado: {payment_id}")
                break

            # Fallo: retry con exponential backoff
            retry_count += 1

            if retry_count <= max_retries:
                wait_time = 2 ** retry_count  # 2, 4, 8 segundos
                logger.warning(
                    f"Pago falló, reintento {retry_count}/{max_retries} "
                    f"en {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
            else:
                # ❌ Máximos intentos alcanzados
                logger.error(f"❌ Pago falló después de {max_retries} intentos")

                failed_event = PaymentFailedEvent(
                    order_id=event.order_id,
                    amount=event.total_amount,
                    reason=error or "Unknown payment error",
                    retry_count=retry_count
                )
                await publish_payment_failed(failed_event)
                break

    except Exception as e:
        logger.error(
            f"❌ Error crítico en handle_inventory_reserved: {e}", exc_info=True
        )

        failed_event = PaymentFailedEvent(
            order_id=event_data.get("order_id", "unknown"),
            amount=event_data.get("total_amount", 0.0),
            reason=f"Critical error: {str(e)}"
        )
        await publish_payment_failed(failed_event)

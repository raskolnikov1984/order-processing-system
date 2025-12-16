# import asyncio
# from ..models.events import PaymentFailedEvent, PaymentProcessedeEvent
from ..models.database import update_order_status
from ..api.dependencies import get_rabbitmq_client
from src.inventory_service.logger import logger


async def handle_payment_processed(event_data: dict) -> None:
    """Maneja evento de pago exitoso"""
    logger.info(f"Pago procesado: {event_data}")

    await update_order_status(
        event_data["order_id"],
        "COMPLETED"
    )


async def handle_payment_failed(event_data: dict) -> None:
    """Maneja evento de pago fallido"""
    logger.error(
        f"❌ Pago fallido: {event_data}")

    await update_order_status(
        event_data["order_id"],
        "PAYMENT_FAILED",
        reason=event_data.get("failure_reason")
    )


async def start_consumers() -> None:
    """Inicia todos los consumidores del servicio"""
    client = get_rabbitmq_client()

    # Suscribir a múltiples eventos
    await client.setup_consumer(
        queue_name="order_service_queue",
        routing_keys=[
            "payment.processed",  # Solo eventos relevantes
            "payment.failed",
        ],
        callback=lambda body: (
            handle_payment_processed(body)
            if body.get("event_type") == "PaymentProcessed"
            else handle_payment_failed(body)
        )
    )

# payment-service/src/payment_service/events/publishers.py
from src.payment_service.models.events import (
    PaymentProcessedEvent,
    PaymentFailedEvent
)
from src.payment_service.api.dependencies import get_rabbitmq_client
from src.payment_service.logger import logger


async def publish_payment_processed(event: PaymentProcessedEvent) -> None:
    """Publica evento de pago exitoso"""
    client = get_rabbitmq_client()
    await client.publish_event(
        routing_key="payment.processed",
        event=event
    )

    logger.info(f"Evento publicado: payment.processed - {event.order_id}")


async def publish_payment_failed(event: PaymentFailedEvent) -> None:
    """Publica evento de pago fallido"""
    client = get_rabbitmq_client()
    await client.publish_event(
        routing_key="payment.failed",
        event=event
    )

    logger.info(f"Evento publicado: payment.failed - {event.order_id}")

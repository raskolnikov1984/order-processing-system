from ..api.dependencies import get_rabbitmq_client
from .router import event_router
from src.payment_service.logger import logger


async def start_consumers() -> None:
    """Inicia consumidor para eventos de inventario"""
    client = get_rabbitmq_client()

    await client.setup_consumer(
        queue_name="payment_service_queue",
        routing_keys=[
            "inventory.reserved",
        ],
        callback=event_router.dispatch
    )

    logger.info("Consumers de Payment Service iniciados")

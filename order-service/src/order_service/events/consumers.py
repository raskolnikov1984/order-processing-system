from ..api.dependencies import get_rabbitmq_client
from .router import event_router
from src.order_service.logger import logger


async def start_consumers() -> None:
    """Inicia todos los consumidores del servicio"""
    client = get_rabbitmq_client()

    await client.setup_consumer(
        queue_name="order_service_queue",
        routing_keys=[
            "payment.*",
            "inventory.*",
        ],
        callback=event_router.dispatch
    )
    logger.info("Consumers de Inventory Service iniciados... ")

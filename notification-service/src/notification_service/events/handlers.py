from src.notification_service.events.router import event_router
from src.notification_service.logger import logger


@event_router.register_decorator("PaymentProcessed")
async def handle_payment_processed(event_data: dict):
    logger.info("Notificacion Enviada")

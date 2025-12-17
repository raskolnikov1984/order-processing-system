from typing import Dict, Callable, Any
import asyncio
from src.payment_service.logger import logger


class EventRouter:
    def __init__(self):
        self.handlers: Dict[str, Callable[[dict], Any]] = {}

    def register(self, event_type: str, handler: Callable):
        logger.info(f"Handler registrado: {event_type}")
        self.handlers[event_type] = handler
        return handler

    def register_decorator(self, event_type: str):
        def decorator(handler: Callable):
            self.register(event_type, handler)
            return handler
        return decorator

    async def dispatch(self, event_data: dict) -> None:
        event_type = event_data.get("event_type")

        if not event_type:
            logger.error(f"Evento sin event_type: {event_data}")
            return

        handler = self.handlers.get(event_type)

        if handler:
            try:
                logger.info(f"Procesando: {event_type}")
                result = handler(event_data)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error en {event_type}: {e}", exc_info=True)
        else:
            logger.warning(f"No hay handler: {event_type}")


event_router = EventRouter()

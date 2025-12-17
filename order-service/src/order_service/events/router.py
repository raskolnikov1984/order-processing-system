from typing import Dict, Callable, Any
import asyncio
from src.order_service.logger import logger


class EventRouter:
    """
    Router que mapea event_types a handlers async.
    Permite registrar múltiples acciones fácilmente.
    """

    def __init__(self):
        # Diccionario: event_type -> handler_function
        self.handlers: Dict[str, Callable[[dict], Any]] = {}

    def register(self, event_type: str, handler: Callable):
        """Registra un handler para un event_type"""

        logger.info(f"Handler registrado para {event_type}")
        self.handlers[event_type] = handler
        return handler

    def register_decorator(self, event_type: str):
        """Decorator para registrar handlers"""

        def decorator(handler: Callable):
            self.register(event_type, handler)
            return handler
        return decorator

    async def dispatch(self, event_data: dict) -> None:
        """
        Recibe un evento y lo envía al handler correspondiente.
        Maneja errores de forma aislada (un error no afecta otros handlers).
        """
        event_type = event_data.get("event_type")

        if not event_type:
            logger.error(f"Evento sin event_type: {event_data}")
            return

        handler = self.handlers.get(event_type)

        if handler:
            try:
                logger.info(f"Procesando evento: {event_type}")
                result = handler(event_data)

                if asyncio.iscoroutine(result):
                    await result

            except Exception as e:
                logger.error(
                    f"Error procesando {event_type}: {e}", exc_info=True)
        else:
            logger.warning(f"No hay handler para event_type: {event_type}")


event_router = EventRouter()

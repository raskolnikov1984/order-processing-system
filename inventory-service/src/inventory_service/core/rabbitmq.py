import json
from typing import Optional, Callable, Any
from aio_pika import connect_robust, Message, ExchangeType
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractExchange
from pydantic import BaseModel
from src.inventory_service.logger import logger


class RabbitMQClient:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.exchange: Optional[AbstractExchange] = None
        self.exchange_name = "order_exchange"

    async def connect(self) -> None:
        """Establece conexión robusta con RabbitMQ"""
        self.connection = await connect_robust(
            self.amqp_url,
            client_properties={"connection_name": "order_service"},
        )
        self.channel = await self.connection.channel()

        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            ExchangeType.TOPIC,
            durable=True,
        )

        logger.info(f"Conectado a RabbitMQ: {self.exchange_name}")

    async def disconnect(self) -> None:
        """Cierra conexión de forma segura"""
        if self.connection:
            await self.connection.close()

            logger.info("Desconectado de RabbitMQ")

    async def publish_event(self, routing_key: str, event: BaseModel) -> None:
        """Publica un evento al exchange"""
        if not self.exchange:
            raise RuntimeError("RabbitMQ no conectado")

        message_body = json.dumps(
            event.model_dump(),
            default=str  # Maneja datetime
        )

        message = Message(
            body=message_body.encode("utf-8"),
            content_type="application/json",
            delivery_mode=2,  # Persistente
        )

        await self.exchange.publish(message, routing_key=routing_key)
        logger.info(f"Evento publicado: {routing_key} - {event.model_dump()}")

    async def setup_consumer(
        self,
        queue_name: str,
        routing_keys: list[str],
        callback: Callable[[Any], None]
    ) -> None:
        """Configura una cola y sus bindings para consumir eventos"""
        if not self.channel:
            raise RuntimeError("RabbitMQ no conectado")

        # Declara cola durable
        queue = await self.channel.declare_queue(
            queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": "dlx_exchange",  # Para dead-letter
            }
        )

        # Binding múltiples routing keys
        for routing_key in routing_keys:
            await queue.bind(self.exchange_name, routing_key=routing_key)

            logger.info(f"Cola '{queue_name}' bind a '{routing_key}'")

        # Inicia consumidor
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        body = json.loads(message.body.decode())
                        await callback(body)
                    except Exception as e:
                        logger.error(
                            f"❌ Error procesando mensaje: {e}"
                        )
                        # NACK para requeue o DLQ
                        await message.nack(requeue=False)

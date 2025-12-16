#!/usr/bin/env python3
import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, call, patch
import json
from src.order_service.models.events import OrderCreatedEvent


@pytest.mark.anyio
class TestRabbitMQCLientUnit:
    """Tests unitarios con mocking para RabbitMQClient"""
    async def test_connect_creates_channel_and_exchange(
            self, rabbitmq_client_mock, mock_channel
    ):
        """Test que connect crea canal y exchange correctamente"""
        # Arrange: Resetear el cliente
        rabbitmq_client_mock.connection = None
        rabbitmq_client_mock.channel = None
        rabbitmq_client_mock.exchange = None

        # 🔥 CORREGIDO: Mock de conexión con método channel() configurado
        mock_connection = AsyncMock()
        mock_connection.channel = AsyncMock(return_value=mock_channel)

        # Patch al nivel correcto (donde se importa)
        with patch("src.order_service.core.rabbitmq.connect_robust",
                   return_value=mock_connection):
            # Act
            await rabbitmq_client_mock.connect()

            # Assert
            assert rabbitmq_client_mock.connection is mock_connection
            assert rabbitmq_client_mock.channel is mock_channel
            mock_channel.declare_exchange.assert_called_once()

            # Verificar parámetros del exchange
            call_args = mock_channel.declare_exchange.call_args
            assert call_args[0][0] == "order_exchange"
            assert call_args[1]["durable"] is True

    async def test_disconnect_closes_connection(self, rabbitmq_client_mock):
        """Test que disconnect cierra la conexión"""
        await rabbitmq_client_mock.disconnect()

        rabbitmq_client_mock.connection.close.assert_called_once()

    async def test_publish_event_success(
            self, rabbitmq_client_mock, sample_order_event):
        """Test publicación exitosa de evento"""
        routing_key = "order.created"

        await rabbitmq_client_mock.publish_event(
            routing_key, sample_order_event)

        rabbitmq_client_mock.exchange.publish.assert_called_once()

        call_args = rabbitmq_client_mock.exchange.publish.call_args
        message = call_args[0][0]
        published_routing_key = call_args[1]['routing_key']

        assert published_routing_key == routing_key
        assert isinstance(message.body, bytes)

        body_dict = json.loads(message.body.decode())
        assert body_dict["order_id"] == sample_order_event.order_id
        assert body_dict["event_type"] == "OrderCreated"
        assert message.content_type == "application/json"
        assert message.delivery_mode == 2  # Persistente

    async def test_publish_event_without_connection_fails(
            self, rabbitmq_client_mock):
        """Test que publicar sin conexión levanta RuntimeError"""

        rabbitmq_client_mock.exchange = None
        event = OrderCreatedEvent(
            order_id="test",
            customer_id="test",
            customer_email="test@test.com",
            items=[], total_amount=0
        )

        with pytest.raises(RuntimeError, match="RabbitMQ no conectado"):
            await rabbitmq_client_mock.publish_event("test.key", event)

    async def test_setup_consumer_creates_queue_and_bindings(
        self, rabbitmq_client_mock
    ):
        """Test setup de consumidor crea cola y bindings"""
        # Arrange
        queue_name = "test_orders_queue"
        routing_keys = ["order.created", "order.cancelled"]
        callback_mock = AsyncMock()

        await rabbitmq_client_mock.setup_consumer(
            queue_name, routing_keys, callback_mock)

        rabbitmq_client_mock.channel.declare_queue.assert_called_once_with(
            queue_name,
            durable=True,
            arguments={"x-dead-letter-exchange": "dlx_exchange"}
        )

        queue_mock = rabbitmq_client_mock.channel.declare_queue.return_value
        assert queue_mock.bind.call_count == 2

        # Verificar que se suscribe a las routing keys correctas
        expected_calls = [
            call(
                rabbitmq_client_mock.exchange_name,
                routing_key="order.created"
            ),
            call(
                rabbitmq_client_mock.exchange_name,
                routing_key="order.cancelled"
            )
        ]
        queue_mock.bind.assert_has_calls(expected_calls)

    async def test_setup_consumer_without_channel_fails(
            self, rabbitmq_client_mock):
        """Test que setup_consumer sin canal levanta RuntimeError"""
        # Arrange
        rabbitmq_client_mock.channel = None

        with pytest.raises(RuntimeError, match="RabbitMQ no conectado"):
            await rabbitmq_client_mock.setup_consumer("test", [], lambda x: x)

    async def test_consumer_callback_processes_message(
        self, rabbitmq_client_mock, mock_channel
    ):
        # Arrange
        received_messages = []

        async def test_callback(body):
            received_messages.append(body)

        queue_mock = mock_channel.declare_queue.return_value
        queue_iterator = queue_mock.iterator.return_value

        # 🔥 USAR MAGICMOCK PARA message.process()
        message_mock = AsyncMock()
        message_mock.body = b'{"test": "data"}'

        # MagicMock automáticamente crea métodos mágicos
        message_mock.process = MagicMock()
        message_mock.process.__aenter__ = AsyncMock(return_value=None)
        message_mock.process.__aexit__ = AsyncMock(return_value=None)

        queue_iterator.messages.append(message_mock)

        # Act
        try:
            await asyncio.wait_for(
                rabbitmq_client_mock.setup_consumer(
                    "test", ["key"], test_callback),
                timeout=0.2
            )
        except asyncio.TimeoutError:
            pass

        # Assert
        assert len(received_messages) == 1

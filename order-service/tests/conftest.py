import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession)
from sqlalchemy.pool import StaticPool

from src.order_service.api.dependencies import get_async_session
from src.order_service.main import app
from src.order_service.models.models import Base
from src.order_service.models.events import OrderCreatedEvent
from src.order_service.models.schemas import Item
from src.order_service.core.rabbitmq import RabbitMQClient


import aio_pika
from unittest.mock import Mock, AsyncMock

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
def engine():
    """Crea el engine async para cada test"""
    return create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        poolclass=StaticPool
    )


@pytest.fixture(scope="function")
def async_session_maker(engine):
    """Factory de sesiones async"""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture(autouse=True, scope="function")
async def setup_database(engine):
    """Setup y teardown automático de la base de datos para cada test"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def async_client(async_session_maker):
    """Cliente HTTP async con override de dependencia"""

    async def override_get_async_session():
        """Crea una nueva sesión por cada request"""
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test/api/v1"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_session(async_session_maker):
    """Sesión directa para tests que necesiten acceso a BD"""
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def order():
    """Datos de ejemplo para una orden"""
    return {
        "customer_id": "customer-123",
        "customer_email": "customer@mail.com",
        "items": [
            {
                "product_id": "product-1",
                "product_name": "Wizard1",
                "quantity": 2,
                "price": 39.0
            },
            {
                "product_id": "product-2",
                "product_name": "Wizard2",
                "quantity": 1,
                "price": 45.0
            }
        ]
    }


@pytest.fixture
def mock_connection():
    """Fixture para una conexión mock de RabbitMQ"""
    mock = AsyncMock(spec=aio_pika.abc.AbstractConnection)

    return mock


@pytest.fixture
def mock_channel():
    """Fixture para un channel mock con queue.iterator() correcto"""
    mock = AsyncMock(spec=aio_pika.abc.AbstractChannel)
    mock.declare_exchange = AsyncMock()

    mock_queue = AsyncMock(spec=aio_pika.abc.AbstractQueue)
    mock_queue.bind = AsyncMock()

    class MockQueueIterator:
        def __init__(self):
            self.messages = []
            self.entered = False

        def __aiter__(self):
            return self

        async def __anext__(self):
            if not self.messages:
                raise StopAsyncIteration
            return self.messages.pop(0)

        async def __aenter__(self):
            self.entered = True
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    # Configurar queue.iterator() como método que retorna el iterador
    mock_queue.iterator = Mock(return_value=MockQueueIterator())
    mock.declare_queue = AsyncMock(return_value=mock_queue)

    return mock


@pytest.fixture
def mock_exchange():
    """Fixture para un exchange mock"""
    mock = AsyncMock(spec=aio_pika.abc.AbstractExchange)
    mock.publish = AsyncMock()
    return mock


@pytest.fixture
def rabbitmq_client_mock(mock_connection, mock_channel, mock_exchange):
    """Fixture para RabbitMQClient con mocks"""
    client = RabbitMQClient("amqp://test:test@localhost:5672/")

    # Inyectar mocks directamente
    client.connection = mock_connection
    client.channel = mock_channel
    client.exchange = mock_exchange

    return client


@pytest.fixture
def sample_order_event():
    """Fixture con evento de orden de ejemplo"""

    return OrderCreatedEvent(
        order_id="test-123",
        customer_id="cust-456",
        customer_email="test@example.com",
        items=[
            Item(
                product_id="prod-1",
                product_name="Test Product",
                quantity=2,
                price=29.99
            )
        ],
        total_amount=59.98
    )

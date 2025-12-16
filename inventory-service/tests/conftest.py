import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession)
from sqlalchemy.pool import StaticPool
from src.inventory_service.api.dependencies import get_async_session
from src.inventory_service.main import app
from src.inventory_service.models.models import Base


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
def product_id():
    return "product-123"


@pytest.fixture
def inventory():
    return {
        "product_id": "product-123",
        "forecast_quantity": 3.0
    }


@pytest.fixture
def order_created_event():
    return {
        "event_id": "evt-123",
        "event_type": "OrderCreated",
        "timestamp": "2024-01-15T10:30:00Z",
        "order_id": "test-123",
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
        ],
        "total_amount": 59.98
    }

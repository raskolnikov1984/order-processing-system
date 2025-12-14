import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from src.order_service.api.dependencies import get_async_session
from src.order_service.main import app
from src.order_service.models.models import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


async def override_get_async_session():
    database = TestingSessionLocal()
    yield database
    await database.close()


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope="function")
async def setup_database():
    """Crea todas las tablas antes de cada test y las elimina después"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_client():
    """Cliente asíncrono para hacer peticiones a la API"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test/api/v1"
    ) as client:
        yield client


@pytest.fixture
def order():
    """Datos de ejemplo para una orden"""
    return {
        "customer_id": "customer-123",
        "items": [
            {"product_id": "product-1", "quantity": 2},
            {"product_id": "product-2", "quantity": 1}
        ]
    }


@pytest.fixture
async def db_session():
    """Proporciona una sesión de BD para tests que necesiten acceso directo"""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

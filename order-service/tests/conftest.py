import pytest
from httpx import ASGITransport, AsyncClient
from src.order_service.main import app


@pytest.fixture
async def async_client():
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://avocado"
    ) as async_client:
        yield async_client

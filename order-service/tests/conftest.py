import pytest
from httpx import ASGITransport, AsyncClient
from src.order_service.main import app


@pytest.fixture
async def async_client():
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://localhost:8010/api/v1"
    ) as async_client:
        yield async_client
@pytest.fixture
def order():
    order_data = {
        "customer_id": "customer-123",
        "items": [
            {"product_id": "product-1", "quantity": 2},
            {"product_id": "product-2", "quantity": 1}
        ]
    }

    return order_data

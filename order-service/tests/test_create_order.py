# test_create_order.py
import pytest
from httpx import AsyncClient
from src.order_service.models.schemas import Order


@pytest.mark.anyio
async def test_create_order(async_client: AsyncClient, order: Order):
    response = await async_client.post('/create_order', json=order)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["message"] == "successful"
    assert response_data["order_id"] is not None

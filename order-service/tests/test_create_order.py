import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.order_service.models.models import OrderSQL
from sqlalchemy import select


@pytest.mark.anyio
async def test_create_order(
        async_client: AsyncClient, async_session: AsyncSession, order: dict):
    response = await async_client.post('/create_order', json=order)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["message"] == "successful"
    assert response_data["order_id"] is not None

    assert response_data["order_id"] is not None

    order_id = response_data["order_id"]

    result = await async_session.execute(
        select(OrderSQL).where(OrderSQL.id == order_id)
    )
    db_order = result.scalar_one_or_none()

    assert db_order is not None, "La orden no se guardó en la base de datos"
    assert db_order.customer_id == "customer-123"
    assert db_order.status == "PENDING"

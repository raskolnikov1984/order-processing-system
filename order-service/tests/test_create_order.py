import pytest
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.order_service.models.models import OrderSQL
from src.order_service.models.events import OrderCreatedEvent
from sqlalchemy import select
from decimal import Decimal


@pytest.mark.anyio
@patch("src.order_service.api.v1.endpoints.orders.publish_order_created")
async def test_create_order_success(
        mock_publish,
        async_client: AsyncClient,
        async_session: AsyncSession, order: dict):

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
    assert db_order.customer_email == "customer@mail.com"
    assert db_order.total_amount == Decimal("123.00")
    assert db_order.status == "PENDING"

    mock_publish.assert_called_once()

    event_passed = mock_publish.call_args[0][0]  # El primer argumento
    assert isinstance(event_passed, OrderCreatedEvent)


@pytest.mark.anyio
@patch("src.order_service.api.v1.endpoints.orders.publish_order_created")
async def test_get_order_status(
        mock_publish, async_client: AsyncClient, order: dict):
    response = await async_client.post('/create_order', json=order)

    mock_publish.assert_called_once()

    assert response.status_code == 201
    order_id = response.json()["order_id"]

    response = await async_client.get(f'/order_status/{order_id}')
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["order_status"] == "PENDING"


@pytest.mark.anyio
async def test_get_order_status_order_not_found(async_client: AsyncClient):
    response = await async_client.get('/order_status/10000')
    response_data = response.json()
    assert response.status_code == 404
    assert response_data["detail"] == "Order Id: 10000 Not Found"

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.order_service.models.database import (
    db_create_order,
    db_get_order_status
)
from src.order_service.models.schemas import Order
from decimal import Decimal


@pytest.mark.anyio
async def test_db_create_order(order: Order, async_session: AsyncSession):
    order_pydantic = Order(**order)
    new_order = await db_create_order(order_pydantic, async_session)

    assert new_order.id == 1
    assert new_order.customer_id == "customer-123"
    assert new_order.total_amount == Decimal("123.00")
    assert new_order.status == "PENDING"


@pytest.mark.anyio
async def test_db_get_order_status(order: Order, async_session: AsyncSession):
    order_pydantic = Order(**order)
    new_order = await db_create_order(order_pydantic, async_session)
    order_status = await db_get_order_status(new_order.id, async_session)

    assert order_status == "PENDING"

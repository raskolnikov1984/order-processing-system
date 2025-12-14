import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.order_service.models.database import db_create_order
from src.order_service.models.schemas import Order


@pytest.mark.anyio
async def test_db_create_order(order: Order, async_session: AsyncSession):
    order_pydantic = Order(**order)
    new_order = await db_create_order(order_pydantic, async_session)

    assert new_order.id == 1
    assert new_order.customer_id == "customer-123"
    assert new_order.total_amount is None
    assert new_order.status == "PENDING"

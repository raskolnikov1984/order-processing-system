import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.order_service.models.database import (
    db_create_order,
    db_get_order_status
)
from src.order_service.models.models import OrderItemSQL
from src.order_service.models.schemas import Order
from sqlalchemy import select
from decimal import Decimal


@pytest.mark.anyio
async def test_db_create_order(order: Order, async_session: AsyncSession):
    order_pydantic = Order(**order)
    new_order = await db_create_order(order_pydantic, async_session)

    assert new_order.id == 1
    assert new_order.customer_id == "customer-123"
    assert new_order.total_amount == Decimal("123.00")
    assert new_order.status == "PENDING"

    result = await async_session.execute(
        select(OrderItemSQL).where(OrderItemSQL.order_id == new_order.id)
    )

    order_items = result.scalars().all()

    assert len(
        order_items
    ) == 2, f"Se esperaban 2 ítems, pero se crearon {len(order_items)}"

    order_items.sort(key=lambda x: x.product_id)

    assert order_items[0].product_id == "product-1"
    assert order_items[0].product_name == "Wizard1"
    assert order_items[0].price == Decimal('39.00')
    assert order_items[0].quantity == 2
    assert order_items[0].order_id == new_order.id

    assert order_items[1].product_id == "product-2"
    assert order_items[1].product_name == "Wizard2"
    assert order_items[1].price == Decimal('45.00')
    assert order_items[1].quantity == 1
    assert order_items[1].order_id == new_order.id


@pytest.mark.anyio
async def test_db_get_order_status(order: Order, async_session: AsyncSession):
    order_pydantic = Order(**order)
    new_order = await db_create_order(order_pydantic, async_session)
    order_status = await db_get_order_status(new_order.id, async_session)

    assert order_status == "PENDING"

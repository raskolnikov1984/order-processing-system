import pytest
from src.inventory_service.models.models import InventorySQL
from src.inventory_service.models.database import (
    db_get_inventory_by_product
)


@pytest.mark.anyio
async def test_db_get_inventory_by_product(
        product_id: str, async_session, inventory: dict):

    new_inventory = InventorySQL(
        **inventory
    )

    async_session.add(new_inventory)
    await async_session.commit()
    await async_session.refresh(new_inventory)

    result = await db_get_inventory_by_product(
        product_id, async_session)

    assert result.forecast_quantity == 3

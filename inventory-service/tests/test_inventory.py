import pytest
from httpx import AsyncClient
from src.inventory_service.models.database import db_create_inventory


@pytest.mark.anyio
async def test_get_inventory_by_product(
        async_client: AsyncClient, async_session, inventory: dict):

    new_inventory = await db_create_inventory(inventory, async_session)

    response = await async_client.get(
        f"/inventory/{new_inventory.product_id}")
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["forecast_quantity"] == 3

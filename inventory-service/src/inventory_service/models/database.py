from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import InventorySQL


async def db_get_inventory_by_product(product_id: str, session: Session):

    forecast_quantity = select(InventorySQL).where(
        InventorySQL.product_id == product_id)

    result = await session.execute(forecast_quantity)

    inventory = result.scalar_one_or_none()

    return inventory


async def db_create_inventory(inventory: dict, session: Session):
    new_inventory = InventorySQL(
        **inventory
    )

    session.add(new_inventory)
    await session.commit()
    await session.refresh(new_inventory)

    return new_inventory


def update_order_status():
    pass

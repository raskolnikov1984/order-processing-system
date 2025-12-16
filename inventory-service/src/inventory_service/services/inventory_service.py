from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.inventory_service.models.database import InventorySQL
from src.inventory_service.models.events import OrderCreatedEvent
from src.inventory_service.logger import logger


class InventoryService:
    """Servicio para operaciones de inventario"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def reserve_inventory(
            self, event: OrderCreatedEvent) -> tuple[bool, str | None]:
        """
        Intenta reservar inventario para una orden.

        Returns:
            tuple[bool, str | None]: (éxito, mensaje_error_si_falla)
        """
        try:
            for item in event.items:
                # Buscar producto en DB
                stmt = select(InventorySQL).where(
                    InventorySQL.product_id == item.product_id
                )
                result = await self.db.execute(stmt)
                inventory = result.scalar_one_or_none()

                if not inventory:
                    logger.error(f"Producto no encontrado: {item.product_id}")
                    return False, f"Product {item.product_id} not found"

                if inventory.forecast_quantity < item.quantity:
                    logger.warning(
                        f"Stock insuficiente para {item.product_id}: "
                        f"disponible {inventory.forecast_quantity}, "
                        f"requerido {item.quantity}"
                    )
                    return False, f"Insufficient stock for {item.product_id}"

                # Reservar (decrementar forecast)
                inventory.forecast_quantity -= item.quantity
                logger.info(
                    f"Reservado {item.quantity} unidades de {item.product_id}"
                )

            # Confirmar cambios
            await self.db.commit()
            return True, None

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error reservando inventario: {e}", exc_info=True)
            return False, f"Database error: {str(e)}"

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from src.order_service.models.database import OrderSQL
from src.order_service.logger import logger


class OrderService:
    """Servicio para gestionar órdenes"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def confirm_order(self, order_id: str) -> bool:
        """Cambia estado a CONFIRMED cuando inventario está reservado"""
        stmt = (
            update(OrderSQL)
            .where(OrderSQL.id == order_id)
            .values(status="CONFIRMED")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()

        if result.rowcount > 0:
            logger.info(f"Orden {order_id} CONFIRMADA")
            return True

        logger.warning(f"Orden {order_id} no encontrada para confirmar")
        return False

    async def cancel_order(self, order_id: int, reason: str) -> bool:
        """Cambia estado a CANCELLED cuando inventario no está disponible"""
        stmt = (
            update(OrderSQL)
            .where(OrderSQL.id == int(order_id))
            .values(
                status="CANCELLED",
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()

        if result.rowcount > 0:
            logger.error(f"Orden {order_id} CANCELADA: {reason}")
            return True

        logger.warning(f"Orden {order_id} no encontrada para cancelar")
        return False

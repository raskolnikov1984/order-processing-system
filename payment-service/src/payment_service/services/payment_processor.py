import asyncio
import random
from sqlalchemy.ext.asyncio import AsyncSession
from src.payment_service.models.schemas import Payment
from typing import Tuple
from src.payment_service.models.database import db_create_payment
from src.payment_service.logger import logger


class PaymentProcessor:
    """
    Simula gateway de pago con 80% éxito y lógica de retry.
    """

    def __init__(self, db_session: AsyncSession):
        self.success_rate = 0.8
        self.db_session = db_session

    async def process(
        self, order_id: str,
        amount: float,
        retry_count: int = 0
    ) -> Tuple[bool, str | None, str | None]:
        """
        Simula procesamiento de pago.

        Returns:
            tuple[bool, str | None, str | None]: (
            éxito, payment_id, error_message)
        """
        logger.info(
            f"Procesando pago para orden {order_id}: "
            f"${amount} (retry {retry_count})"
        )

        await asyncio.sleep(0.1)

        # 80% éxito
        if random.random() < self.success_rate:
            payment_id = f"pay_{order_id}_{random.randint(1000, 9999)}"

            payment = Payment(
                payment_id=payment_id,
                order_id=order_id,
                amount=amount
            )

            payment_created = await db_create_payment(payment, self.db_session)

            logger.info(f"Pago creado en DB con ID: {payment_created.id}")
            logger.info(f"Pago exitoso: {payment_id}")

            return True, payment_id, None

        # 20% fallo
        error_messages = [
            "Tarjeta rechazada",
            "Fondos insuficientes",
            "Gateway timeout",
            "Autenticación 3D fallida"
        ]

        error = random.choice(error_messages)
        logger.error(f"❌ Pago fallido: {error}")

        return False, None, error

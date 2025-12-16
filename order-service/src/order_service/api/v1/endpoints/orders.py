import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.order_service.api.dependencies import get_async_session
from src.order_service.models.schemas import Order, Item
from src.order_service.models.events import OrderCreatedEvent
from src.order_service.models.database import (
    db_create_order,
    db_get_order_status
)
from src.order_service.events.publishers import publish_order_created
from src.order_service.logger import logger


router = APIRouter()


@router.post("/create_order", status_code=status.HTTP_201_CREATED)
async def create_order(
        order: Order, session: Session = Depends(get_async_session)):
    """
    Crear una nueva orden
    """

    try:
        new_order = await db_create_order(order, session)

        event_items = [
            Item(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                price=item.price
            )
            for item in order.items
        ]

        # Crear evento
        event = OrderCreatedEvent(
            order_id=str(new_order.id),
            customer_id=order.customer_id,
            customer_email=order.customer_email,
            items=event_items,
            total_amount=order.total_amount
        )

        # Publicar evento async (no bloquea la respuesta)
        # Usar asyncio.create_task para no esperar
        asyncio.create_task(publish_order_created(event))

        return {
            "message": "successful",
            "order_id": new_order.id,
            "status": "PENDING"
        }
    except Exception as e:
        logger.error(f"Error al crear orden: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo crear la orden. Por favor, intente nuevamente."
        )


@router.get("/order_status/{order_id}", status_code=status.HTTP_200_OK)
async def order_status(
        order_id: int, session: Session = Depends(get_async_session)):

    try:
        order_status = await db_get_order_status(order_id, session)

        if order_status:
            return {
                "message": "successful",
                "order_status": order_status
            }
    except Exception as e:
        logger.error(f"Error al obtener orden status: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No se pudo encontrar la orden."
                "Por favor, intente nuevamente.")
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Order Id: {order_id} Not Found")

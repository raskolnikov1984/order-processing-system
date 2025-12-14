from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.order_service.api.dependencies import get_async_session
from src.order_service.models.schemas import Order
from src.order_service.models.database import (
    db_create_order)

router = APIRouter()


@router.post("/create_order", status_code=status.HTTP_201_CREATED)
async def create_order(
        order: Order, session: Session = Depends(get_async_session)):
    """
    Crear una nueva orden
    """

    try:
        new_order = await db_create_order(order, session)

        return {
            "message": "successful",
            "order_id": new_order.id
        }
    except Exception as e:
        print(f"Error al crear orden: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo crear la orden. Por favor, intente nuevamente."
        )

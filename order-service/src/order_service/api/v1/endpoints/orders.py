from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.order_service.api.dependencies import get_async_session
from src.order_service.models.schemas import Order
from src.order_service.models.database import (
    db_create_order)

router = APIRouter()


@router.post("/create_order", status_code=201)
async def create_order(
        order: Order, session: Session = Depends(get_async_session)):
    """
    Crear una nueva orden
    """

    new_order = await db_create_order(order, session)

    return {
        "message": "successful",
        "order_id": new_order.id
    }

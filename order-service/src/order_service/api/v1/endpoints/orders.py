from fastapi import APIRouter
from src.order_service.models.schemas import Order


router = APIRouter()



@router.post("/create_order", status_code=201)
async def create_order(order: Order):
    """
    Crear una nueva orden
    """

    return {"message": "successful"}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.inventory_service.api.dependencies import get_async_session
from src.inventory_service.models.database import (
    db_get_inventory_by_product
)
from src.inventory_service.models.schemas import InventoryResponse

router = APIRouter()


@router.get(
    "/inventory/{product_id}",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK)
async def inventory(
        product_id: str, session: Session = Depends(get_async_session)):

    try:
        result = await db_get_inventory_by_product(product_id, session)
        if result:
            return InventoryResponse(
                message="successful",
                forecast_quantity=result.forecast_quantity
            )
    except Exception as e:
        print(f"Error al crear orden: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al Obetener el Inventario"
        )
    return InventoryResponse(
            message="Not Found",
            forecast_quantity=0
        )

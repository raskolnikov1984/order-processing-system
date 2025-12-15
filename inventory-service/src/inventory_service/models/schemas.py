from pydantic import BaseModel


class Inventory(BaseModel):
    id: int
    product_id: str
    forecast_quantity: float


class InventoryResponse(BaseModel):
    message: str
    forecast_quantity: float

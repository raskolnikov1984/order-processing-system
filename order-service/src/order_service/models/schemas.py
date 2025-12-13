from pydantic import BaseModel
from typing import List


class Item(BaseModel):
    product_id: str
    quantity: float


class Order(BaseModel):
    customer_id: str
    items: List[Item]

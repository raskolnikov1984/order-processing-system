from pydantic import BaseModel
from typing import List


class Item(BaseModel):
    product_id: str
    product_name: str
    quantity: float
    price: float


class Order(BaseModel):
    customer_id: str
    customer_email: str
    items: List[Item]
    total_amount: float

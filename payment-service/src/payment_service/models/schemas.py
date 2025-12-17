from pydantic import BaseModel


class Payment(BaseModel):
    payment_id: str
    order_id: str
    amount: float

from sqlalchemy.orm import Session
from .schemas import Order
from .models import OrderSQL


async def db_create_order(order: Order, session: Session) -> OrderSQL:

    new_order = OrderSQL(
        customer_id=order.customer_id
    )

    session.add(new_order)

    await session.commit()
    await session.refresh(new_order)

    return new_order

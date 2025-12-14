from sqlalchemy.orm import Session
from .schemas import Order
from .models import OrderSQL, OrderItemSQL
import datetime


async def db_create_order(order: Order, session: Session) -> OrderSQL:

    new_order = OrderSQL(
        customer_id=order.customer_id,
        created_at=datetime.datetime.now(datetime.UTC)
    )

    session.add(new_order)
    await session.flush()

    for item in order.items:
        order_item = OrderItemSQL(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=int(item.quantity),
            created_at=datetime.datetime.now(datetime.UTC)
        )
        session.add(order_item)

    await session.commit()
    await session.refresh(new_order)

    return new_order

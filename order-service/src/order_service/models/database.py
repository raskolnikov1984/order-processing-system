from sqlalchemy.orm import Session
from .schemas import Order
from .models import OrderSQL, OrderItemSQL
import datetime


async def db_create_order(order: Order, session: Session) -> OrderSQL:

    total_amount = sum(
        item.price * item.quantity
        for item in order.items if item.price and item.quantity
    )

    new_order = OrderSQL(
        customer_id=order.customer_id,
        customer_email=order.customer_email,
        created_at=datetime.datetime.now(datetime.UTC),
        total_amount=total_amount
    )

    session.add(new_order)
    await session.flush()

    for item in order.items:
        order_item = OrderItemSQL(
            order_id=new_order.id,
            product_id=item.product_id,
            product_name=item.product_name,
            quantity=int(item.quantity),
            price=item.price,
            created_at=datetime.datetime.now(datetime.UTC)
        )
        session.add(order_item)

    await session.commit()
    await session.refresh(new_order)

    return new_order


async def db_get_order_status(order_id: int, session: Session) -> str:
    order = await session.get(OrderSQL, order_id)

    if order:
        return order.status
    return ""


def update_order_status():
    pass

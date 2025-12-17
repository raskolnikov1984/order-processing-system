from sqlalchemy.orm import Session
from .schemas import Payment
from .models import PaymentSQL
import datetime


async def db_create_payment(payment: Payment, session: Session) -> PaymentSQL:
    new_payment = PaymentSQL(
        payment_id=payment.payment_id,
        order_id=payment.order_id,
        amount=payment.amount,
        created_at=datetime.datetime.now(datetime.UTC),
    )

    session.add(new_payment)

    await session.commit()
    await session.refresh(new_payment)

    return new_payment

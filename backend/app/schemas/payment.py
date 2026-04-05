from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentBase(BaseModel):
    booking_id: int
    amount: Decimal
    payment_method: str
    comment: str | None = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: Decimal | None = None
    payment_method: str | None = None
    comment: str | None = None


class PaymentRead(PaymentBase):
    id: int
    paid_at: datetime

    model_config = ConfigDict(from_attributes=True)

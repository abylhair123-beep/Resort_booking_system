from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.booking import BookingStatus


class BookingBase(BaseModel):
    client_id: int
    room_id: int
    check_in: date
    check_out: date
    total_price: Decimal
    status: BookingStatus = BookingStatus.reserved
    is_paid: bool = False
    guest_count: int
    notes: str | None = None

    @field_validator("check_out")
    @classmethod
    def validate_dates(cls, value: date, info):
        check_in = info.data.get("check_in")
        if check_in and value <= check_in:
            raise ValueError("check_out must be later than check_in")
        return value


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    client_id: int | None = None
    room_id: int | None = None
    check_in: date | None = None
    check_out: date | None = None
    total_price: Decimal | None = None
    status: BookingStatus | None = None
    is_paid: bool | None = None
    guest_count: int | None = None
    notes: str | None = None


class BookingRead(BookingBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MarkPaidRequest(BaseModel):
    amount: Decimal
    payment_method: str
    comment: str | None = None


class OccupancyEntry(BaseModel):
    date: date
    room_id: int
    room_number: str
    is_occupied: bool
    booking_id: int | None = None

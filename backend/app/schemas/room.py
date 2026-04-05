from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.room import RoomStatus


class RoomBase(BaseModel):
    number: str
    category: str
    price_per_night: Decimal
    status: RoomStatus = RoomStatus.free
    capacity: int
    notes: str | None = None


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    number: str | None = None
    category: str | None = None
    price_per_night: Decimal | None = None
    status: RoomStatus | None = None
    capacity: int | None = None
    notes: str | None = None


class RoomRead(RoomBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

import enum

from sqlalchemy import Enum, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RoomStatus(str, enum.Enum):
    free = "free"
    occupied = "occupied"
    cleaning = "cleaning"


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    price_per_night: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[RoomStatus] = mapped_column(Enum(RoomStatus), default=RoomStatus.free, nullable=False)
    capacity: Mapped[int] = mapped_column(nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    bookings = relationship("Booking", back_populates="room")

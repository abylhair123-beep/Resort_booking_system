from datetime import date, timedelta

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models import Booking, BookingStatus, Room

ACTIVE_BOOKING_STATUSES = [BookingStatus.reserved, BookingStatus.checked_in]


def validate_booking_overlap(
    db: Session,
    room_id: int,
    check_in: date,
    check_out: date,
    exclude_booking_id: int | None = None,
) -> None:
    filters = [
        Booking.room_id == room_id,
        Booking.status.in_(ACTIVE_BOOKING_STATUSES),
        Booking.check_in < check_out,
        Booking.check_out > check_in,
    ]
    if exclude_booking_id is not None:
        filters.append(Booking.id != exclude_booking_id)

    statement = select(Booking).where(and_(*filters))
    existing = db.execute(statement).scalar_one_or_none()
    if existing:
        raise ValueError("Room already has an active booking in selected dates")


def build_occupancy_calendar(db: Session, date_from: date, date_to: date) -> list[dict]:
    rooms = db.execute(select(Room).order_by(Room.number)).scalars().all()
    bookings = db.execute(
        select(Booking).where(
            Booking.status.in_(ACTIVE_BOOKING_STATUSES),
            or_(
                and_(Booking.check_in >= date_from, Booking.check_in < date_to),
                and_(Booking.check_out > date_from, Booking.check_out <= date_to),
                and_(Booking.check_in <= date_from, Booking.check_out >= date_to),
            ),
        )
    ).scalars().all()

    occupancy_index: dict[tuple[date, int], int] = {}
    for booking in bookings:
        current = booking.check_in
        while current < booking.check_out:
            if date_from <= current <= date_to:
                occupancy_index[(current, booking.room_id)] = booking.id
            current += timedelta(days=1)

    rows: list[dict] = []
    current = date_from
    while current <= date_to:
        for room in rooms:
            booking_id = occupancy_index.get((current, room.id))
            rows.append(
                {
                    "date": current,
                    "room_id": room.id,
                    "room_number": room.number,
                    "is_occupied": booking_id is not None,
                    "booking_id": booking_id,
                }
            )
        current += timedelta(days=1)
    return rows

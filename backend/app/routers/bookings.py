from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Booking, BookingStatus, Client, Payment, Room
from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate, MarkPaidRequest, OccupancyEntry
from app.services.booking_service import build_occupancy_calendar, validate_booking_overlap

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/", response_model=list[BookingRead])
def list_bookings(
    status_filter: BookingStatus | None = Query(default=None, alias="status"),
    client_id: int | None = None,
    room_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Booking).order_by(Booking.created_at.desc())
    filters = []
    if status_filter:
        filters.append(Booking.status == status_filter)
    if client_id:
        filters.append(Booking.client_id == client_id)
    if room_id:
        filters.append(Booking.room_id == room_id)
    if date_from:
        filters.append(Booking.check_out > date_from)
    if date_to:
        filters.append(Booking.check_in < date_to)

    if filters:
        statement = statement.where(and_(*filters))

    return db.execute(statement).scalars().all()


@router.get("/{booking_id}", response_model=BookingRead)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking


@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    if not db.get(Client, payload.client_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    room = db.get(Room, payload.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    try:
        validate_booking_overlap(db, payload.room_id, payload.check_in, payload.check_out)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    booking = Booking(**payload.model_dump())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.put("/{booking_id}", response_model=BookingRead)
def update_booking(booking_id: int, payload: BookingUpdate, db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    data = payload.model_dump(exclude_unset=True)
    merged_check_in = data.get("check_in", booking.check_in)
    merged_check_out = data.get("check_out", booking.check_out)
    merged_room_id = data.get("room_id", booking.room_id)

    if merged_check_out <= merged_check_in:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="check_out must be later than check_in")

    if "client_id" in data and not db.get(Client, data["client_id"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    if "room_id" in data and not db.get(Room, data["room_id"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    try:
        validate_booking_overlap(db, merged_room_id, merged_check_in, merged_check_out, exclude_booking_id=booking.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    for field, value in data.items():
        setattr(booking, field, value)

    db.commit()
    db.refresh(booking)
    return booking


@router.post("/{booking_id}/mark-paid", response_model=BookingRead)
def mark_booking_paid(booking_id: int, payload: MarkPaidRequest, db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    payment = Payment(
        booking_id=booking.id,
        amount=payload.amount,
        payment_method=payload.payment_method,
        comment=payload.comment,
    )
    booking.is_paid = True

    db.add(payment)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/occupancy/calendar", response_model=list[OccupancyEntry])
def occupancy_calendar(date_from: date, date_to: date, db: Session = Depends(get_db)):
    if date_to < date_from:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="date_to must be >= date_from")
    return build_occupancy_calendar(db, date_from, date_to)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    db.delete(booking)
    db.commit()

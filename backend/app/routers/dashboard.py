from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Booking, BookingStatus, Client, Room
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    clients_total = db.scalar(select(func.count()).select_from(Client)) or 0
    rooms_total = db.scalar(select(func.count()).select_from(Room)) or 0
    active_bookings_total = (
        db.scalar(
            select(func.count()).select_from(Booking).where(Booking.status.in_([BookingStatus.reserved, BookingStatus.checked_in]))
        )
        or 0
    )
    unpaid_bookings_total = db.scalar(select(func.count()).select_from(Booking).where(Booking.is_paid.is_(False))) or 0

    occupancy_rate_percent = (active_bookings_total / rooms_total * 100) if rooms_total else 0

    return DashboardStats(
        clients_total=clients_total,
        rooms_total=rooms_total,
        active_bookings_total=active_bookings_total,
        unpaid_bookings_total=unpaid_bookings_total,
        occupancy_rate_percent=round(occupancy_rate_percent, 2),
    )

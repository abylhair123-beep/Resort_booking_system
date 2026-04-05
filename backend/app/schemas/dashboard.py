from pydantic import BaseModel


class DashboardStats(BaseModel):
    clients_total: int
    rooms_total: int
    active_bookings_total: int
    unpaid_bookings_total: int
    occupancy_rate_percent: float

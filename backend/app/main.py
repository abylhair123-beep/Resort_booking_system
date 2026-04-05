from fastapi import FastAPI

from app.core.config import get_settings
from app.core.database import engine
from app.models import Base
from app.routers import bookings, clients, dashboard, payments, rooms

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(dashboard.router)
app.include_router(clients.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
app.include_router(payments.router)

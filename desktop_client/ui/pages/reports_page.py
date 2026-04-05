from PySide6.QtWidgets import (
    QDateEdit,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from desktop_client.api.client import ApiError


class ReportsPage(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client

        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.load_button = QPushButton("Load occupancy")
        self.load_button.clicked.connect(self.refresh)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Date", "Room ID", "Room", "Occupied", "Booking ID"])

        filters = QHBoxLayout()
        filters.addWidget(self.from_date)
        filters.addWidget(self.to_date)
        filters.addWidget(self.load_button)

        layout = QVBoxLayout(self)
        layout.addLayout(filters)
        layout.addWidget(self.table)

    def refresh(self):
        params = {
            "date_from": self.from_date.date().toString("yyyy-MM-dd"),
            "date_to": self.to_date.date().toString("yyyy-MM-dd"),
        }
        try:
            rows = self.api_client.get("/bookings/occupancy/calendar", params=params)
            self.table.setRowCount(len(rows))
            for row, entry in enumerate(rows):
                self.table.setItem(row, 0, QTableWidgetItem(entry["date"]))
                self.table.setItem(row, 1, QTableWidgetItem(str(entry["room_id"])))
                self.table.setItem(row, 2, QTableWidgetItem(entry["room_number"]))
                self.table.setItem(row, 3, QTableWidgetItem("Yes" if entry["is_occupied"] else "No"))
                self.table.setItem(row, 4, QTableWidgetItem(str(entry["booking_id"] or "")))
        except ApiError as exc:
            QMessageBox.critical(self, "Error", str(exc))

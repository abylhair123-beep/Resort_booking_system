from PySide6.QtWidgets import (
    QComboBox,
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
from desktop_client.ui.widgets.forms import BookingFormDialog, MarkPaidDialog


class BookingsPage(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client

        self.status_filter = QComboBox()
        self.status_filter.addItems(["", "reserved", "checked_in", "checked_out", "cancelled"])

        self.client_filter = QComboBox()
        self.room_filter = QComboBox()

        self.from_filter = QDateEdit()
        self.from_filter.setCalendarPopup(True)
        self.to_filter = QDateEdit()
        self.to_filter.setCalendarPopup(True)

        self.apply_filter_button = QPushButton("Apply filters")
        self.apply_filter_button.clicked.connect(self.refresh)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Client", "Room", "Check-in", "Check-out", "Status", "Paid", "Guests", "Total"]
        )

        self.add_button = QPushButton("Add booking")
        self.edit_button = QPushButton("Edit booking")
        self.delete_button = QPushButton("Delete booking")
        self.mark_paid_button = QPushButton("Mark as paid")

        self.add_button.clicked.connect(self.add_booking)
        self.edit_button.clicked.connect(self.edit_booking)
        self.delete_button.clicked.connect(self.delete_booking)
        self.mark_paid_button.clicked.connect(self.mark_paid)

        filters = QHBoxLayout()
        filters.addWidget(self.status_filter)
        filters.addWidget(self.client_filter)
        filters.addWidget(self.room_filter)
        filters.addWidget(self.from_filter)
        filters.addWidget(self.to_filter)
        filters.addWidget(self.apply_filter_button)

        actions = QHBoxLayout()
        actions.addWidget(self.add_button)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addWidget(self.mark_paid_button)
        actions.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(filters)
        layout.addLayout(actions)
        layout.addWidget(self.table)

    def _load_filter_data(self):
        clients = self.api_client.get("/clients/")
        rooms = self.api_client.get("/rooms/")

        self.client_filter.clear()
        self.client_filter.addItem("All clients", None)
        for item in clients:
            self.client_filter.addItem(item["full_name"], item["id"])

        self.room_filter.clear()
        self.room_filter.addItem("All rooms", None)
        for item in rooms:
            self.room_filter.addItem(f"Room {item['number']}", item["id"])

    def refresh(self):
        try:
            self._load_filter_data()
            params = {}
            if self.status_filter.currentText():
                params["status"] = self.status_filter.currentText()
            if self.client_filter.currentData() is not None:
                params["client_id"] = self.client_filter.currentData()
            if self.room_filter.currentData() is not None:
                params["room_id"] = self.room_filter.currentData()
            params["date_from"] = self.from_filter.date().toString("yyyy-MM-dd")
            params["date_to"] = self.to_filter.date().toString("yyyy-MM-dd")

            bookings = self.api_client.get("/bookings/", params=params)
            self.table.setRowCount(len(bookings))
            for row, booking in enumerate(bookings):
                self.table.setItem(row, 0, QTableWidgetItem(str(booking["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(booking["client_id"])))
                self.table.setItem(row, 2, QTableWidgetItem(str(booking["room_id"])))
                self.table.setItem(row, 3, QTableWidgetItem(booking["check_in"]))
                self.table.setItem(row, 4, QTableWidgetItem(booking["check_out"]))
                self.table.setItem(row, 5, QTableWidgetItem(booking["status"]))
                self.table.setItem(row, 6, QTableWidgetItem("Yes" if booking["is_paid"] else "No"))
                self.table.setItem(row, 7, QTableWidgetItem(str(booking["guest_count"])))
                self.table.setItem(row, 8, QTableWidgetItem(str(booking["total_price"])))
        except ApiError as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _selected_booking_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def _list_form_data(self):
        return self.api_client.get("/clients/"), self.api_client.get("/rooms/")

    def add_booking(self):
        clients, rooms = self._list_form_data()
        dialog = BookingFormDialog(clients, rooms, self)
        if dialog.exec():
            try:
                self.api_client.post("/bookings/", dialog.payload())
                self.refresh()
                QMessageBox.information(self, "Saved", "Booking created.")
            except ApiError as exc:
                QMessageBox.critical(self, "Error", str(exc))

    def edit_booking(self):
        booking_id = self._selected_booking_id()
        if not booking_id:
            QMessageBox.warning(self, "Selection", "Select a booking first.")
            return
        clients, rooms = self._list_form_data()
        initial = self.api_client.get(f"/bookings/{booking_id}")
        dialog = BookingFormDialog(clients, rooms, self, initial=initial)
        if dialog.exec():
            try:
                self.api_client.put(f"/bookings/{booking_id}", dialog.payload())
                self.refresh()
                QMessageBox.information(self, "Saved", "Booking updated.")
            except ApiError as exc:
                QMessageBox.critical(self, "Error", str(exc))

    def delete_booking(self):
        booking_id = self._selected_booking_id()
        if not booking_id:
            QMessageBox.warning(self, "Selection", "Select a booking first.")
            return
        try:
            self.api_client.delete(f"/bookings/{booking_id}")
            self.refresh()
            QMessageBox.information(self, "Deleted", "Booking deleted.")
        except ApiError as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def mark_paid(self):
        booking_id = self._selected_booking_id()
        if not booking_id:
            QMessageBox.warning(self, "Selection", "Select a booking first.")
            return

        dialog = MarkPaidDialog(self)
        if dialog.exec():
            try:
                self.api_client.post(f"/bookings/{booking_id}/mark-paid", dialog.payload())
                self.refresh()
                QMessageBox.information(self, "Saved", "Booking marked as paid.")
            except ApiError as exc:
                QMessageBox.critical(self, "Error", str(exc))

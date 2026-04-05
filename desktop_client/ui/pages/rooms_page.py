from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from desktop_client.api.client import ApiError
from desktop_client.ui.widgets.forms import RoomFormDialog


class RoomsPage(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Number", "Category", "Price", "Status", "Capacity"])

        self.add_button = QPushButton("Add room")
        self.edit_button = QPushButton("Edit room")
        self.delete_button = QPushButton("Delete room")

        self.add_button.clicked.connect(self.add_room)
        self.edit_button.clicked.connect(self.edit_room)
        self.delete_button.clicked.connect(self.delete_room)

        actions = QHBoxLayout()
        actions.addWidget(self.add_button)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(actions)
        layout.addWidget(self.table)

    def refresh(self):
        rooms = self.api_client.get("/rooms/")
        self.table.setRowCount(len(rooms))
        for row, room in enumerate(rooms):
            self.table.setItem(row, 0, QTableWidgetItem(str(room["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(room["number"]))
            self.table.setItem(row, 2, QTableWidgetItem(room["category"]))
            self.table.setItem(row, 3, QTableWidgetItem(str(room["price_per_night"])))
            self.table.setItem(row, 4, QTableWidgetItem(room["status"]))
            self.table.setItem(row, 5, QTableWidgetItem(str(room["capacity"])))

    def _selected_room_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def add_room(self):
        dialog = RoomFormDialog(self)
        if dialog.exec():
            try:
                self.api_client.post("/rooms/", dialog.payload())
                self.refresh()
                QMessageBox.information(self, "Saved", "Room created.")
            except ApiError as exc:
                QMessageBox.critical(self, "Error", str(exc))

    def edit_room(self):
        room_id = self._selected_room_id()
        if not room_id:
            QMessageBox.warning(self, "Selection", "Select a room first.")
            return

        initial = self.api_client.get(f"/rooms/{room_id}")
        dialog = RoomFormDialog(self, initial=initial)
        if dialog.exec():
            try:
                self.api_client.put(f"/rooms/{room_id}", dialog.payload())
                self.refresh()
                QMessageBox.information(self, "Saved", "Room updated.")
            except ApiError as exc:
                QMessageBox.critical(self, "Error", str(exc))

    def delete_room(self):
        room_id = self._selected_room_id()
        if not room_id:
            QMessageBox.warning(self, "Selection", "Select a room first.")
            return

        try:
            self.api_client.delete(f"/rooms/{room_id}")
            self.refresh()
            QMessageBox.information(self, "Deleted", "Room deleted.")
        except ApiError as exc:
            QMessageBox.critical(self, "Error", str(exc))

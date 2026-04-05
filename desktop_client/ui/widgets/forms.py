from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
)


class ClientFormDialog(QDialog):
    def __init__(self, parent=None, initial: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Client")
        self.full_name = QLineEdit(initial.get("full_name", "") if initial else "")
        self.phone = QLineEdit(initial.get("phone", "") if initial else "")
        self.email = QLineEdit(initial.get("email", "") if initial else "")
        self.notes = QPlainTextEdit(initial.get("notes", "") if initial else "")

        layout = QFormLayout(self)
        layout.addRow("Full name", self.full_name)
        layout.addRow("Phone", self.phone)
        layout.addRow("Email", self.email)
        layout.addRow("Notes", self.notes)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def payload(self) -> dict:
        return {
            "full_name": self.full_name.text().strip(),
            "phone": self.phone.text().strip(),
            "email": self.email.text().strip() or None,
            "notes": self.notes.toPlainText().strip() or None,
        }


class RoomFormDialog(QDialog):
    def __init__(self, parent=None, initial: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Room")
        self.number = QLineEdit(initial.get("number", "") if initial else "")
        self.category = QLineEdit(initial.get("category", "") if initial else "")

        self.price_per_night = QDoubleSpinBox()
        self.price_per_night.setMaximum(100000)
        self.price_per_night.setDecimals(2)
        self.price_per_night.setValue(float(initial.get("price_per_night", 0)) if initial else 0)

        self.status = QComboBox()
        self.status.addItems(["free", "occupied", "cleaning"])
        if initial:
            self.status.setCurrentText(initial.get("status", "free"))

        self.capacity = QSpinBox()
        self.capacity.setRange(1, 20)
        self.capacity.setValue(initial.get("capacity", 1) if initial else 1)

        self.notes = QPlainTextEdit(initial.get("notes", "") if initial else "")

        layout = QFormLayout(self)
        layout.addRow("Room number", self.number)
        layout.addRow("Category", self.category)
        layout.addRow("Price per night", self.price_per_night)
        layout.addRow("Status", self.status)
        layout.addRow("Capacity", self.capacity)
        layout.addRow("Notes", self.notes)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def payload(self) -> dict:
        return {
            "number": self.number.text().strip(),
            "category": self.category.text().strip(),
            "price_per_night": self.price_per_night.value(),
            "status": self.status.currentText(),
            "capacity": self.capacity.value(),
            "notes": self.notes.toPlainText().strip() or None,
        }


class BookingFormDialog(QDialog):
    def __init__(self, clients: list[dict], rooms: list[dict], parent=None, initial: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Booking")
        self.clients = clients
        self.rooms = rooms

        self.client = QComboBox()
        for item in clients:
            self.client.addItem(item["full_name"], item["id"])

        self.room = QComboBox()
        for item in rooms:
            self.room.addItem(f"Room {item['number']} ({item['category']})", item["id"])

        self.check_in = QDateEdit()
        self.check_in.setCalendarPopup(True)
        self.check_out = QDateEdit()
        self.check_out.setCalendarPopup(True)

        self.total_price = QDoubleSpinBox()
        self.total_price.setMaximum(1000000)
        self.total_price.setDecimals(2)

        self.status = QComboBox()
        self.status.addItems(["reserved", "checked_in", "checked_out", "cancelled"])

        self.guest_count = QSpinBox()
        self.guest_count.setRange(1, 20)

        self.notes = QPlainTextEdit()

        if initial:
            self._apply_initial(initial)

        layout = QFormLayout(self)
        layout.addRow("Client", self.client)
        layout.addRow("Room", self.room)
        layout.addRow("Check-in", self.check_in)
        layout.addRow("Check-out", self.check_out)
        layout.addRow("Total price", self.total_price)
        layout.addRow("Status", self.status)
        layout.addRow("Guest count", self.guest_count)
        layout.addRow("Notes", self.notes)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _apply_initial(self, initial: dict) -> None:
        client_idx = self.client.findData(initial.get("client_id"))
        room_idx = self.room.findData(initial.get("room_id"))
        if client_idx >= 0:
            self.client.setCurrentIndex(client_idx)
        if room_idx >= 0:
            self.room.setCurrentIndex(room_idx)

        self.check_in.setDate(self.check_in.date().fromString(initial.get("check_in"), "yyyy-MM-dd"))
        self.check_out.setDate(self.check_out.date().fromString(initial.get("check_out"), "yyyy-MM-dd"))
        self.total_price.setValue(float(initial.get("total_price", 0)))
        self.status.setCurrentText(initial.get("status", "reserved"))
        self.guest_count.setValue(initial.get("guest_count", 1))
        self.notes.setPlainText(initial.get("notes") or "")

    def payload(self) -> dict:
        return {
            "client_id": self.client.currentData(),
            "room_id": self.room.currentData(),
            "check_in": self.check_in.date().toString("yyyy-MM-dd"),
            "check_out": self.check_out.date().toString("yyyy-MM-dd"),
            "total_price": self.total_price.value(),
            "status": self.status.currentText(),
            "guest_count": self.guest_count.value(),
            "notes": self.notes.toPlainText().strip() or None,
            "is_paid": False,
        }


class MarkPaidDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mark booking as paid")

        self.amount = QDoubleSpinBox()
        self.amount.setMaximum(1000000)
        self.amount.setDecimals(2)

        self.payment_method = QLineEdit("cash")
        self.comment = QLineEdit()

        layout = QFormLayout(self)
        layout.addRow("Amount", self.amount)
        layout.addRow("Payment method", self.payment_method)
        layout.addRow("Comment", self.comment)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def payload(self) -> dict:
        return {
            "amount": self.amount.value(),
            "payment_method": self.payment_method.text().strip(),
            "comment": self.comment.text().strip() or None,
        }

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class DashboardPage(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client

        self.clients_label = QLabel("Clients: 0")
        self.rooms_label = QLabel("Rooms: 0")
        self.active_bookings_label = QLabel("Active bookings: 0")
        self.unpaid_bookings_label = QLabel("Unpaid bookings: 0")
        self.occupancy_label = QLabel("Occupancy rate: 0%")

        layout = QVBoxLayout(self)
        layout.addWidget(self.clients_label)
        layout.addWidget(self.rooms_label)
        layout.addWidget(self.active_bookings_label)
        layout.addWidget(self.unpaid_bookings_label)
        layout.addWidget(self.occupancy_label)
        layout.addStretch()

    def refresh(self) -> None:
        stats = self.api_client.get("/dashboard/stats")
        self.clients_label.setText(f"Clients: {stats['clients_total']}")
        self.rooms_label.setText(f"Rooms: {stats['rooms_total']}")
        self.active_bookings_label.setText(f"Active bookings: {stats['active_bookings_total']}")
        self.unpaid_bookings_label.setText(f"Unpaid bookings: {stats['unpaid_bookings_total']}")
        self.occupancy_label.setText(f"Occupancy rate: {stats['occupancy_rate_percent']}%")

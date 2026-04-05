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
from desktop_client.ui.widgets.forms import ClientFormDialog


class ClientsPage(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Full name", "Phone", "Email"])

        self.add_button = QPushButton("Add client")
        self.edit_button = QPushButton("Edit client")
        self.delete_button = QPushButton("Delete client")

        self.add_button.clicked.connect(self.add_client)
        self.edit_button.clicked.connect(self.edit_client)
        self.delete_button.clicked.connect(self.delete_client)

        actions = QHBoxLayout()
        actions.addWidget(self.add_button)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(actions)
        layout.addWidget(self.table)

    def refresh(self):
        clients = self.api_client.get("/clients/")
        self.table.setRowCount(len(clients))
        for row, client in enumerate(clients):
            self.table.setItem(row, 0, QTableWidgetItem(str(client["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(client["full_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(client["phone"]))
            self.table.setItem(row, 3, QTableWidgetItem(client.get("email") or ""))

    def _selected_client_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def add_client(self):
        dialog = ClientFormDialog(self)
        if dialog.exec():
            try:
                self.api_client.post("/clients/", dialog.payload())
                self.refresh()
                QMessageBox.information(self, "Saved", "Client created.")
            except ApiError as exc:
                QMessageBox.critical(self, "Error", str(exc))

    def edit_client(self):
        client_id = self._selected_client_id()
        if not client_id:
            QMessageBox.warning(self, "Selection", "Select a client first.")
            return

        initial = self.api_client.get(f"/clients/{client_id}")
        dialog = ClientFormDialog(self, initial=initial)
        if dialog.exec():
            try:
                self.api_client.put(f"/clients/{client_id}", dialog.payload())
                self.refresh()
                QMessageBox.information(self, "Saved", "Client updated.")
            except ApiError as exc:
                QMessageBox.critical(self, "Error", str(exc))

    def delete_client(self):
        client_id = self._selected_client_id()
        if not client_id:
            QMessageBox.warning(self, "Selection", "Select a client first.")
            return

        try:
            self.api_client.delete(f"/clients/{client_id}")
            self.refresh()
            QMessageBox.information(self, "Deleted", "Client deleted.")
        except ApiError as exc:
            QMessageBox.critical(self, "Error", str(exc))

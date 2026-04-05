from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget


class Sidebar(QWidget):
    page_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.menu = QListWidget()
        self.menu.setObjectName("sidebarMenu")
        for page in ["Dashboard", "Clients", "Rooms", "Bookings", "Reports"]:
            QListWidgetItem(page, self.menu)

        self.menu.currentTextChanged.connect(self.page_selected.emit)
        self.menu.setCurrentRow(0)

        layout = QVBoxLayout(self)
        layout.addWidget(self.menu)

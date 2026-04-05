from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMessageBox, QStackedWidget, QWidget

from desktop_client.api.client import ApiClient, ApiError
from desktop_client.config import APP_TITLE
from desktop_client.ui.pages.bookings_page import BookingsPage
from desktop_client.ui.pages.clients_page import ClientsPage
from desktop_client.ui.pages.dashboard_page import DashboardPage
from desktop_client.ui.pages.reports_page import ReportsPage
from desktop_client.ui.pages.rooms_page import RoomsPage
from desktop_client.ui.widgets.sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1200, 700)

        self.api_client = ApiClient()

        self.sidebar = Sidebar()
        self.sidebar.page_selected.connect(self.switch_page)

        self.pages = QStackedWidget()
        self.dashboard_page = DashboardPage(self.api_client)
        self.clients_page = ClientsPage(self.api_client)
        self.rooms_page = RoomsPage(self.api_client)
        self.bookings_page = BookingsPage(self.api_client)
        self.reports_page = ReportsPage(self.api_client)

        self.page_map = {
            "Dashboard": self.dashboard_page,
            "Clients": self.clients_page,
            "Rooms": self.rooms_page,
            "Bookings": self.bookings_page,
            "Reports": self.reports_page,
        }

        for page_name in ["Dashboard", "Clients", "Rooms", "Bookings", "Reports"]:
            self.pages.addWidget(self.page_map[page_name])

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(self.sidebar, 1)
        layout.addWidget(self.pages, 5)
        self.setCentralWidget(container)

        self.refresh_current_page()

    def switch_page(self, page_name: str):
        page_widget = self.page_map[page_name]
        self.pages.setCurrentWidget(page_widget)
        self.refresh_current_page()

    def refresh_current_page(self):
        page = self.pages.currentWidget()
        if hasattr(page, "refresh"):
            try:
                page.refresh()
            except ApiError as exc:
                QMessageBox.critical(self, "API Error", str(exc))

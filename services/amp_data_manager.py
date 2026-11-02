
import os

from dotenv import load_dotenv, find_dotenv

from PySide6.QtCore import QObject, QTimer, Signal, QThread

from services.amp_scraper import AMPScraper


load_dotenv(find_dotenv())


class AMPScraperThread(QThread):

    data_updated = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, amp_server, username, password):
        super().__init__()

        self.amp_server = amp_server
        self.username = username
        self.password = password

    def run(self):

        try:
            scraper = AMPScraper(
                self.amp_server,
                self.username,
                self.password
            )

            data = scraper.scrape()

            self.data_updated.emit(data)

        except Exception as e:
            self.error_occurred.emit(str(e))


class AMPDataManager(QObject):

    data_updated = Signal(list)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()

        self.amp_server = os.getenv("AMP_SERVER")
        self.username = os.getenv("AMP_USERNAME")
        self.password = os.getenv("AMP_PASSWORD")

        self.server_data = []

        # Widget activation tracking
        self.active_widgets = 0

        # Scraper thread
        self.scraper_thread = None

        # Refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)

    def activate(self):

        self.active_widgets += 1

        # Start scraping when the first widget activates
        if self.active_widgets == 1:

            self.refresh()

            self.refresh_timer.start(30_000)

    def deactivate(self):

        self.active_widgets = max(0, self.active_widgets - 1)

        # Stop refreshing when no widgets are active
        if self.active_widgets == 0:
            self.refresh_timer.stop()

    def refresh(self):

        # Don't scrape if no widgets are active
        if self.active_widgets == 0:
            return

        # Prevent overlapping scraping threads
        if self.scraper_thread is not None:
            if self.scraper_thread.isRunning():
                return

        self.scraper_thread = AMPScraperThread(
            self.amp_server,
            self.username,
            self.password
        )

        self.scraper_thread.data_updated.connect(
            self.update_server_data
        )

        self.scraper_thread.error_occurred.connect(
            self.error_occurred.emit
        )

        self.scraper_thread.finished.connect(
            self.scraper_finished
        )

        self.scraper_thread.start()

    def update_server_data(self, data):

        # Ignore results if all widgets are inactive
        if self.active_widgets == 0:
            return

        self.server_data = data
        self.data_updated.emit(data)

    def scraper_finished(self):

        thread = self.scraper_thread
        self.scraper_thread = None

        if thread is not None:
            thread.deleteLater()

    def get_data(self):
        return self.server_data

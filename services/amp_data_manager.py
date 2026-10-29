from PySide6.QtCore import QObject, QTimer, Signal

from playwright.sync_api import sync_playwright

from dotenv import load_dotenv, find_dotenv
import os
import math

load_dotenv(find_dotenv())

AMP_SERVER = os.getenv("AMP_SERVER")
AMP_USERNAME = os.getenv("AMP_USERNAME")
AMP_PASSWORD = os.getenv("AMP_PASSWORD")

class AMPDataManager(QObject):
    data_updated = Signal(list)

    def __init__(self):
        super().__init__()

        self.server_data = []

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(30_000)

        # Get initial data immediately.
        self.refresh()

    def refresh(self):
        try:
            self.server_data = self.get_running_game_servers_information()

            # Notifiy widgets of updated data
            self.data_updated.emit(self.server_data)

        except Exception as e:
            print(f"Failed to update AMP data: {e}")

    def get_running_game_servers_information(self):
        server_data = []

        with sync_playwright() as playwright:
            browser = playwright.firefox.launch(headless=True)

            page = browser.new_page()

            page.goto(AMP_SERVER)
            page.wait_for_load_state("networkidle") # Wait for AMP to load correctly

            # Login to AMP
            page.locator('input[name="username"]').fill(os.getenv("AMP_USERNAME"))
            page.locator('input[name="password"]').fill(os.getenv("AMP_PASSWORD"))
            page.locator("#loginButton").click()

            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000) # Makes sure the page is loaded before getting data

            # Debug page contents
            # print("RUNNING DIV COUNT:",
            #     page.locator(".statusRunning").count())

            # print("SERVER ENTRY COUNT:",
            #     page.locator(".ServerEntryTop").count())

            # print("FRIENDLY NAME COUNT:",
            #     page.locator(
            #         '[data-bind="text: friendlyname"]'
            #     ).count())

            # Find running servers
            running_divs = page.locator(".statusRunning")
            friendly_name = running_divs.locator(".ServerEntryTop").locator(".ServerEntryHeader").locator('[data-bind="text: friendlyname"]')

            servers = friendly_name.all_text_contents()
            servers = servers[:math.ceil(len(servers)/2)]

            # Get CPU, MEMORY, and PLAYERS information
            metrics = running_divs.locator(".ServerEntryInfo").locator(".ServerEntryMetrics").locator(".ServerEntryMetric").locator(".MetricText").locator("h4")
            metrics_array = metrics.all_text_contents()
            metrics_array = metrics_array[:len(metrics_array)//2]

            next_index = 0
            for i in range(len(servers)):
                single_server_data = {
                    "name": servers[i],
                    "cpu_usage": metrics_array[0+next_index],
                    "ram_usage": metrics_array[1+next_index],
                    "player_count": metrics_array[2+next_index]
                }
                next_index += 3
                server_data.append(single_server_data)

            browser.close()
            return server_data

    def get_data(self):
        return self.server_data
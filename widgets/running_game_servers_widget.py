from PySide6.QtCore import QTimer, QDateTime, Qt
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout

from widgets.base_widget import BaseWidget

# Web scrapping for AMP game Servers
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv, dotenv_values, find_dotenv
import os

# Find the env file
load_dotenv(find_dotenv())

# Local hosted AMP Server IP
AMP_SERVER = os.getenv("AMP_SERVER")

WIDTH = 300
HEIGHT_PER_SERVER = 100

class RunningGameServersWidget(BaseWidget):    

    def __init__(self):
        super().__init__("Game Servers")

        self.server_data = self.get_running_game_servers_information()
        num_servers = len(self.server_data)

        height = HEIGHT_PER_SERVER * num_servers

        self.server_labels = []

        for server in self.server_data:

            # Vertical layout for each server
            server_layout = QVBoxLayout()
            server_layout.setSpacing(5)

            # Server name
            server_name = QLabel(server["name"])
            server_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
            server_name.setStyleSheet("""
                color: white;
                font-size: 18px;
                font-weight: bold;
            """)

            server_layout.addWidget(server_name)

            # Horizontal layout for CPU, RAM, and players
            metrics_layout = QHBoxLayout()
            metrics_layout.setSpacing(10)

            # Create labels with consistent widths
            server_cpu = QLabel(f"CPU: {server['cpu_usage']}")
            server_ram = QLabel(f"RAM: {server['ram_usage']}")
            server_players = QLabel(f"Players: {server['player_count']}")

            server_cpu.setFixedWidth(75)
            server_ram.setFixedWidth(125)
            server_players.setFixedWidth(100)

            for label in (server_cpu, server_ram, server_players):
                label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                label.setStyleSheet("""
                    color: white;
                    font-size: 13px;
                """)

            metrics_layout.addWidget(server_cpu)
            metrics_layout.addWidget(server_ram)
            metrics_layout.addWidget(server_players)

            self.server_labels.append({
                "name": server_name,
                "cpu": server_cpu,
                "ram": server_ram,
                "players": server_players
            })

            server_layout.addLayout(metrics_layout)

            # Add this server's complete layout to the widget
            self.content_layout.addLayout(server_layout)

        self.style_widget()
        self.resize(WIDTH, max(height, HEIGHT_PER_SERVER))

        # Update data every 30 seconds
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_server_data)
        self.refresh_timer.start(30_000)

    def refresh_server_data(self):
        updated_data = self.get_running_game_servers_information()

        for i, server in enumerate(updated_data):
            if i >= len(self.server_labels):
                break

            labels = self.server_labels[i]

            labels["name"].setText(server["name"])
            labels["cpu"].setText(f"CPU: {server['cpu_usage']}")
            labels["ram"].setText(f"RAM: {server['ram_usage']}")
            labels["players"].setText(f"Players: {server['player_count']}")


    def get_running_game_servers_information(self):
        self.server_data = []
        with sync_playwright() as playwright:
            browser = playwright.firefox.launch(headless = True)
            page = browser.new_page()
            page.goto(AMP_SERVER)
            page.wait_for_load_state("networkidle")

            # Log in to amp
            page.locator('input[name="username"]').fill(os.getenv("AMP_USERNAME"))
            page.locator('input[name="password"]').fill(os.getenv("AMP_PASSWORD"))
            page.locator("#loginButton").click()

            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000) # Makes sure the page is loaded before getting data

            # Find the needed divs
            running_divs = page.locator(".statusRunning")
            friendly_name = running_divs.locator(".ServerEntryTop").locator(".ServerEntryHeader").locator('[data-bind="text: friendlyname"]')

            servers = friendly_name.all_text_contents()
            servers = servers[:len(servers)//2]

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
                self.server_data.append(single_server_data)

            browser.close()
            return self.server_data
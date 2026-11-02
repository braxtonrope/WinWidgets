
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QGridLayout

from widgets.base_widget import BaseWidget

WIDTH = 300
HEIGHT_PER_SERVER = 100


class RunningGameServersWidget(BaseWidget):

    def __init__(self, amp_manager):
        super().__init__("Game Servers")

        self.amp_manager = amp_manager
        self.is_active = False

        self.server_labels = []

        # Listen for updates from AMPDataManager
        self.amp_manager.data_updated.connect(
            self.refresh_server_data
        )

        # Display cached data if available
        server_data = self.amp_manager.get_data()

        if server_data:
            self.create_server_widgets(server_data)

        self.style_widget()
        self.update_widget_size()

    def showEvent(self, event):
        super().showEvent(event)

        if not self.is_active:
            self.is_active = True
            self.amp_manager.activate()

    def hideEvent(self, event):
        super().hideEvent(event)

        if self.is_active:
            self.is_active = False
            self.amp_manager.deactivate()

    def refresh_server_data(self, updated_data):

        # If the number of servers has changed, rebuild the layout
        if len(updated_data) != len(self.server_labels):
            self.clear_server_widgets()
            self.create_server_widgets(updated_data)
            self.update_widget_size()
            return

        # Update existing widgets
        for i, server in enumerate(updated_data):

            labels = self.server_labels[i]

            labels["name"].setText(server["name"])
            labels["cpu"].setText(f"CPU: {server['cpu_usage']}")
            labels["ram"].setText(f"RAM: {server['ram_usage']}")
            labels["players"].setText(
                f"Players: {server['player_count']}"
            )

    def create_server_widgets(self, server_data):

        for server in server_data:

            server_layout = QGridLayout()
            server_layout.setContentsMargins(10, 10, 10, 10)
            server_layout.setSpacing(20)

            # Server name
            server_name = QLabel(server["name"])
            server_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
            server_name.setStyleSheet("""
                color: white;
                font-size: 18px;
                font-weight: bold;
            """)

            server_layout.addWidget(server_name, 0, 0, 1, 3)

            # Server metrics
            server_cpu = QLabel(f"CPU: {server['cpu_usage']}")
            server_ram = QLabel(f"RAM: {server['ram_usage']}")
            server_players = QLabel(
                f"Players: {server['player_count']}"
            )

            for label in (server_cpu, server_ram, server_players):
                label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                label.setStyleSheet("""
                    color: white;
                    font-size: 13px;
                """)

            server_layout.addWidget(server_cpu, 1, 0)
            server_layout.addWidget(server_ram, 1, 1)
            server_layout.addWidget(server_players, 1, 2)

            self.server_labels.append({
                "name": server_name,
                "cpu": server_cpu,
                "ram": server_ram,
                "players": server_players
            })

            self.content_layout.addLayout(server_layout)

    def clear_server_widgets(self):

        for labels in self.server_labels:

            for label in labels.values():
                label.deleteLater()

        self.server_labels.clear()

        # Remove old layouts from content_layout
        while self.content_layout.count():

            item = self.content_layout.takeAt(0)

            if item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)

                    if child.widget():
                        child.widget().deleteLater()

                item.layout().deleteLater()

    def update_widget_size(self):

        server_count = len(self.server_labels)

        height = HEIGHT_PER_SERVER * server_count

        self.resize(
            int(WIDTH),
            max(height, HEIGHT_PER_SERVER)
        )

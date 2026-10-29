from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout

from widgets.base_widget import BaseWidget

WIDTH = 300
HEIGHT_PER_SERVER = 100

class RunningGameServersWidget(BaseWidget):    

    def __init__(self, scale, amp_manager):
        super().__init__("Game Servers", scale)
        self.scale = scale

        self.amp_manager = amp_manager

        # Get current data
        server_data = amp_manager.get_data()
       
        self.server_labels = []

        # Listen for updates from the manager
        self.amp_manager.data_updated.connect(self.refresh_server_data)

        # Check if data already exists
        server_data = self.amp_manager.get_data()
        if server_data:
            self.create_server_widgets(server_data)

        self.style_widget()
        height = HEIGHT_PER_SERVER * len(server_data)
        self.resize(int(WIDTH * self.scale), int(max(height, HEIGHT_PER_SERVER) * self.scale))

        


    def refresh_server_data(self, updated_data):

        # If there are no widgets yet, create them all
        if not self.server_labels:
            self.create_server_widgets(updated_data)
            self.update_widget_size()
            return

        # Update existing widgets
        for i, server in enumerate(updated_data):

            if i >= len(self.server_labels):
                print("Missing widget for:", server["name"])
                continue

            labels = self.server_labels[i]

            labels["name"].setText(server["name"])
            labels["cpu"].setText(f"CPU: {server['cpu_usage']}")
            labels["ram"].setText(f"RAM: {server['ram_usage']}")
            labels["players"].setText(
                f"Players: {server['player_count']}"
            )


    def create_server_widgets(self, server_data):
        for server in server_data:
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

            server_cpu.setFixedWidth(int(75*self.scale))
            server_ram.setFixedWidth(int(125*self.scale))
            server_players.setFixedWidth(int(100*self.scale))

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


    def update_widget_size(self):

        server_count = len(self.server_labels)

        height = HEIGHT_PER_SERVER * server_count

        self.resize(
            int(WIDTH * self.scale),
            int(
                max(height, HEIGHT_PER_SERVER)
                * self.scale
            )
        )
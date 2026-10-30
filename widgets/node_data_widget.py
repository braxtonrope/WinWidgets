from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout

from widgets.base_widget import BaseWidget

WIDTH = 300
HEIGHT_PER_SERVER = 100

class NodeDataWidget(BaseWidget):    

    def __init__(self, scale, node_manager):
        super().__init__("Node Data", scale)
        self.scale = scale

        self.node_manager = node_manager

        # Get current data
        node_data = node_manager.get_data()

        self.node_labels = []

        # Check if data already exists
        node_data = self.node_manager.get_data()
        if node_data:
            self.create_widgets(node_data)

        self.style_widget()
        height = HEIGHT_PER_SERVER * len(node_data)
        self.resize(int(WIDTH * self.scale), int(max(height, HEIGHT_PER_SERVER) * self.scale))

    def create_widgets(self, node_data):
        for node in node_data:
            # Vertical layout for each server
            node_layout = QVBoxLayout()
            node_layout.setSpacing(5)

            # Server name
            node_name = QLabel(node["node_name"])
            node_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
            node_name.setStyleSheet("""
                color: white;
                font-size: 18px;
                font-weight: bold;
            """)

            node_layout.addWidget(node_name)

            # Horizontal layout for CPU usage, Ram free, Disk free, and CPU Temp 
            metrics_layout = QHBoxLayout()
            metrics_layout.setSpacing(10)

            # Create labels with consistent widths
            cpu_usage = QLabel(f"CPU Usage: {node['cpu_usage']}")
            ram_free = QLabel(f"RAM Free: {node['ram_free']}")
            disk_free = QLabel(f"Disk Free: {node['disk_free']}")
            cpu_temp = QLabel(f"CPU Temp: {node['cpu_temp']}")

            # cpu_usage.setFixedWidth(int(50*self.scale))
            # ram_free.setFixedWidth(int(125*self.scale))
            # disk_free.setFixedWidth(int(125*self.scale))
            # cpu_temp.setFixedWidth(int(50*self.scale))

            for label in (cpu_usage, ram_free, disk_free, cpu_temp):
                label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                label.setStyleSheet("""
                    color: white;
                    font-size: 13px;
                """)

            metrics_layout.addWidget(cpu_usage)
            metrics_layout.addWidget(ram_free)
            metrics_layout.addWidget(disk_free)
            metrics_layout.addWidget(cpu_temp)

            self.node_labels.append({
                "node_name": node_name,
                "cpu_usage": cpu_usage,
                "ram_free": ram_free,
                "disk_free": disk_free,
                "cpu_temp": cpu_temp
            })

            node_layout.addLayout(metrics_layout)

            # Add this server's complete layout to the widget
            self.content_layout.addLayout(node_layout)



    def refresh_data(self, updated_data):
        # If there are no widgets yet, create them all
        if not self.node_labels:
            self.create_widgets(updated_data)
            self.update_widget_size()
            return

        # Update existing widgets
        for i, node in enumerate(updated_data):

            if i >= len(self.server_labels):
                print("Missing widget for:", node["node_name"])
                continue

            labels = self.server_labels[i]

            labels["node_name"].setText(node["node_name"])
            labels["node_ip"].setText(f"IP: {node['node_ip']}")
            labels["cpu_usage"].setText(f"CPU Usage: {node['cpu_usage']}")
            labels["ram_free"].setText(f"RAM Free: {node['ram_free']}")
            labels["disk_free"].setText(f"Disk Free: {node['disk_free']}")
            labels["cpu_temp"].setText(f"CPU Temp: {node['cpu_temp']}")


    def update_widget_size(self):
        node_count = len(self.node_labels)

        height = HEIGHT_PER_SERVER * node_count

        self.resize(
            int(WIDTH * self.scale),
            int(
                max(height, HEIGHT_PER_SERVER)
                * self.scale
            )
        )
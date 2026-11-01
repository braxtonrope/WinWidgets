from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QGridLayout

from widgets.base_widget import BaseWidget

WIDTH = 300
HEIGHT_PER_SERVER = 100

class NodeDataWidget(BaseWidget):    

    def __init__(self, node_manager):
        super().__init__("Node Data")

        self.node_manager = node_manager

        # Get current data
        node_data = node_manager.get_data()

        self.node_labels = []

        # Check if data already exists
        node_data = self.node_manager.get_data()
        if node_data:
            self.create_widgets(node_data)

        self.style_widget()
        self.update_widget_size()

    def create_widgets(self, node_data):
        for node in node_data:
            node_layout = QGridLayout()
            node_layout.setContentsMargins(10,10,10,10)
            node_layout.setSpacing(10)
            # Server name
            node_name = QLabel(node["node_name"])
            node_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
            node_name.setStyleSheet("""
                color: white;
                font-size: 18px;
                font-weight: bold;
            """)

            node_ip = QLabel(node["node_ip"])
            node_ip.setStyleSheet("""
                color: white;
                font-size: 18px;
                font-weight: bold;
            """)

            node_layout.addWidget(node_name, 0,0)
            node_layout.addWidget(node_ip, 0,1)


            # Create labels with consistent widths
            cpu_usage = QLabel(f"CPU Usage: {node['cpu_usage']}")
            ram_free = QLabel(f"RAM Free: {node['ram_free']}")
            disk_free = QLabel(f"Disk Free: {node['disk_free']}")
            cpu_temp = QLabel(f"CPU Temp: {node['cpu_temp']}")

            for label in (cpu_usage, ram_free, disk_free, cpu_temp):
                label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                label.setStyleSheet("""
                    color: white;
                    font-size: 13px;
                """)

            node_layout.addWidget(cpu_usage, 1, 0)
            node_layout.addWidget(ram_free, 2, 0)
            node_layout.addWidget(disk_free, 2, 1)
            node_layout.addWidget(cpu_temp, 1, 1)

            self.node_labels.append({
                "node_name": node_name,
                "node_ip": node_ip,
                "cpu_usage": cpu_usage,
                "ram_free": ram_free,
                "disk_free": disk_free,
                "cpu_temp": cpu_temp
            })

            self.content_layout.addLayout(node_layout)



    def refresh_data(self, updated_data):
        # If there are no widgets yet, create them all
        if not self.node_labels:
            self.create_widgets(updated_data)
            self.update_widget_size()
            return

        # Update existing widgets
        for i, node in enumerate(updated_data):

            if i >= len(self.node_labels):
                print("Missing widget for:", node["node_name"])
                continue

            labels = self.node_labels[i]

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
            int(WIDTH),
            int(
                max(height, HEIGHT_PER_SERVER)
            )
        )
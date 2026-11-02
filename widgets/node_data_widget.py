
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QGridLayout

from widgets.base_widget import BaseWidget


WIDTH = 350
HEIGHT_PER_NODE = 110


class NodeDataWidget(BaseWidget):

    def __init__(self, node_manager):
        super().__init__("Node Data")

        self.node_manager = node_manager

        self.node_labels = {}

        # Listen for monitoring updates
        self.node_manager.data_updated.connect(
            self.refresh_data
        )

        # Display cached data
        node_data = self.node_manager.get_data()

        if node_data:
            self.refresh_data(node_data)

        self.style_widget()
        self.update_widget_size()

    # ----------------------------------------------
    # Create node widgets
    # ----------------------------------------------

    def create_widgets(self, node_data):

        for node in node_data:

            node_ip = node["node_ip"]

            node_layout = QGridLayout()
            node_layout.setContentsMargins(10, 10, 10, 10)
            node_layout.setSpacing(10)

            # Node name
            node_name = QLabel(node["node_name"])
            node_name.setStyleSheet("""
                color: white;
                font-size: 18px;
                font-weight: bold;
            """)

            # Node IP
            ip_label = QLabel(f"IP: {node_ip}")
            ip_label.setStyleSheet("""
                color: white;
                font-size: 12px;
            """)

            # Status
            status = QLabel()
            status.setAlignment(Qt.AlignmentFlag.AlignRight)

            # Metrics
            cpu_usage = QLabel()
            cpu_temp = QLabel()
            ram_free = QLabel()
            disk_free = QLabel()

            for label in (
                cpu_usage,
                cpu_temp,
                ram_free,
                disk_free
            ):
                label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                label.setStyleSheet("""
                    color: white;
                    font-size: 13px;
                """)

            # Layout
            node_layout.addWidget(node_name, 0, 0)
            node_layout.addWidget(status, 0, 1)

            node_layout.addWidget(ip_label, 1, 0, 1, 2)

            node_layout.addWidget(cpu_usage, 2, 0)
            node_layout.addWidget(cpu_temp, 2, 1)

            node_layout.addWidget(ram_free, 3, 0)
            node_layout.addWidget(disk_free, 3, 1)

            self.content_layout.addLayout(node_layout)

            # Store labels using IP as identifier
            self.node_labels[node_ip] = {
                "layout": node_layout,
                "node_name": node_name,
                "node_ip": ip_label,
                "status": status,
                "cpu_usage": cpu_usage,
                "cpu_temp": cpu_temp,
                "ram_free": ram_free,
                "disk_free": disk_free
            }

            # Populate labels
            self.update_node(node)

    # ----------------------------------------------
    # Update individual node
    # ----------------------------------------------

    def update_node(self, node):

        node_ip = node["node_ip"]

        if node_ip not in self.node_labels:
            return

        labels = self.node_labels[node_ip]

        status = node.get("status", "unknown")

        # Node status
        if status == "online":
            labels["status"].setText("ONLINE")
            labels["status"].setStyleSheet("""
                color: #4ade80;
                font-size: 12px;
                font-weight: bold;
            """)

        elif status == "offline":
            labels["status"].setText("OFFLINE")
            labels["status"].setStyleSheet("""
                color: #f87171;
                font-size: 12px;
                font-weight: bold;
            """)

        else:
            labels["status"].setText("ERROR")
            labels["status"].setStyleSheet("""
                color: #fbbf24;
                font-size: 12px;
                font-weight: bold;
            """)

        labels["node_name"].setText(
            node.get("node_name") or "Unknown Node"
        )

        labels["node_ip"].setText(
            f"IP: {node_ip or 'Unknown'}"
        )

        # Display metrics
        labels["cpu_usage"].setText(
            f"CPU Usage: {node.get('cpu_usage') or 'N/A'}"
        )

        labels["cpu_temp"].setText(
            f"CPU Temp: {node.get('cpu_temp') or 'N/A'}"
        )

        labels["ram_free"].setText(
            f"RAM Free: {node.get('ram_free') or 'N/A'}"
        )

        labels["disk_free"].setText(
            f"Disk Free: {node.get('disk_free') or 'N/A'}"
        )

        # Grey out unavailable metrics
        metric_names = (
            "cpu_usage",
            "cpu_temp",
            "ram_free",
            "disk_free"
        )

        for metric in metric_names:

            if node.get(metric) is None:
                labels[metric].setStyleSheet("""
                    color: #888888;
                    font-size: 13px;
                """)
            else:
                labels[metric].setStyleSheet("""
                    color: white;
                    font-size: 13px;
                """)

        # Show errors in tooltip
        errors = node.get("metric_errors", [])

        if node.get("error"):
            error_text = node["error"]
        else:
            error_text = "\n".join(errors)

        labels["status"].setToolTip(
            error_text or "No errors"
        )

    # ----------------------------------------------
    # Refresh all node data
    # ----------------------------------------------

    def refresh_data(self, updated_data):

        updated_ips = {
            node["node_ip"]
            for node in updated_data
            if node.get("node_ip")
        }

        existing_ips = set(self.node_labels.keys())

        # Rebuild if nodes have been added or removed
        if updated_ips != existing_ips:

            self.clear_widgets()
            self.create_widgets(updated_data)
            self.update_widget_size()

            return

        # Update existing nodes
        for node in updated_data:
            self.update_node(node)

    # ----------------------------------------------
    # Remove existing widgets
    # ----------------------------------------------

    def clear_widgets(self):

        self.node_labels.clear()

        while self.content_layout.count():

            item = self.content_layout.takeAt(0)

            if item.layout():

                layout = item.layout()

                while layout.count():

                    child = layout.takeAt(0)

                    if child.widget():
                        child.widget().deleteLater()

                layout.deleteLater()

            elif item.widget():
                item.widget().deleteLater()

    # ----------------------------------------------
    # Widget sizing
    # ----------------------------------------------

    def update_widget_size(self):

        node_count = len(self.node_labels)

        height = HEIGHT_PER_NODE * node_count

        self.resize(
            WIDTH,
            max(height, HEIGHT_PER_NODE)
        )

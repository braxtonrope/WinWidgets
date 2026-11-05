from widgets.base_widget import BaseWidget

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QGridLayout

class SystemStatsWidget(BaseWidget):
    def __init__(self, hardware_manager):
        super().__init__("System Stats")

        self.hardware_manager = hardware_manager
        
        self.system_stats_labels = {}
        
        
        self.create_widgets()

        # Listen for monitoring updates
        self.hardware_manager.data_updated.connect(
            self.refresh_data
        )

        # Display cached data
        data = self.hardware_manager.get_data()

        if data:
            self.refresh_data(data)

        self.style_widget()

    def refresh_data(self, updated_data):
        self.system_stats_labels["cpu_temp"].setText(f"{updated_data['cpu_temp']}°C")
        self.system_stats_labels["cpu_usage"].setText(f"{updated_data['cpu_usage']}%")
        self.system_stats_labels["ram_usage"].setText(f"{updated_data['ram_usage']}%")

    def create_widgets(self):
        system_stats_layout = QGridLayout()

        # Metrics
        cpu_usage = QLabel()
        cpu_temp = QLabel()
        ram_usage = QLabel()

        for label in (
            cpu_usage,
            cpu_temp,
            ram_usage
        ):
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setStyleSheet("""
                color: white;
                font-size: 13px;
            """)

        # Layout
        system_stats_layout.addWidget(cpu_temp, 0, 0)
        system_stats_layout.addWidget(cpu_usage, 0, 1)
        system_stats_layout.addWidget(ram_usage, 0, 2)

        self.content_layout.addLayout(system_stats_layout)

        # Store labels using IP as identifier
        self.system_stats_labels = {
            "layout": system_stats_layout,
            "cpu_usage": cpu_usage,
            "cpu_temp": cpu_temp,
            "ram_usage": ram_usage
        }
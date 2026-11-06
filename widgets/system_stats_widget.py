from widgets.base_widget import BaseWidget

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QGridLayout
from PySide6.QtGui import QPixmap

from pathlib import Path

WIDTH = 300
HEIGHT = 100

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

        # Images
        ROOT_DIR = Path(__file__).resolve().parent.parent
        ASSETS_DIR = ROOT_DIR / "assets"
        # Setup your sizes
        ICON_SIZE = 32 

        # Load and scale efficiently
        cpu_temp_img = QPixmap(str(ASSETS_DIR / "cpu_temp_img.png")).scaled(
            ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        cpu_usage_img = QPixmap(str(ASSETS_DIR / "cpu_usage_img.png")).scaled(
            ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        ram_img = QPixmap(str(ASSETS_DIR / "ram_img.png")).scaled(
            ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )

        cpu_temp_img_label = QLabel()
        cpu_temp_img_label.setPixmap(cpu_temp_img)
        cpu_usage_img_label = QLabel()
        cpu_usage_img_label.setPixmap(cpu_usage_img)
        ram_img_label = QLabel()
        ram_img_label.setPixmap(ram_img)


        for label in (
            cpu_usage,
            cpu_temp,
            ram_usage
        ):
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setStyleSheet("""
                color: white;
                font-size: 18px;
            """)

        # Layout
        # Images
        system_stats_layout.addWidget(cpu_temp_img_label, 0, 0, Qt.AlignmentFlag.AlignCenter)
        system_stats_layout.addWidget(cpu_usage_img_label, 0, 1, Qt.AlignmentFlag.AlignCenter)
        system_stats_layout.addWidget(ram_img_label, 0, 2, Qt.AlignmentFlag.AlignCenter)

        # Metrics
        system_stats_layout.addWidget(cpu_temp, 1, 0, Qt.AlignmentFlag.AlignCenter)
        system_stats_layout.addWidget(cpu_usage, 1, 1, Qt.AlignmentFlag.AlignCenter)
        system_stats_layout.addWidget(ram_usage, 1, 2, Qt.AlignmentFlag.AlignCenter)

        self.content_layout.addLayout(system_stats_layout)

        # Store labels using IP as identifier
        self.system_stats_labels = {
            "layout": system_stats_layout,
            "cpu_usage": cpu_usage,
            "cpu_temp": cpu_temp,
            "ram_usage": ram_usage
        }

        self.resize(int(WIDTH),int(HEIGHT))
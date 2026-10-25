from PySide6.QtCore import QTimer, QDateTime, Qt
from PySide6.QtWidgets import QLabel

from widgets.base_widget import BaseWidget

class TimeWidget(BaseWidget):
    def __init__(self):
        super().__init__("Time And Date")

        # Time Display
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            color: white;
            font-size: 34px;
            font-weight: bold;
        """)

        # Date Display
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("""
            color: #BBBBCC;
            font-size: 14px;
        """)

        self.content_layout.addWidget(self.time_label)
        self.content_layout.addWidget(self.date_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.update_time()

        self.resize(500,100)

    def update_time(self):
        now = QDateTime.currentDateTime()

        self.time_label.setText(
            now.toString("hh:mm:ss")
        )

        self.date_label.setText(
            now.toString("dddd, d MMM yyyy")
        )
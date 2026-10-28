from PySide6.QtCore import QTimer, QDateTime, Qt
from PySide6.QtWidgets import QLabel

from widgets.base_widget import BaseWidget

WIDTH = 500
HEIGHT = 100

class TimeWidget(BaseWidget):
    def __init__(self):
        super().__init__("Time And Date")

        # Time Display
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            color: white;
            font-size: 54px;
            font-weight: bold;
        """)

        # Date Display
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("""
            color: #BBBBCC;
            font-size: 28px;
        """)

        self.style_widget()

        self.content_layout.addWidget(self.time_label)
        self.content_layout.addWidget(self.date_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.update_time()

        self.resize(WIDTH,HEIGHT)

    def update_time(self):
        now = QDateTime.currentDateTime()

        hour = now.time().hour() % 12 or 12
        self.time_label.setText(
            # 24 Hour time
            # now.toString("hh:mm:ss")

            # 12 Hour time
            f"{hour}:{now.toString('mm:ss')}"
        )

        self.date_label.setText(
            now.toString("dddd, d MMM yyyy")
        )

    def style_widget(self):
        return
from PySide6.QtCore import QTimer, QDateTime, Qt
from PySide6.QtWidgets import QLabel

from widgets.base_widget import BaseWidget

class TimeWidget(BaseWidget):
    def __init__(self):
        super().__init__("Weather")
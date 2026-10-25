
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout


class BaseWidget(QWidget):

    def __init__(self, title):
        super().__init__()

        self.setWindowTitle(title)

        # Frameless desktop-style window
        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint
        )

        # Allow transparent areas around the card
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        # Create the card background
        self.card = QFrame()
        self.card.setObjectName("card")

        self.card.setStyleSheet("""
            QFrame#card {
                background-color: rgba(30, 30, 40, 230);
                border-radius: 16px;
            }
        """)

        # Layout inside the card
        self.content_layout = QVBoxLayout(self.card)
        self.content_layout.setContentsMargins(18, 15, 18, 15)
        self.content_layout.setSpacing(6)

        # Layout for the window itself
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(self.card)

        self.resize(250, 120)

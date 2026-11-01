
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGraphicsDropShadowEffect


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

        self.style_widget()

        # Layout inside the card
        self.content_layout = QVBoxLayout(self.card)
        self.content_layout.setContentsMargins(18, 15, 18, 15)
        self.content_layout.setSpacing(6)

        # Layout for the window itself
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(self.card)

        # Default Size
        self.resize(250, 120)
    
    # Style the Widget
    def style_widget(self):
        # Apply liquid glass preset
        self.card.setStyleSheet("""
            QFrame#card {
                    background-color: rgba(255, 255, 255, 35);
                    border: 1px solid rgba(255, 255, 255, 80);
                    border-radius: 28px;
                }
        """)

        # Add a subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(Qt.GlobalColor.black)

        self.card.setGraphicsEffect(shadow)


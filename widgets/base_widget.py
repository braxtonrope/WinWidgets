
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGraphicsDropShadowEffect


class BaseWidget(QWidget):

    # Notifiy of changes made to widget
    drag_started = Signal(object)
    dragging = Signal(object, object)
    drag_finished = Signal(object)
    context_menu_requested = Signal(object)


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

        self._dragging = False
        self._drag_offset = QPoint()

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

    
    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self._dragging = True

            mouse_position = event.globalPosition().toPoint()
            widget_position = self.frameGeometry().topLeft()

            self._drag_offset = mouse_position - widget_position

            self.drag_started.emit(self)

            event.accept()
            return

        elif event.button() == Qt.MouseButton.RightButton:
            self.context_menu_requested.emit(self)

            event.accept()
            return

        super().mousePressEvent(event)


    def mouseMoveEvent(self, event):

        if self._dragging:

            mouse_position = event.globalPosition().toPoint()
            new_position = mouse_position - self._drag_offset

            self.dragging.emit(self, new_position)

            event.accept()
            return

        super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self._dragging = False

            self.drag_finished.emit(self)

            event.accept()
            return

        super().mouseReleaseEvent(event)

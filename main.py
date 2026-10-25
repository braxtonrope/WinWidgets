import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QVBoxLayout,
    QFrame
    )

class DesktopWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Configure the window
        self.setWindowTitle("Desktop Widget")

        self.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint
        )

        # Allow Transparency
        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

        # Size the window
        self.resize(300,100)
                
        # Put the widget somewhere on the screen
        self.move(100,100)

        # # Create the Text
        # label = QLabel("Hello From My Desktop Widget!", self)


        # # Puts the label in the widget
        # label.setGeometry(0, 0, 300, 1000)

        # label.setAlignment(Qt.AlignCenter)

        # Main card
        card = QFrame()

        # CSS for the label (Convert to liquid glass later on)
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(25,25,30,230);
                border-radius: 20px;
            }
        """)

        title = QLabel("My Desktop")

        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """)

        # Widget Information
        info = QLabel("Hello From Your Desktop!")

        info.setStyleSheet("""
            QLabel {
                color: #bbbbbb;
                font-size: 16px;
            }
        """)

        # Layout inside card
        layout = QVBoxLayout(card)

        layout.addWidget(title)
        layout.addWidget(info)

        layout.setContentsMargins(20,20,20,20)

        window_layout = QVBoxLayout(self)

        window_layout.addWidget(card)

        window_layout.setContentsMargins(0,0,0,0)

def main():
    app = QApplication(sys.argv)

    widget = DesktopWidget()

    widget.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

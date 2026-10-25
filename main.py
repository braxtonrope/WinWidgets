import sys, os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication

from widgets.time_widget import TimeWidget



def main():

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    app.widgets = []

    screens = QGuiApplication.screens()

    for i in range(len(screens)):
        time_widget = TimeWidget()
        screen = screens[i]
        screen_geometry = screen.availableGeometry()

        # Force calculation of true widget size
        time_widget.show()
        time_widget.adjustSize()

        # Bind this window handle to the target screen
        if time_widget.windowHandle():
            time_widget.windowHandle().setScreen(screen)

        # Centers x by width of Screen
        x = screen_geometry.center().x() - time_widget.width() // 2
        y = screen_geometry.y() + 50 # Handle vertical monitor arangement

        time_widget.move(x,y)

        app.widgets.append(time_widget)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

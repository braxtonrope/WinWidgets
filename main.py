import sys, os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication

from widgets.time_widget import TimeWidget
from widgets.running_game_servers_widget import RunningGameServersWidget

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

app.widgets = []

screens = QGuiApplication.screens()

def main():

    add_running_game_servers_widgets()
    add_time_and_date_widgets()

    sys.exit(app.exec())

def add_time_and_date_widgets():
    

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

def add_running_game_servers_widgets():
    for i in range(len(screens)):
        running_game_servers_widget = RunningGameServersWidget()
        screen = screens[i]
        screen_geometry = screen.availableGeometry()

        running_game_servers_widget.show()
        running_game_servers_widget.adjustSize()

        if running_game_servers_widget.windowHandle():
            running_game_servers_widget.windowHandle().setScreen(screen)

        x = screen_geometry.x() + 50
        y = screen_geometry.y() + 50

        running_game_servers_widget.move(x,y)

        app.widgets.append(running_game_servers_widget)


if __name__ == "__main__":
    main()

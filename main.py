import sys, os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication

from widgets.time_widget import TimeWidget
from widgets.running_game_servers_widget import RunningGameServersWidget
from services.amp_data_manager import AMPDataManager
from services.node_data_manager import NodeDataManager

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

app.widgets = []

screens = QGuiApplication.screens()

# ONE shared AMP data manager
amp_manager = AMPDataManager()

def main():
    node_manager = NodeDataManager()
    add_running_game_servers_widgets()
    add_time_and_date_widgets()

    sys.exit(app.exec())

def add_time_and_date_widgets():

    for screen in screens:

        scale = get_screen_scale(screen)
        screen_geometry = screen.availableGeometry()

        time_widget = TimeWidget(scale)

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
    for screen in screens:
        
        scale = get_screen_scale(screen)
        screen_geometry = screen.availableGeometry()

        running_game_servers_widget = RunningGameServersWidget(scale, amp_manager)

        running_game_servers_widget.show()
        running_game_servers_widget.adjustSize()

        if running_game_servers_widget.windowHandle():
            running_game_servers_widget.windowHandle().setScreen(screen)

        x = screen_geometry.x() + 50
        y = screen_geometry.y() + 50

        running_game_servers_widget.move(x,y)

        app.widgets.append(running_game_servers_widget)



def get_screen_scale(screen):
    """
    Returns the scale factor for a screen.
    96 DPI = 1.0
    120 DPI = 1.25
    144 DPI = 1.5
    """
    return screen.logicalDotsPerInch() / 96.0



if __name__ == "__main__":
    main()

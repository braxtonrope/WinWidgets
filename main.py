import sys, os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication

from manager.widget_manager import WidgetManager

from widgets.time_widget import TimeWidget
from widgets.running_game_servers_widget import RunningGameServersWidget
from widgets.node_data_widget import NodeDataWidget
from services.amp_data_manager import AMPDataManager
from services.node_data_manager import NodeDataManager



app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

app.widgets = []

screens = QGuiApplication.screens()

# ONE shared AMP data manager
amp_manager = AMPDataManager()
node_manager = NodeDataManager()

def main():

    widget_manager = WidgetManager(padding=25, snap_distance=50)
    widget_manager.register_widget("time", TimeWidget)
    widget_manager.register_widget("node_data", NodeDataWidget)
    widget_manager.register_widget("game_servers", RunningGameServersWidget)

    time_widget = widget_manager.add_widget(
    "time"
    )

    node_widget = widget_manager.add_widget(
        "node_data",
        node_manager
    )

    server_widget = widget_manager.add_widget(
        "game_servers",
        amp_manager
    )

    sys.exit(app.exec())



def add_time_and_date_widgets():

    for screen in screens:
        screen_geometry = screen.availableGeometry()

        time_widget = TimeWidget()

        # Force calculation of true widget size
        time_widget.show()
        # time_widget.adjustSize()

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
        screen_geometry = screen.availableGeometry()

        running_game_servers_widget = RunningGameServersWidget(amp_manager)

        running_game_servers_widget.show()
        # running_game_servers_widget.adjustSize()

        if running_game_servers_widget.windowHandle():
            running_game_servers_widget.windowHandle().setScreen(screen)

        x = screen_geometry.x() + 50
        y = screen_geometry.y() + 50

        running_game_servers_widget.move(x,y)

        app.widgets.append(running_game_servers_widget)

def add_node_widget():
    for screen in screens:
        screen_geometry = screen.availableGeometry()

        node_widget = NodeDataWidget(node_manager)

        node_widget.show()

        if node_widget.windowHandle():
            node_widget.windowHandle().setScreen(screen)

        x = (
            screen_geometry.right()
            - node_widget.width()
            - int(50)
        )
        y = screen_geometry.top() + int(50)

        node_widget.move(x,y)

        app.widgets.append(node_widget)



if __name__ == "__main__":
    main()

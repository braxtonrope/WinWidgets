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

# ONE shared AMP data manager
amp_manager = AMPDataManager()
node_manager = NodeDataManager()

def main():

    widget_manager = WidgetManager(
        padding=25,
        snap_distance=50
    )

    # Register widget types
    widget_manager.register_widget(
        "time",
        lambda: TimeWidget()
    )

    widget_manager.register_widget(
        "node_data",
        lambda: NodeDataWidget(node_manager)
    )

    widget_manager.register_widget(
        "game_servers",
        lambda: RunningGameServersWidget(amp_manager)
    )

    # Load saved layout
    loaded = widget_manager.load_layout()

    # Create defaults if no saved layout exists
    if not loaded:

        time_widget = widget_manager.add_widget(
            "time",
            save=False
        )

        node_widget = widget_manager.add_widget(
            "node_data",
            save=False
        )

        server_widget = widget_manager.add_widget(
            "game_servers",
            save=False
        )

        # Set initial positions
        time_widget.move(50, 50)
        node_widget.move(50, 200)
        server_widget.move(400, 50)

        # Save the initial layout
        widget_manager.save_layout()

    sys.exit(app.exec())



if __name__ == "__main__":
    main()

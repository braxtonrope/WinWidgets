import sys, os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

from PySide6.QtWidgets import QApplication

from manager.widget_manager import WidgetManager
from widgets.time_widget import TimeWidget

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)


def main():

    widget_manager = WidgetManager(
        padding=25,
        snap_distance=50
    )

    # Shared managers - initially None
    amp_manager = None
    node_manager = None
    hardware_manager = None

    def get_amp_manager():
        nonlocal amp_manager

        if amp_manager is None:
            from services.amp_data_manager import AMPDataManager
            amp_manager = AMPDataManager()

        return amp_manager

    def get_node_manager():
        nonlocal node_manager

        if node_manager is None:
            from services.node_data_manager import NodeDataManager
            node_manager = NodeDataManager()

        return node_manager

    def get_hardware_manager():
        nonlocal hardware_manager

        if hardware_manager is None:
            from services.hardware_manager import HardwareManager
            hardware_manager = HardwareManager()

        return hardware_manager

    # Register all widget types
    widget_manager.register_widget(
        "time",
        lambda: TimeWidget()
    )

    widget_manager.register_widget(
        "game_servers",
        lambda: create_game_servers()
    )

    widget_manager.register_widget(
        "node_data",
        lambda: create_node_data()
    )

    widget_manager.register_widget(
        "system_stats",
        lambda: create_system_stats()
    )

    # Widget factories
    def create_game_servers():
        from widgets.running_game_servers_widget import RunningGameServersWidget
        return RunningGameServersWidget(get_amp_manager())

    def create_node_data():
        from widgets.node_data_widget import NodeDataWidget
        return NodeDataWidget(get_node_manager())

    def create_system_stats():
        from widgets.system_stats_widget import SystemStatsWidget
        return SystemStatsWidget(get_hardware_manager())

    # Load saved layout
    loaded = widget_manager.load_layout()

    if not loaded:
        time_widget = widget_manager.add_widget(
            "time",
            save=False
        )

        time_widget.move(50, 50)
        widget_manager.save_layout()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
import json
from pathlib import Path
import subprocess
import sys
import uuid

from PySide6.QtCore import QObject, QTimer
from PySide6.QtGui import QGuiApplication


class WidgetManager(QObject):

    def __init__(self, padding=15, snap_distance=20):
        super().__init__()

        self.widgets = []

        # Snapping configuration
        self.padding = padding
        self.snap_distance = snap_distance

        # Registered widget types
        self.widget_types = {}

        # Configuration file
        self.config_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "widgets.json"
        )

        self.commands_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "commands"
        )

        self.commands_path.mkdir(parents=True, exist_ok=True)

        # Check for GUI commands every 200ms
        self.command_timer = QTimer(self)
        self.command_timer.timeout.connect(self.process_commands)
        self.command_timer.start(200)

    # --------------------------------------------------
    # Widget registration
    # --------------------------------------------------

    def register_widget(self, name, widget_factory):
        """
        Register a widget type.

        Example:
            manager.register_widget("time", lambda: TimeWidget())
        """
        self.widget_types[name] = widget_factory

    # --------------------------------------------------
    # Adding and removing widgets
    # --------------------------------------------------

    def add_widget(self, widget_type, *args, save=True, **kwargs):

        if widget_type not in self.widget_types:
            raise ValueError(f"Unknown widget type: {widget_type}")

        widget_factory = self.widget_types[widget_type]

        widget = widget_factory(*args, **kwargs)

        widget._widget_type = widget_type
        widget._screen_name = None

        widget._widget_id = str(uuid.uuid4())

        self.widgets.append(widget)

        # Connect drag signals
        widget.drag_started.connect(self.start_drag)
        widget.dragging.connect(self.drag_widget)
        widget.drag_finished.connect(self.end_drag)
        widget.context_menu_requested.connect(self.open_widget_settings)

        widget.show()

        # Track its initial monitor
        self.update_widget_screen(widget)

        if save:
            self.save_layout()

        return widget

    def remove_widget(self, widget):

        if widget not in self.widgets:
            return

        self.widgets.remove(widget)

        widget.close()
        widget.deleteLater()

        self.save_layout()

    # --------------------------------------------------
    # Dragging
    # --------------------------------------------------

    def start_drag(self, widget):

        widget._manager_dragging = True

    def drag_widget(self, widget, position):

        if widget not in self.widgets:
            return

        # Move the widget to the mouse position
        widget.move(position)

        # Update its monitor
        self.update_widget_screen(widget)

        # Apply snapping
        self.snap_widget(widget)

    def end_drag(self, widget):

        if widget not in self.widgets:
            return

        # Final snapping
        self.snap_widget(widget)

        # Update monitor assignment after snapping
        self.update_widget_screen(widget)

        widget._manager_dragging = False

        self.save_layout()

    # --------------------------------------------------
    # Monitor tracking
    # --------------------------------------------------

    def get_widget_screen(self, widget):

        geometry = widget.frameGeometry()
        center = geometry.center()

        # First, check which screen contains the widget centre
        screen = QGuiApplication.screenAt(center)

        if screen is not None:
            return screen

        # If the centre is between monitors, find the screen
        # that overlaps the widget the most.
        best_screen = None
        best_area = 0

        for current_screen in QGuiApplication.screens():

            intersection = geometry.intersected(
                current_screen.availableGeometry()
            )

            area = intersection.width() * intersection.height()

            if area > best_area:
                best_area = area
                best_screen = current_screen

        if best_screen is not None:
            return best_screen

        # If the widget is completely outside all monitors,
        # retain its previous monitor if possible.
        previous_name = getattr(widget, "_screen_name", None)

        if previous_name:
            for current_screen in QGuiApplication.screens():
                if current_screen.name() == previous_name:
                    return current_screen

        return QGuiApplication.primaryScreen()

    def update_widget_screen(self, widget):

        screen = self.get_widget_screen(widget)

        if screen is None:
            return None

        widget._screen_name = screen.name()

        return screen

    # --------------------------------------------------
    # Snapping
    # --------------------------------------------------

    def snap_widget(self, widget):

        screen = self.get_widget_screen(widget)

        if screen is None:
            return

        geometry = widget.frameGeometry()

        x = geometry.x()
        y = geometry.y()

        width = geometry.width()
        height = geometry.height()

        screen_geometry = screen.availableGeometry()

        best_x = self.get_best_x_snap(
            widget,
            x,
            width,
            screen_geometry,
            screen
        )

        best_y = self.get_best_y_snap(
            widget,
            y,
            height,
            screen_geometry,
            screen
        )

        if best_x is not None:
            x = best_x

        if best_y is not None:
            y = best_y

        widget.move(x, y)

    # --------------------------------------------------
    # Horizontal snapping
    # --------------------------------------------------

    def get_best_x_snap(
        self,
        widget,
        x,
        width,
        screen_geometry,
        screen
    ):

        candidates = []

        left = screen_geometry.x()
        right = left + screen_geometry.width()

        # Screen left edge
        target = left + self.padding
        distance = abs(x - target)

        if distance <= self.snap_distance:
            candidates.append((distance, target))

        # Screen right edge
        target = right - width - self.padding
        distance = abs(x - target)

        if distance <= self.snap_distance:
            candidates.append((distance, target))

        # Screen horizontal centre
        screen_center = left + screen_geometry.width() / 2
        widget_center = x + width / 2

        distance = abs(widget_center - screen_center)

        if distance <= self.snap_distance:
            target = round(screen_center - width / 2)
            candidates.append((distance, target))

        # Snap against other widgets on the same screen
        for other in self.widgets:

            if other is widget:
                continue

            other_screen = self.get_widget_screen(other)

            if other_screen != screen:
                continue

            other_geometry = other.frameGeometry()

            other_x = other_geometry.x()
            other_width = other_geometry.width()

            other_right = other_x + other_width

            possible_positions = [
                # Align left edges
                other_x,

                # Align right edges
                other_right - width,

                # Place beside the other widget's right edge
                other_right + self.padding,

                # Place beside the other widget's left edge
                other_x - width - self.padding
            ]

            for target in possible_positions:

                distance = abs(x - target)

                if distance <= self.snap_distance:
                    candidates.append((distance, target))

        if not candidates:
            return None

        # Use the closest snapping position
        return min(candidates, key=lambda candidate: candidate[0])[1]

    # --------------------------------------------------
    # Vertical snapping
    # --------------------------------------------------

    def get_best_y_snap(
        self,
        widget,
        y,
        height,
        screen_geometry,
        screen
    ):

        candidates = []

        top = screen_geometry.y()
        bottom = top + screen_geometry.height()

        # Screen top edge
        target = top + self.padding
        distance = abs(y - target)

        if distance <= self.snap_distance:
            candidates.append((distance, target))

        # Screen bottom edge
        target = bottom - height - self.padding
        distance = abs(y - target)

        if distance <= self.snap_distance:
            candidates.append((distance, target))

        # Screen vertical centre
        screen_center = top + screen_geometry.height() / 2
        widget_center = y + height / 2

        distance = abs(widget_center - screen_center)

        if distance <= self.snap_distance:
            target = round(screen_center - height / 2)
            candidates.append((distance, target))

        # Snap against other widgets on the same screen
        for other in self.widgets:

            if other is widget:
                continue

            other_screen = self.get_widget_screen(other)

            if other_screen != screen:
                continue

            other_geometry = other.frameGeometry()

            other_y = other_geometry.y()
            other_height = other_geometry.height()

            other_bottom = other_y + other_height

            possible_positions = [
                # Align top edges
                other_y,

                # Align bottom edges
                other_bottom - height,

                # Place below the other widget
                other_bottom + self.padding,

                # Place above the other widget
                other_y - height - self.padding
            ]

            for target in possible_positions:

                distance = abs(y - target)

                if distance <= self.snap_distance:
                    candidates.append((distance, target))

        if not candidates:
            return None

        return min(candidates, key=lambda candidate: candidate[0])[1]

    # --------------------------------------------------
    # Saving configuration
    # --------------------------------------------------

    def save_layout(self):

        self.config_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        config = {
            "widgets": []
        }

        for widget in self.widgets:

            geometry = widget.frameGeometry()

            screen = self.update_widget_screen(widget)

            if screen is None:
                continue

            screen_geometry = screen.availableGeometry()

            widget_data = {
                "id": widget._widget_id,
                "type": widget._widget_type,

                # Store positions relative to the monitor
                "x": geometry.x() - screen_geometry.x(),
                "y": geometry.y() - screen_geometry.y(),

                "width": geometry.width(),
                "height": geometry.height(),

                # Remember the monitor
                "screen": screen.name()
            }

            config["widgets"].append(widget_data)

        # Write to a temporary file first to reduce
        # the risk of corrupting the configuration.
        temp_path = self.config_path.with_suffix(".tmp")

        try:

            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(config, file, indent=4)

            temp_path.replace(self.config_path)

        except OSError as error:

            print(f"Failed to save widget configuration: {error}")

    # --------------------------------------------------
    # Loading configuration
    # --------------------------------------------------

    def load_layout(self):

        if not self.config_path.exists():
            return False

        # Prevent loading duplicate widgets
        if self.widgets:
            print("Cannot load layout: widgets already exist.")
            return False

        try:

            with open(self.config_path, "r", encoding="utf-8") as file:
                config = json.load(file)

        except (OSError, json.JSONDecodeError) as error:

            print(f"Failed to load widget configuration: {error}")
            return False

        screens = QGuiApplication.screens()
        primary_screen = QGuiApplication.primaryScreen()

        if not screens or primary_screen is None:
            return False

        for widget_data in config.get("widgets", []):
            

            widget_type = widget_data.get("type")

            if widget_type not in self.widget_types:
                print(f"Unknown widget type: {widget_type}")
                continue

            # Find the monitor saved in the configuration
            saved_screen_name = widget_data.get("screen")

            screen = next(
                (
                    current_screen
                    for current_screen in screens
                    if current_screen.name() == saved_screen_name
                ),
                primary_screen
            )

            screen_geometry = screen.availableGeometry()

            # Create the widget without saving immediately
            widget = self.add_widget(
                widget_type,
                save=False
            )

            widget._widget_id = widget_data.get(
                "id",
                str(uuid.uuid4())
            )

            # Restore its size
            width = widget_data.get(
                "width",
                widget.width()
            )

            height = widget_data.get(
                "height",
                widget.height()
            )

            widget.resize(width, height)

            # Restore its position relative to its monitor
            x = screen_geometry.x() + widget_data.get("x", 0)
            y = screen_geometry.y() + widget_data.get("y", 0)

            # Keep the widget inside the monitor
            max_x = screen_geometry.x() + screen_geometry.width() - width
            max_y = screen_geometry.y() + screen_geometry.height() - height

            x = max(screen_geometry.x(), min(x, max_x))
            y = max(screen_geometry.y(), min(y, max_y))

            widget.move(x, y)

            widget._screen_name = screen.name()

        # Save the restored layout
        self.save_layout()

        return True

    def open_widget_settings(self, widget):
        print(f"Opening settings for {widget.windowTitle()}")

        gui_path = (
            Path(__file__).resolve().parent.parent
            / "gui"
            / "widget_gui.py"
        )

        subprocess.Popen(
            [sys.executable, str(gui_path)],
            cwd=str(gui_path.parent.parent)
        )

    def get_widgets(self):
        return self.widgets

    def process_commands(self):
        for command_file in self.commands_path.glob("*.json"):

            try:
                with open(command_file, "r", encoding="utf-8") as file:
                    command = json.load(file)

                action = command.get("action")

                if action == "add":
                    widget_type = command.get("type")

                    if widget_type in self.widget_types:
                        self.add_widget(widget_type)

                elif action == "remove":
                    widget_id = command.get("id")

                    widget = next(
                        (
                            w for w in self.widgets
                            if w._widget_id == widget_id
                        ),
                        None
                    )

                    if widget is not None:
                        self.remove_widget(widget)

                command_file.unlink(missing_ok=True)

            except Exception as error:
                print(f"Failed to process GUI command: {error}")
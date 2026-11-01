
from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication


class WidgetManager(QObject):

    def __init__(self, padding=15, snap_distance=20):
        super().__init__()

        self.widgets = []

        self.padding = padding
        self.snap_distance = snap_distance

        self.widget_types = {}

    # =========================================================
    # Widget registration
    # =========================================================

    def register_widget(self, name, widget_class):
        self.widget_types[name] = widget_class

    # =========================================================
    # Add / Remove widgets
    # =========================================================

    def add_widget(self, widget_type, *args, **kwargs):

        if widget_type not in self.widget_types:
            raise ValueError(
                f"Unknown widget type: {widget_type}"
            )

        widget_class = self.widget_types[widget_type]

        widget = widget_class(*args, **kwargs)

        self.widgets.append(widget)

        # Connect drag signals
        widget.drag_started.connect(
            self.start_drag
        )

        widget.dragging.connect(
            self.drag_widget
        )

        widget.drag_finished.connect(
            self.end_drag
        )

        widget.show()

        return widget

    def remove_widget(self, widget):

        if widget in self.widgets:
            self.widgets.remove(widget)

        widget.close()
        widget.deleteLater()

    # =========================================================
    # Dragging
    # =========================================================

    def start_drag(self, widget):

        widget._manager_dragging = True

    def drag_widget(self, widget, position):

        if widget not in self.widgets:
            return

        # Move to the requested mouse position
        widget.move(position)

        # Apply snapping
        self.snap_widget(widget)

    def end_drag(self, widget):

        if widget not in self.widgets:
            return

        self.snap_widget(widget)

        widget._manager_dragging = False

    # =========================================================
    # Main snapping function
    # =========================================================

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

        # Find best horizontal and vertical positions
        best_x = self.get_best_x_snap(
            widget,
            x,
            width,
            screen_geometry
        )

        best_y = self.get_best_y_snap(
            widget,
            y,
            height,
            screen_geometry
        )

        if best_x is not None:
            x = best_x

        if best_y is not None:
            y = best_y

        widget.move(x, y)

    # =========================================================
    # Horizontal snapping
    # =========================================================

    def get_best_x_snap(
        self,
        widget,
        x,
        width,
        screen_geometry
    ):

        candidates = []

        # -----------------------------------------------------
        # Screen left edge
        # -----------------------------------------------------

        target = screen_geometry.left() + self.padding

        distance = abs(x - target)

        if distance <= self.snap_distance:
            candidates.append((distance, target))

        # -----------------------------------------------------
        # Screen right edge
        # -----------------------------------------------------

        target = (
            screen_geometry.right()
            - width
            - self.padding
            + 1
        )

        distance = abs(x - target)

        if distance <= self.snap_distance:
            candidates.append((distance, target))

        # -----------------------------------------------------
        # Screen horizontal centre
        # -----------------------------------------------------

        screen_center = (
            screen_geometry.left()
            + screen_geometry.width() / 2
        )

        widget_center = x + width / 2

        distance = abs(
            widget_center - screen_center
        )

        if distance <= self.snap_distance:

            target = round(
                screen_center - width / 2
            )

            candidates.append((distance, target))

        # -----------------------------------------------------
        # Other widgets
        # -----------------------------------------------------

        for other in self.widgets:

            if other is widget:
                continue

            other_geometry = other.frameGeometry()

            other_x = other_geometry.x()
            other_width = other_geometry.width()

            other_right = (
                other_x + other_width
            )

            # ---------------------------------------------
            # Left edge to left edge
            # ---------------------------------------------

            target = other_x

            distance = abs(x - target)

            if distance <= self.snap_distance:
                candidates.append((distance, target))

            # ---------------------------------------------
            # Right edge to right edge
            # ---------------------------------------------

            target = other_right - width

            distance = abs(x - target)

            if distance <= self.snap_distance:
                candidates.append((distance, target))

            # ---------------------------------------------
            # Our left -> other right
            # ---------------------------------------------

            target = other_right + self.padding

            distance = abs(x - target)

            if distance <= self.snap_distance:
                candidates.append((distance, target))

            # ---------------------------------------------
            # Our right -> other left
            # ---------------------------------------------

            target = (
                other_x
                - width
                - self.padding
            )

            distance = abs(x - target)

            if distance <= self.snap_distance:
                candidates.append((distance, target))

        if not candidates:
            return None

        # Closest candidate wins
        candidates.sort(
            key=lambda candidate: candidate[0]
        )

        return candidates[0][1]

    # =========================================================
    # Vertical snapping
    # =========================================================

    def get_best_y_snap(
        self,
        widget,
        y,
        height,
        screen_geometry
    ):

        candidates = []

        # -----------------------------------------------------
        # Screen top edge
        # -----------------------------------------------------

        target = screen_geometry.top() + self.padding

        distance = abs(y - target)

        if distance <= self.snap_distance:
            candidates.append((distance, target))

        # -----------------------------------------------------
        # Screen bottom edge
        # -----------------------------------------------------

        target = (
            screen_geometry.bottom()
            - height
            - self.padding
            + 1
        )

        distance = abs(y - target)

        if distance <= self.snap_distance:
            candidates.append((distance, target))

        # -----------------------------------------------------
        # Screen vertical centre
        # -----------------------------------------------------

        screen_center = (
            screen_geometry.top()
            + screen_geometry.height() / 2
        )

        widget_center = y + height / 2

        distance = abs(
            widget_center - screen_center
        )

        if distance <= self.snap_distance:

            target = round(
                screen_center - height / 2
            )

            candidates.append((distance, target))

        # -----------------------------------------------------
        # Other widgets
        # -----------------------------------------------------

        for other in self.widgets:

            if other is widget:
                continue

            other_geometry = other.frameGeometry()

            other_y = other_geometry.y()
            other_height = other_geometry.height()

            other_bottom = (
                other_y + other_height
            )

            # ---------------------------------------------
            # Top edge to top edge
            # ---------------------------------------------

            target = other_y

            distance = abs(y - target)

            if distance <= self.snap_distance:
                candidates.append((distance, target))

            # ---------------------------------------------
            # Bottom edge to bottom edge
            # ---------------------------------------------

            target = other_bottom - height

            distance = abs(y - target)

            if distance <= self.snap_distance:
                candidates.append((distance, target))

            # ---------------------------------------------
            # Our top -> other bottom
            # ---------------------------------------------

            target = other_bottom + self.padding

            distance = abs(y - target)

            if distance <= self.snap_distance:
                candidates.append((distance, target))

            # ---------------------------------------------
            # Our bottom -> other top
            # ---------------------------------------------

            target = (
                other_y
                - height
                - self.padding
            )

            distance = abs(y - target)

            if distance <= self.snap_distance:
                candidates.append((distance, target))

        if not candidates:
            return None

        # Closest candidate wins
        candidates.sort(
            key=lambda candidate: candidate[0]
        )

        return candidates[0][1]

    # =========================================================
    # Monitor detection
    # =========================================================

    def get_widget_screen(self, widget):

        center = widget.frameGeometry().center()

        for screen in QGuiApplication.screens():

            if screen.availableGeometry().contains(center):
                return screen

        return None

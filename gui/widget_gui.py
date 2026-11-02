
import customtkinter as ctk

import json
import uuid
from pathlib import Path


class WidgetGUI(ctk.CTk):

    def __init__(self):

        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("WinWidgets Settings")
        self.geometry("800x600")
        self.minsize(650, 450)

        self.data_path = (
            Path(__file__).resolve().parent.parent / "data"
        )

        self.config_path = self.data_path / "widgets.json"
        self.commands_path = self.data_path / "commands"

        self.commands_path.mkdir(parents=True, exist_ok=True)

        self.widget_options = {
            "Time and Date": "time",
            "AMP Manager": "game_servers",
            "Node Data": "node_data"
        }

        self.widget_names = {
            "time": "Time and Date",
            "game_servers": "AMP Manager",
            "node_data": "Node Data"
        }

        self.create_layout()
        self.refresh_widgets()

        # Automatically refresh the active widget list
        self.after(1000, self.auto_refresh)

    def create_layout(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        content = ctk.CTkFrame(self, corner_radius=10)
        content.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="nsew"
        )

        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)

        # Header
        ctk.CTkLabel(
            content,
            text="Widget Manager",
            font=("Arial", 24, "bold")
        ).grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="w"
        )

        # Add widget section
        add_frame = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        add_frame.grid(
            row=1,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

        self.widget_dropdown = ctk.CTkComboBox(
            add_frame,
            values=list(self.widget_options.keys()),
            state="readonly",
            width=250
        )
        self.widget_dropdown.pack(side="left", padx=(0, 10))
        self.widget_dropdown.set("Time and Date")

        ctk.CTkButton(
            add_frame,
            text="Add Widget",
            command=self.add_widget
        ).pack(side="left")

        # Active widgets header
        widgets_header = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        widgets_header.grid(
            row=2,
            column=0,
            padx=20,
            pady=(10, 5),
            sticky="new"
        )

        ctk.CTkLabel(
            widgets_header,
            text="Active Widgets",
            font=("Arial", 18, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            widgets_header,
            text="Refresh",
            width=80,
            command=self.refresh_widgets
        ).pack(side="right")

        self.widget_list = ctk.CTkScrollableFrame(content)
        self.widget_list.grid(
            row=3,
            column=0,
            padx=20,
            pady=10,
            sticky="nsew"
        )

        content.grid_rowconfigure(3, weight=1)

    def send_command(self, command):

        command_id = str(uuid.uuid4())

        command_file = self.commands_path / f"{command_id}.json"
        temp_file = command_file.with_suffix(".tmp")

        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(command, file)

        temp_file.replace(command_file)

    def add_widget(self):

        selected = self.widget_dropdown.get()
        widget_type = self.widget_options.get(selected)

        if widget_type is None:
            return

        self.send_command({
            "action": "add",
            "type": widget_type
        })

    def remove_widget(self, widget_id):

        self.send_command({
            "action": "remove",
            "id": widget_id
        })

    def refresh_widgets(self):

        for child in self.widget_list.winfo_children():
            child.destroy()

        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                config = json.load(file)

        except (OSError, json.JSONDecodeError):
            config = {"widgets": []}

        widgets = config.get("widgets", [])

        if not widgets:
            ctk.CTkLabel(
                self.widget_list,
                text="No active widgets."
            ).pack(pady=20)
            return

        for widget in widgets:

            widget_id = widget.get("id")
            widget_type = widget.get("type")

            widget_name = self.widget_names.get(
                widget_type,
                widget_type
            )

            row = ctk.CTkFrame(self.widget_list)
            row.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(
                row,
                text=widget_name,
                font=("Arial", 14)
            ).pack(side="left", padx=15, pady=12)

            ctk.CTkButton(
                row,
                text="Remove",
                fg_color="#B83232",
                hover_color="#8F2424",
                width=90,
                command=lambda wid=widget_id: self.remove_widget(wid)
            ).pack(side="right", padx=10, pady=8)

    def auto_refresh(self):

        if self.winfo_exists():
            self.refresh_widgets()
            self.after(1000, self.auto_refresh)


if __name__ == "__main__":
    app = WidgetGUI()
    app.mainloop()

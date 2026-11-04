
import customtkinter as ctk

import json
import uuid
import threading
import requests
import os
import sys
import subprocess
import tempfile

from pathlib import Path


# --------------------------------------------------
# UPDATE CONFIGURATION
# --------------------------------------------------

CURRENT_VERSION = "v1.0.0"
GITHUB_REPO = "braxtonrope/WinWidgets"


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

        # Updater variables
        self.download_url = None
        self.file_name = None
        self.update_dir = None

        # Create interface
        self.create_layout()
        self.updater()

        self.refresh_widgets()

        # Automatically refresh active widgets
        self.after(1000, self.auto_refresh)

    # --------------------------------------------------
    # MAIN GUI
    # --------------------------------------------------

    def create_layout(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        content = ctk.CTkFrame(self, corner_radius=10)

        content.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 10),
            sticky="nsew"
        )

        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(3, weight=1)

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

        # Widget list
        self.widget_list = ctk.CTkScrollableFrame(content)

        self.widget_list.grid(
            row=3,
            column=0,
            padx=20,
            pady=10,
            sticky="nsew"
        )

    # --------------------------------------------------
    # WIDGET MANAGEMENT
    # --------------------------------------------------

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

    # --------------------------------------------------
    # UPDATER GUI
    # --------------------------------------------------

    def updater(self):

        update_frame = ctk.CTkFrame(self, corner_radius=10)

        update_frame.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 20),
            sticky="ew"
        )

        self.version_label = ctk.CTkLabel(
            update_frame,
            text=f"Current Version: {CURRENT_VERSION}"
        )

        self.version_label.pack(pady=(10, 5))

        self.status_label = ctk.CTkLabel(
            update_frame,
            text="Ready to check for updates."
        )

        self.status_label.pack(pady=5)

        self.update_button = ctk.CTkButton(
            update_frame,
            text="Check for Updates",
            command=self.check_for_updates
        )

        self.update_button.pack(pady=5)

        self.download_button = ctk.CTkButton(
            update_frame,
            text="Download & Install Update",
            command=self.start_download,
            fg_color="#2CC985",
            hover_color="#208B5C"
        )

        self.progress_bar = ctk.CTkProgressBar(
            update_frame,
            width=300
        )

        self.progress_bar.set(0)

    # --------------------------------------------------
    # CHECK FOR UPDATES
    # --------------------------------------------------

    def check_for_updates(self):

        self.status_label.configure(
            text="Checking for updates...",
            text_color="white"
        )

        self.update_button.configure(state="disabled")

        threading.Thread(
            target=self.fetch_update_from_github,
            daemon=True
        ).start()

    def fetch_update_from_github(self):

        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

        try:

            response = requests.get(
                url,
                timeout=10,
                headers={
                    "Accept": "application/vnd.github+json"
                }
            )

            response.raise_for_status()

            data = response.json()

            latest_version = data.get("tag_name")

            if not latest_version:
                raise ValueError("GitHub release has no version tag.")

            # Check version
            if latest_version == CURRENT_VERSION:

                self.after(
                    0,
                    lambda: self.status_label.configure(
                        text="You are running the latest version.",
                        text_color="gray"
                    )
                )

                return

            # Find executable
            assets = data.get("assets", [])

            executable = next(
                (
                    asset for asset in assets
                    if asset.get("name", "").lower().endswith(".exe")
                ),
                None
            )

            if executable is None:

                self.after(
                    0,
                    lambda: self.status_label.configure(
                        text="Update found, but no executable was attached.",
                        text_color="orange"
                    )
                )

                return

            self.download_url = executable["browser_download_url"]
            self.file_name = Path(executable["name"]).name

            def show_update():

                self.status_label.configure(
                    text=f"New version available: {latest_version}",
                    text_color="#00FF00"
                )

                self.download_button.pack(pady=5)

            self.after(0, show_update)

        except Exception as e:

            print(f"Update check error: {e}")

            self.after(
                0,
                lambda: self.status_label.configure(
                    text="Failed to check for updates.",
                    text_color="red"
                )
            )

        finally:

            self.after(
                0,
                lambda: self.update_button.configure(state="normal")
            )

    # --------------------------------------------------
    # DOWNLOAD UPDATE
    # --------------------------------------------------

    def start_download(self):

        if not self.download_url or not self.file_name:
            return

        self.download_button.pack_forget()

        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.status_label.configure(
            text="Downloading update...",
            text_color="white"
        )

        self.update_button.configure(state="disabled")

        threading.Thread(
            target=self.download_and_run,
            daemon=True
        ).start()

    def download_and_run(self):

        update_dir = None

        try:

            # Only packaged executables can be replaced
            if not getattr(sys, "frozen", False):
                raise RuntimeError(
                    "Updates require the packaged WinWidgets executable."
                )

            if os.name != "nt":
                raise RuntimeError("Updater only supports Windows.")

            # Create temporary directory
            update_dir = Path(
                tempfile.mkdtemp(prefix="WinWidgets_Update_")
            )

            download_path = update_dir / self.file_name

            # Download
            with requests.get(
                self.download_url,
                stream=True,
                timeout=(5, 60)
            ) as response:

                response.raise_for_status()

                total_length = int(
                    response.headers.get("content-length", 0)
                )

                downloaded = 0

                with open(download_path, "wb") as file:

                    for chunk in response.iter_content(chunk_size=8192):

                        if not chunk:
                            continue

                        file.write(chunk)
                        downloaded += len(chunk)

                        if total_length:

                            progress = downloaded / total_length

                            self.after(
                                0,
                                lambda p=progress: self.progress_bar.set(p)
                            )

            # Validate download
            if not download_path.exists() or download_path.stat().st_size == 0:
                raise ValueError("Downloaded executable is empty.")

            if download_path.suffix.lower() != ".exe":
                raise ValueError("Downloaded file is not an executable.")

            # Schedule installation on GUI thread
            self.after(
                0,
                lambda: self.install_update(download_path, update_dir)
            )

        except Exception as e:

            print(f"Download error: {e}")

            if update_dir and update_dir.exists():
                import shutil
                shutil.rmtree(update_dir, ignore_errors=True)

            self.after(
                0,
                lambda: self.status_label.configure(
                    text="Download failed. Check console for details.",
                    text_color="red"
                )
            )

            self.after(
                0,
                lambda: self.update_button.configure(state="normal")
            )

    # --------------------------------------------------
    # INSTALL UPDATE
    # --------------------------------------------------

    def install_update(self, download_path, update_dir):

        try:

            if not getattr(sys, "frozen", False):
                raise RuntimeError("Application is not packaged.")

            current_exe = Path(sys.executable).resolve()

            # Ensure the existing executable is writable
            if not os.access(current_exe.parent, os.W_OK):
                raise PermissionError(
                    "Cannot write to the application directory. "
                    "Install WinWidgets in a user-writable folder."
                )

            script_path = update_dir / "installer.ps1"

            # Escape PowerShell paths
            target = str(current_exe).replace("'", "''")
            update = str(download_path.resolve()).replace("'", "''")
            update_folder = str(update_dir.resolve()).replace("'", "''")

            app_pid = os.getpid()

            script = f"""
$ErrorActionPreference = 'Stop'

$Target = '{target}'
$Update = '{update}'
$UpdateFolder = '{update_folder}'
$AppPID = {app_pid}

try {{

    # Wait for current WinWidgets process to close
    while (Get-Process -Id $AppPID -ErrorAction SilentlyContinue) {{
        Start-Sleep -Milliseconds 500
    }}

    # Prepare replacement
    $NewTarget = "$Target.new"

    # Copy new executable next to original
    Copy-Item -LiteralPath $Update -Destination $NewTarget -Force

    # Replace existing executable
    Move-Item -LiteralPath $NewTarget -Destination $Target -Force

    # Launch updated WinWidgets
    Start-Process -FilePath $Target

    # Clean up temporary files
    Start-Sleep -Seconds 3

    Remove-Item -LiteralPath $UpdateFolder -Recurse -Force -ErrorAction SilentlyContinue

}}
catch {{

    Write-Error $_

    # Remove incomplete replacement
    Remove-Item -LiteralPath "$Target.new" -Force -ErrorAction SilentlyContinue

    # Preserve the downloaded update for manual recovery
}}
"""

            script_path.write_text(
                script,
                encoding="utf-8"
            )

            self.status_label.configure(
                text="Installing update...",
                text_color="#00FF00"
            )

            # Launch separate PowerShell process
            subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script_path)
                ],
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # Close current application
            self.after(500, self.destroy)

        except Exception as e:

            print(f"Installation error: {e}")

            self.status_label.configure(
                text="Failed to start installer.",
                text_color="red"
            )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    app = WidgetGUI()
    app.mainloop()

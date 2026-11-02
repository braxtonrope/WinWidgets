
import os
import re
import socket

import paramiko

from dotenv import load_dotenv, find_dotenv

from PySide6.QtCore import QObject, QTimer, Signal, QThread


load_dotenv(find_dotenv())


# --------------------------------------------------
# Configuration
# --------------------------------------------------

NUM_NODES = int(os.getenv("NUM_NODES", "0"))

SSH_USERNAME = os.getenv("SSH_USERNAME")

# Prefer a separate SSH_PASSWORD variable.
# Falls back to your existing SUDO_PASSWORD variable.
SSH_PASSWORD = (
    os.getenv("SSH_PASSWORD")
    or os.getenv("SUDO_PASSWORD")
)


# --------------------------------------------------
# Node monitoring worker
# --------------------------------------------------

class NodeMonitorThread(QThread):

    data_updated = Signal(list)

    def __init__(self):
        super().__init__()

    def run(self):

        node_data = []

        for i in range(1, NUM_NODES + 1):

            node_name = os.getenv(f"NODE{i}_DNS_NAME")
            node_ip = os.getenv(f"NODE{i}_IP")

            data = self.get_node_data(
                node_name,
                node_ip
            )

            node_data.append(data)

        self.data_updated.emit(node_data)

    # ----------------------------------------------
    # Connect to node and collect information
    # ----------------------------------------------

    def get_node_data(self, node_name, node_ip):

        data = {
            "node_name": node_name or f"Node",
            "node_ip": node_ip,
            "status": "offline",
            "cpu_usage": None,
            "cpu_temp": None,
            "ram_free": None,
            "disk_free": None,
            "error": None,
            "metric_errors": []
        }

        if not node_ip or not SSH_USERNAME or not SSH_PASSWORD:
            data["status"] = "configuration_error"
            data["error"] = "Missing node IP or SSH credentials"
            return data

        client = paramiko.SSHClient()

        # Automatically accept unknown host keys.
        # For stronger security, use a managed known_hosts file.
        client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )

        try:

            # Connect to node
            client.connect(
                hostname=node_ip,
                username=SSH_USERNAME,
                password=SSH_PASSWORD,
                timeout=5,
                banner_timeout=5,
                auth_timeout=5,
                allow_agent=False,
                look_for_keys=False
            )

            data["status"] = "online"

            # Collect metrics independently
            metrics = {
                "cpu_temp": self.get_temp,
                "cpu_usage": self.get_cpu_usage,
                "ram_free": self.get_ram_free,
                "disk_free": self.get_disk_free
            }

            for metric_name, metric_function in metrics.items():

                try:
                    data[metric_name] = metric_function(client)

                except Exception as e:

                    data["metric_errors"].append(
                        f"{metric_name}: {str(e)}"
                    )

            if data["metric_errors"]:
                data["error"] = "; ".join(
                    data["metric_errors"]
                )

        except (paramiko.SSHException, socket.timeout, OSError) as e:

            data["status"] = "offline"
            data["error"] = str(e) or "SSH connection failed"

        except Exception as e:

            data["status"] = "error"
            data["error"] = str(e)

        finally:

            client.close()

        return data

    # ----------------------------------------------
    # Execute SSH command safely
    # ----------------------------------------------

    def run_command(self, client, command):

        stdin, stdout, stderr = client.exec_command(
            command,
            timeout=8
        )

        output = stdout.read().decode(
            "utf-8",
            errors="replace"
        ).strip()

        error = stderr.read().decode(
            "utf-8",
            errors="replace"
        ).strip()

        exit_code = stdout.channel.recv_exit_status()

        if exit_code != 0:
            raise RuntimeError(
                error or f"Command exited with code {exit_code}"
            )

        if not output:
            raise RuntimeError("Command returned empty output")

        return output

    # ----------------------------------------------
    # CPU temperature
    # ----------------------------------------------

    def get_temp(self, client):

        output = self.run_command(
            client,
            "sensors"
        )

        match = re.search(
            r"Package id 0:\s*\+?([\d.]+)°C",
            output
        )

        if not match:
            raise ValueError("CPU temperature not found")

        return f"{float(match.group(1)):.1f}°C"

    # ----------------------------------------------
    # CPU usage
    # ----------------------------------------------

    def get_cpu_usage(self, client):

        output = self.run_command(
            client,
            "LC_ALL=C top -bn1"
        )

        match = re.search(
            r"%Cpu\(s\):.*?([\d.]+)\s*id",
            output
        )

        if not match:
            raise ValueError("CPU usage not found")

        idle = float(match.group(1))

        return f"{round(100 - idle, 1)}%"

    # ----------------------------------------------
    # Available RAM
    # ----------------------------------------------

    def get_ram_free(self, client):

        output = self.run_command(
            client,
            "free -m"
        )

        for line in output.splitlines():

            if line.startswith("Mem:"):

                values = line.split()

                # Available memory is the final value
                # in standard Linux free output.
                ram_available_mb = int(values[6])

                ram_available_gb = ram_available_mb / 1024

                return f"{ram_available_gb:.1f} GiB"

        raise ValueError("RAM information not found")

    # ----------------------------------------------
    # Disk free space
    # ----------------------------------------------

    def get_disk_free(self, client):

        output = self.run_command(
            client,
            "df -BG --output=avail /"
        )

        lines = output.splitlines()

        if len(lines) < 2:
            raise ValueError("Disk information not found")

        match = re.search(
            r"([\d]+)G",
            lines[1].strip()
        )

        if not match:
            raise ValueError("Could not parse disk space")

        return f"{int(match.group(1))} GB"


# --------------------------------------------------
# Node data manager
# --------------------------------------------------

class NodeDataManager(QObject):

    data_updated = Signal(list)

    def __init__(self):
        super().__init__()

        self.node_data = []

        self.monitor_thread = None

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(10_000)

        # Initial collection
        self.refresh()

    def refresh(self):

        # Prevent overlapping monitoring threads
        if self.monitor_thread is not None:
            return

        self.monitor_thread = NodeMonitorThread()

        self.monitor_thread.data_updated.connect(
            self.update_node_data
        )

        self.monitor_thread.finished.connect(
            self.monitor_finished
        )

        self.monitor_thread.start()

    def update_node_data(self, data):

        self.node_data = data

        self.data_updated.emit(data)

    def monitor_finished(self):

        thread = self.monitor_thread
        self.monitor_thread = None

        if thread is not None:
            thread.deleteLater()

    def get_data(self):
        return self.node_data

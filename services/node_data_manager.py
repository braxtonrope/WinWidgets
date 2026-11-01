from PySide6.QtCore import QObject, QTimer, Signal

from dotenv import load_dotenv, find_dotenv
import os
import paramiko
import re

load_dotenv(find_dotenv())

NUM_NODES = os.getenv("NUM_NODES")
SSH_USERNAME = os.getenv("SSH_USERNAME")
SUDO_PASSWORD = os.getenv("SUDO_PASSWORD")

class NodeDataManager(QObject):
    data_updated = Signal(list)

    def __init__(self):
        super().__init__()

        self.node_data = []
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(5_000)

        # Get initial data immediately.
        self.refresh()


    def refresh(self):
        try:
            self.node_data = self.get_all_data()

            # Notifiy widgets of updated data
            self.data_updated.emit(self.node_data)

        except Exception as e:
            print(f"Failed to update Node data: {e}")

    def get_all_data(self):
        node_data = []
        for i in range(1, int (NUM_NODES)+1):
            try:
                host = os.getenv(f"NODE{i}_IP")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(host, username=SSH_USERNAME, password=SUDO_PASSWORD)

                node_name = os.getenv(f"NODE{i}_DNS_NAME")
                node_ip = os.getenv(f"NODE{i}_IP")
                cpu_temp = self.get_temp(client)
                cpu_usage = self.get_cpu_usage(client)
                ram_free = self.get_ram_free(client)
                disk_free = self.get_disk_free(client)

                data = {"node_name": node_name, "node_ip": node_ip, "cpu_usage":cpu_usage, "cpu_temp":cpu_temp, "ram_free":ram_free, "disk_free":disk_free}
                node_data.append(data)

            finally:
                client.close()
        return node_data

    def get_temp(self, client):
        stdin, stdout, stderr = client.exec_command("sensors")
        output = stdout.read().decode()

        match = re.search(r"Package id 0:\s+\+([\d.]+)°C", output)

        if match:
            return f"{float(match.group(1))}°C"


    def get_cpu_usage(self, client):
        stdin, stdout, stderr = client.exec_command("top -bn1")
        output = stdout.read().decode()

        match = re.search(r"%Cpu\(s\):.*?([\d.]+)\s+id", output)

        if match:
            return f"{round(100 - float(match.group(1)), 1)}%"

    def get_ram_free(self, client):
        stdin, stdout, stderr = client.exec_command("free -m")
        output = stdout.read().decode()

        for line in output.splitlines():
            if line.startswith("Mem:"):
                values = line.split()
                ram_in_mb = int(values[6])
                ram_in_gb = ram_in_mb / 1000
                return f"{ram_in_gb:.1f} GiB"

    def get_disk_free(self, client):
        stdin, stdout, stderr = client.exec_command("df -h")
        output = stdout.read().decode()
        available_space = 0 # Stored in MB

        for line in output.splitlines():
            if not line.startswith("Filesystem"):
                values = line.split()
                string = values[3]

                match string[-1]:
                    case "M":
                        available_space += float(string[:-1]) / 1000
                    case "K":
                        available_space += float(string[:-1]) / (1024 ** 2)
                    case "G":
                        available_space += float(string[:-1])
                
        return f"{round(available_space)} GB" # Converts to GB

    def get_data(self):
        return self.node_data
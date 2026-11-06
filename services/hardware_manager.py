import ctypes
import subprocess
import time
import sys, os

from pathlib import Path
from ctypes import wintypes

import psutil

from PySide6.QtCore import QObject, QTimer, Signal, QThread


class CoreTempSharedDataEx(ctypes.Structure):

    _pack_ = 4

    _fields_ = [
        ("uiLoad", ctypes.c_uint32 * 256),
        ("uiTjMax", ctypes.c_uint32 * 128),
        ("uiCoreCnt", ctypes.c_uint32),
        ("uiCPUCnt", ctypes.c_uint32),
        ("fTemp", ctypes.c_float * 256),
        ("fVID", ctypes.c_float),
        ("fCPUSpeed", ctypes.c_float),
        ("fFSBSpeed", ctypes.c_float),
        ("fMultiplier", ctypes.c_float),
        ("sCPUName", ctypes.c_char * 100),
        ("ucFahrenheit", ctypes.c_uint8),
        ("ucDeltaToTjMax", ctypes.c_uint8),
        ("ucTdpSupported", ctypes.c_uint8),
        ("ucPowerSupported", ctypes.c_uint8),
        ("uiStructVersion", ctypes.c_uint32),
        ("uiTdp", ctypes.c_uint32 * 128),
        ("fPower", ctypes.c_float * 128),
        ("fMultipliers", ctypes.c_float * 256),
    ]


class CoreTempManager:

    def __init__(self, core_temp_path):

        self.core_temp_path = Path(core_temp_path)
        self.process = None
        self.started_by_us = False

        self.kernel32 = ctypes.WinDLL(
            "kernel32",
            use_last_error=True
        )

        self.kernel32.OpenFileMappingW.restype = wintypes.HANDLE
        self.kernel32.OpenFileMappingW.argtypes = [
            wintypes.DWORD,
            wintypes.BOOL,
            wintypes.LPCWSTR
        ]

        self.kernel32.MapViewOfFile.restype = ctypes.c_void_p
        self.kernel32.MapViewOfFile.argtypes = [
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.c_size_t
        ]

        self.kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

    def start(self):
        if not ctypes.windll.shell32.IsUserAnAdmin():
            self.request_admin()

        if not self.core_temp_path.is_file():
            raise FileNotFoundError(self.core_temp_path)

        for proc in psutil.process_iter(["name"]):

            try:
                if proc.info["name"].lower() == "core temp.exe":
                    return

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0

        self.process = subprocess.Popen(
            [str(self.core_temp_path)],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        self.started_by_us = True

        time.sleep(2)

    def read(self):

        FILE_MAP_READ = 0x0004

        handle = self.kernel32.OpenFileMappingW(
            FILE_MAP_READ,
            False,
            "CoreTempMappingObjectEx"
        )

        if not handle:
            return "N/A"
            # raise RuntimeError("Could not open Core Temp shared memory")

        address = self.kernel32.MapViewOfFile(
            handle,
            FILE_MAP_READ,
            0,
            0,
            ctypes.sizeof(CoreTempSharedDataEx)
        )

        if not address:
            self.kernel32.CloseHandle(handle)
            raise RuntimeError("Could not map Core Temp memory")

        try:

            data = ctypes.cast(
                address,
                ctypes.POINTER(CoreTempSharedDataEx)
            ).contents

            core_count = min(data.uiCoreCnt, 256)

            temperatures = [
                data.fTemp[i] - 32 if data.ucFahrenheit
                else data.fTemp[i]
                for i in range(core_count)
            ]

            if data.ucDeltaToTjMax:
                tjmax = data.uiTjMax[0]
                temperatures = [
                    tjmax - temp for temp in temperatures
                ]

            if not temperatures:
                return "N/A"
            
            return temperatures

        finally:
            self.kernel32.UnmapViewOfFile(address)
            self.kernel32.CloseHandle(handle)

    def getCPUTemp(self):
        
        temperatures = self.read()

        if temperatures == "N/A":
            return "N/A"

        return round(max(temperatures), 1)

    def stop(self):

        if self.started_by_us and self.process:

            if self.process.poll() is None:
                self.process.terminate()
                self.process.wait(timeout=5)

            self.process = None
            self.started_by_us = False

    def request_admin(self):
        script = os.path.abspath(sys.argv[0])
        params = subprocess.list2cmdline([script] + sys.argv[1:])

        hinstance = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            params,
            None,
            0 # Hides the terminal window
        )

class HardwareManager(QObject):

    data_updated = Signal(object)
    
    def __init__(self):
        super().__init__()

        self.core_temp_manager = CoreTempManager(core_temp_path=r"C:\Program Files\Core Temp\Core Temp.exe")

        try:
            self.core_temp_manager.start()
        except Exception as e:
            print("Admin required...")

        self.data = {}

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(3_000)

        # Initial collection
        self.refresh_data()

    def refresh_data(self):
        cpu_temp = self.get_cpu_temp()
        cpu_usage = self.get_cpu_usage()
        ram_usage = self.get_ram_usage()

        self.data = {"cpu_temp": cpu_temp, "cpu_usage": cpu_usage, "ram_usage": ram_usage}
        self.data_updated.emit(self.data)

    def get_data(self):
        return self.data

    def get_cpu_temp(self):
        return self.core_temp_manager.getCPUTemp()

    def get_cpu_usage(self):
        return psutil.cpu_percent()

    def get_ram_usage(self):
        return psutil.virtual_memory().percent

    def get_network_usage(self):
        return psutil.net_io_counters()

    def stop(self):
        self.core_temp_manager.stop()


    
import win32gui
import win32process
import win32api
import win32com.client as win32client
import win32con
import datetime
import os
import time

from logger.logger import Logger


class Win32ProcessLogger(Logger):
    def __init__(self, target_freq=None):
        self.wmi = win32client.GetObject("winmgmts:")
        self.id_history = []

        children = self.wmi.ExecQuery("Select * from Win32_NetworkAdapter")
        for child in children:
            if child.MACAddress is not None:
                self.mac = child.MACAddress

        self.iteration_count = 0
        os.makedirs("logs", exist_ok=True)

        self.out_file = open(os.path.join("logs", self.mac.replace(":", "-") + ".json"), "w+")
        self.target_freq = target_freq

    def __window_callback(self, hwnd, hwnds):
        process_info = {"iter_id": self.iteration_count, "timestamp": datetime.datetime.now().isoformat()}

        thread_process_id = win32process.GetWindowThreadProcessId(hwnd)
        process_info["process_id"] = thread_process_id[1]
        process_info["thread_id"] = thread_process_id[0]

        if str(process_info["process_id"]) + "-" + str(process_info["thread_id"]) in self.id_history:
            return

        self.id_history.append(
            str(process_info["process_id"]) + "-" + str(process_info["thread_id"]))

        children = self.wmi.ExecQuery("Select * from win32_process "
                                      "where ProcessId=" + str(process_info["process_id"]))
        for child in children:
            process_info["process_name"] = child.Name
            process_info["exec_path"] = child.ExecutablePath
            process_info["cmd"] = child.CommandLine
            process_info["creation_time"] = child.CreationDate
            process_info["state"] = child.ExecutionState

        process_info["window_title"] = win32gui.GetWindowText(hwnd)

        is_foreground = \
            win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow()) == thread_process_id

        process_info["foreground"] = is_foreground
        try:
            h_proc = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, process_info["process_id"])
            process_times = win32process.GetProcessTimes(h_proc)
            process_info["user_time"] = process_times["UserTime"] * 100 / (10 ** 6)
            process_info["memory"] = win32process.GetProcessMemoryInfo(h_proc)
            process_info["io_counter"] = win32process.GetProcessIoCounters(h_proc)
        except Exception:
            pass

        self.out_file.write(str(process_info) + "\n")

    def log(self):
        freq = 0
        target_period = None

        if self.target_freq is not None:
            target_period = 1 / self.target_freq

        while True:
            start = time.time()

            print("\rLogging freq: " + str(freq) + " Hz", end="")

            hwnds = []
            self.id_history = []

            win32gui.EnumWindows(self.__window_callback, hwnds)

            self.iteration_count += 1
            self.out_file.flush()

            period = time.time() - start

            if target_period is not None:
                time.sleep(max(target_period - period, 0))

            freq = 1 / (time.time() - start)

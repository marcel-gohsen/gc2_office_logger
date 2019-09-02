import win32gui
import win32process
import win32api
import win32com.client as win32client
import win32con
import datetime
import os
import time
import wmi
import psutil
import json

from logger.logger import Logger


class Win32ProcessLogger(Logger):
    def __init__(self, target_freq=None):
        # self.c = wmi.WMI()

        self.wmi = win32client.GetObject("winmgmts:")
        self.id_history = []

        children = self.wmi.ExecQuery("Select * from Win32_NetworkAdapter")
        for child in children:
            if child.MACAddress is not None:
                self.mac = child.MACAddress

        self.__save_hw_info()

        # self.iteration_count = 0
        # os.makedirs("logs", exist_ok=True)
        os.makedirs(os.path.join("logs", self.mac.replace(":", "-")), exist_ok=True)

        out_path = os.path.join("logs", self.mac.replace(":", "-"), datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".json")
        self.out_file = open(out_path, "w+")
        self.target_freq = target_freq

    def __save_hw_info(self):
        hw_info = {}
        hw_info["cpu"] = {}
        hw_info["memory"] = []
        hw_info["disks"] = []
        hw_info["gpu"] = []

        children = self.wmi.ExecQuery("Select * from Win32_Processor")
        for child in children:
            hw_info["cpu"]["name"] = child.Name
            hw_info["cpu"]["vendor"] = child.Manufacturer
            hw_info["cpu"]["max_clock"] = child.MaxClockSpeed
            hw_info["cpu"]["num_cores"] = child.NumberOfCores

        children = self.wmi.ExecQuery("Select * from Win32_PhysicalMemory")
        for child in children:
            mem_info = {}
            mem_info["name"] = child.Name

            hw_info["memory"].append(mem_info)

        children = self.wmi.ExecQuery("Select * from Win32_DiskDrive")
        for child in children:
            mem_info = {}
            mem_info["name"] = child.Name
            mem_info["vendor"] = child.Manufacturer
            mem_info["size"] = child.Size

            hw_info["disks"].append(mem_info)

        children = self.wmi.ExecQuery("Select * from Win32_VideoController")
        for child in children:
            mem_info = {}
            mem_info["name"] = child.Name
            # mem_info["vendor"] = child.Manufacturer
            mem_info["max_memory"] = child.MaxMemorySupported

            hw_info["gpu"].append(mem_info)

        out_path = os.path.join("logs", self.mac.replace(":", "-"), "hw.json")
        with open(out_path, "w+") as outfile:
            outfile.write(json.dumps(hw_info))

    def __window_callback(self, hwnd, win_informations):
        window = {}

        thread_process_id = win32process.GetWindowThreadProcessId(hwnd)

        window["win_id"] = hwnd
        window["pid"] = thread_process_id[1]
        window["thread_id"] = thread_process_id[0]
        window["wm-class"] = win32gui.GetClassName(hwnd)
        window["title"] = win32gui.GetWindowText(hwnd)
        window["focus"] = win32gui.GetForegroundWindow() == hwnd

        win_informations.append(window)

        # process_info = {"iter_id": self.iteration_count, "timestamp": datetime.datetime.now().isoformat()}
        #

        # process_info["process_id"] = thread_process_id[1]
        # process_info["thread_id"] = thread_process_id[0]
        #
        # if str(process_info["process_id"]) + "-" + str(process_info["thread_id"]) in self.id_history:
        #     return
        #
        # self.id_history.append(
        #     str(process_info["process_id"]) + "-" + str(process_info["thread_id"]))
        #
        # children = self.wmi.ExecQuery("Select * from win32_process "
        #                               "where ProcessId=" + str(process_info["process_id"]))
        # for child in children:
        #     process_info["process_name"] = child.Name
        #     process_info["exec_path"] = child.ExecutablePath
        #     process_info["cmd"] = child.CommandLine
        #     process_info["creation_time"] = child.CreationDate
        #     process_info["state"] = child.ExecutionState
        #
        # process_info["window_title"] = win32gui.GetWindowText(hwnd)
        #
        # is_foreground = \
        #     win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow()) == thread_process_id
        #
        # process_info["foreground"] = is_foreground
        # try:
        #     h_proc = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, process_info["process_id"])
        #     process_times = win32process.GetProcessTimes(h_proc)
        #     process_info["user_time"] = process_times["UserTime"] * 100 / (10 ** 6)
        #     process_info["memory"] = win32process.GetProcessMemoryInfo(h_proc)
        #     process_info["io_counter"] = win32process.GetProcessIoCounters(h_proc)
        # except Exception:
        #     pass
        #
        # self.out_file.write(str(process_info) + "\n")

    def log(self):
        freq = 0
        target_period = None

        if self.target_freq is not None:
            target_period = 1 / self.target_freq

        while True:
            start = time.time()
            # print("\rLogging freq: " + str(freq) + " Hz", end="")

            mem = psutil.virtual_memory()

            data = {}
            data["timestamp"] = datetime.datetime.now().isoformat()
            data["%cpu"] = psutil.cpu_percent()
            data["mem_available"] = mem.available
            data["mem_used"] = mem.used
            data["processes"] = []
            data["focussed_window"] = None

            win_informations = []
            win32gui.EnumWindows(self.__window_callback, win_informations)

            for id in win32process.EnumProcesses():
                process = {}
                process["pid"] = id
                try:
                    p_handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, id)

                    process["cmd"] = win32process.GetModuleFileNameEx(p_handle, 0)

                    times = win32process.GetProcessTimes(p_handle)
                    process["start"] = times["CreationTime"].isoformat()
                    process["ktime"] = (times["KernelTime"] * 100) / 1000
                    process["utime"] = (times["UserTime"] * 100) / 1000

                    etime = (datetime.datetime.now(tz=None) - times["CreationTime"].replace(
                        tzinfo=None)).total_seconds()
                    ktime = (process["ktime"] / (10 ** 6))
                    cpu_util = round(ktime / etime * 100, 2)
                    process["%cpu"] = cpu_util

                    mem_info = win32process.GetProcessMemoryInfo(p_handle)
                    process["mem"] = mem_info["WorkingSetSize"]
                except Exception as e:
                    pass

                # print(process)
                data["processes"].append(process)

            for window in win_informations:
                if window["focus"]:
                    data["focussed_window"] = window
                    break

            self.out_file.write(json.dumps(data) + "\n")
            self.out_file.flush()

            period = time.time() - start

            if target_period is not None:
                time.sleep(max(target_period - period, 0))

            freq = 1 / (time.time() - start)

import win32gui
import win32process
import win32api
import win32com.client as win32client
import win32con
import win32timezone
import datetime


class Win32ProcessLogger:
    def __init__(self):
        self.wmi = win32client.GetObject("winmgmts:")
        self.id_history = []

    def __window_callback(self, hwnd, hwnds):
        process_info = {}

        thread_process_id = win32process.GetWindowThreadProcessId(hwnd)
        process_info["process_id"] = thread_process_id[1]
        process_info["thread_id"] = thread_process_id[0]

        if str(process_info["process_id"]) + "-" + str(process_info["thread_id"]) in self.id_history:
            return

        self.id_history.append(
            str(process_info["process_id"]) + "-" + str(process_info["thread_id"]))

        children = self.wmi.ExecQuery("Select * from win32_process where ProcessId=" + str(process_info["process_id"]))
        for child in children:
            process_info["process_name"] = child.Name

        process_info["window_title"] = win32gui.GetWindowText(hwnd)

        is_foreground = \
            win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow()) == thread_process_id

        process_info["foreground"] = is_foreground
        try:
            h_proc = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, process_info["process_id"])
            process_times = win32process.GetProcessTimes(h_proc)
            print(process_times["UserTime"] * 100 / (10 ** 6))
            process_info["creation_time"] = process_times["CreationTime"].isoformat()
        except Exception as e:
            pass

        print(process_info)

    def log(self):
        for i in range(2):
            hwnds = []
            self.id_history = []
            win32gui.EnumWindows(self.__window_callback, hwnds)

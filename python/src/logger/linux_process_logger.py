from logger.logger import Logger
import os
from uuid import getnode
import subprocess
import datetime
import time
import json
import re
import psutil


class LinuxProcessLogger(Logger):
    def __init__(self, target_freq=1):
        self.target_freq = target_freq
        self.mac_address = getnode()
        self.mac_address = "-".join(("%012X" % self.mac_address)[i:i + 2] for i in range(0, 12, 2))

        self.out_file_dir_path = "./logs/" + self.mac_address + "/"

        if not os.path.exists(self.out_file_dir_path):
            os.makedirs(self.out_file_dir_path)

        self.out_file_path = self.out_file_dir_path + "log.jsonld"
        self.out_file = open(self.out_file_path, "w+")

        hw_info = subprocess.check_output(["lshw", "-json"]).decode("utf-8")
        data = {}

        with open(self.out_file_dir_path + "system.json", "w+") as outfile:
            try:
                hw_infos = json.loads(hw_info)
                self.iter_hw(hw_infos, data)
                json.dump(data, outfile)
            except ValueError:
                outfile.write(hw_info)

        os.system("gnome-terminal -- sh -c 'echo \"OfficeLogger started succesfully!\";sleep 2s;'")

        self.err_log = open(self.out_file_dir_path + "err_log.txt", "w+")

    def iter_hw(self, children, data):
        if children["id"] == "memory":
            if "size" in children:
                data["memory"] = {}
                data["memory"]["size"] = children["size"]
                data["memory"]["units"] = children["units"]

        if children["id"] == "cpu":
            data["cpu"] = {}
            data["cpu"]["vendor"] = children["vendor"]
            data["cpu"]["product"] = children["product"]
            data["cpu"]["capacity"] = children["capacity"]
            data["cpu"]["units"] = children["units"]

        if children["id"] == "display":
            data["gpu"] = {}
            data["gpu"]["vendor"] = children["vendor"]
            data["gpu"]["product"] = children["product"]

        for key, value in children.items():
            if key == "children":
                for item in value:
                    self.iter_hw(item, data)

    def log(self):
        target_period = 1 / self.target_freq

        out_file_stat = os.stat(self.out_file_path).st_size

        pattern = re.compile("[ ]+")

        while True:
            start_time = time.time()
            data = {}

            timestamp = datetime.datetime.now()

            try:
                process_list_str = subprocess.check_output(
                    ["ps", "-e", "wwh",
                     "-o", "\"%p||%P||%r||%U||%c||\"",
                     "-o", "cmd:500",
                     "-o", "\"||%t||%x||\"",
                     "-o", "lstart",
                     "-o", "\"||%C||\"",
                     "-o", "%mem",
                     "-o", "||%z||%y||",
                     "-o", "psr"])

                process_list_str = process_list_str.decode("utf-8").replace("\"", "").split("\n")

            except subprocess.CalledProcessError as err:
                self.err_log.write("{} | command '{}' return with error (code {}): {}\n"
                                   .format(timestamp, err.cmd, err.returncode, err.output))
                process_list_str = []

            try:
                window_list_str = subprocess.check_output(
                    ["wmctrl", "-lpx"]
                )

                window_list_str = window_list_str.decode("utf-8").split("\n")
            except subprocess.CalledProcessError as err:
                self.err_log.write("{} | command '{}' return with error (code {}): {}\n"
                                   .format(timestamp, err.cmd, err.returncode, err.output))
                window_list_str = []

            try:
                window_focus_str = subprocess.check_output(
                    ["xprop", "-root", "_NET_ACTIVE_WINDOW"]
                )

                window_focus_str = window_focus_str.decode("utf-8").replace("\n", "").split("window id # ")[1]
            except subprocess.CalledProcessError as err:
                self.err_log.write("{} | command '{}' return with error (code {}): {}\n"
                                   .format(timestamp, err.cmd, err.returncode, err.output))
                window_focus_str = []

            windows = []
            focussed_window = None

            for window in window_list_str:
                attribs = pattern.split(window)

                if len(attribs) > 1:
                    win = {"win_id": attribs[0],
                           "pid": attribs[2],
                           "wm-class": attribs[3],
                           "title": " ".join(attribs[5:len(attribs)]),
                           "focus": False}

                    if hex(int(win["win_id"], base=16)) == hex(int(window_focus_str, base=16)):
                        focussed_window = win
                        win["focus"] = True

                    windows.append(win)

            data["timestamp"] = timestamp.isoformat()
            data["%cpu"] = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            data["mem_available"] = mem.available
            data["mem_used"] = mem.used
            data["focussed_window"] = focussed_window
            data["processes"] = []

            for process in process_list_str:
                process_data = {}

                attribs = process.split("||")
                attribs = [x.strip() for x in attribs]

                if len(attribs) > 1:
                    if len(attribs) == 14:
                        process_data["pid"] = attribs[0]
                        process_data["ppid"] = attribs[1]
                        process_data["pgid"] = attribs[2]
                        process_data["user"] = attribs[3]
                        process_data["cmd_name"] = attribs[4]
                        process_data["cmd"] = attribs[5]
                        process_data["etime"] = attribs[6]
                        process_data["ctime"] = attribs[7]
                        process_data["start"] = attribs[8]
                        process_data["%cpu"] = attribs[9]
                        process_data["%mem"] = attribs[10]
                        process_data["mem"] = attribs[11]
                        process_data["psr"] = attribs[13]

                        process_data["windows"] = []

                        for window in windows:
                            if window["pid"] == process_data["pid"]:
                                process_data["windows"].append(window)

                        data["processes"].append(process_data)

            self.out_file.write(json.dumps(data) + "\n")
            self.out_file.flush()

            size_gain = os.stat(self.out_file_path).st_size - out_file_stat
            out_file_stat = os.stat(self.out_file_path).st_size

            print("\rGained: " + str(round(size_gain / 1024, 2)) + "kB " +
                  "Total: " + str(round(out_file_stat / 1024, 2)) + "kB", end="")

            period = time.time() - start_time
            time.sleep(max(target_period - period, 0))

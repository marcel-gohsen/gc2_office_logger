from cx_Freeze import setup, Executable
import platform

build_exe_options = {}
name = None

if platform.system() == "Windows":
    build_exe_options = {
        "packages": [
            "datetime",
            "win32gui",
            "win32process",
            "win32api",
            "win32com",
            "win32con",
            "os",
            "time",
            "tendo"],
        "build_exe": "../build/" + platform.system().lower()}
    name = "OfficeLogger_win32.exe"
elif platform.system() == "Linux":
    build_exe_options = {
        "packages": ["os", "uuid", "tendo"],
        "init_script": "ConsoleSetLibPath",
        "build_exe": "../build/" + platform.system().lower()
    }
    name = "OfficeLogger"

setup(name="OfficeLogger",
      version="0.1",
      description="",
      options={"build_exe": build_exe_options},
      executables=[Executable("./launch.py", targetName=name)])

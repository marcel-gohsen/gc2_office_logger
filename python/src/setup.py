from cx_Freeze import setup, Executable
import platform

build_exe_options = {}

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
            "time"],
        "build_exe": "../build/" + platform.system().lower()}
elif platform.system() == "Linux":
    build_exe_options = {
        "packages": ["os", "uuid"],
        "init_script": "ConsoleSetLibPath",
        "build_exe": "../build/" + platform.system().lower()
    }

setup(name="OfficeLogger",
      version="0.1",
      description="",
      options={"build_exe": build_exe_options},
      executables=[Executable("./launch.py", targetName="OfficeLogger")])

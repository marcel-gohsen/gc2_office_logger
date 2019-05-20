from cx_Freeze import setup, Executable

build_exe_options = {"packages": [
      "datetime",
      "win32gui",
      "win32process",
      "win32api",
      "win32com",
      "win32con",
      "os",
      "time"]}

setup(name="OfficeLogger",
      version="0.1",
      description="",
      options={"build_exe": build_exe_options},
      executables=[Executable("./launch.py", targetName="OfficeLogger.exe")])

from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["time", "win32gui", "win32process"]}

setup(name="OfficeLogger",
      version="0.1",
      description="",
      options={"build_exe": build_exe_options},
      executables=[Executable("./launch.py")])

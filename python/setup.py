from cx_Freeze import setup, Executable

setup(name="OfficeLogger",
      version="0.1",
      description="",
      executables=[Executable("src/test.py")])

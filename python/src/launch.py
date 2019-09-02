import time
import traceback
import platform
# import os
# import uuid


def main():
    logger = None

    if platform.system() == "Linux":
        from logger.linux_process_logger import LinuxProcessLogger
        logger = LinuxProcessLogger()
    elif platform.system() == "Windows":
        from logger.win32_process_logger import Win32ProcessLogger
        logger = Win32ProcessLogger(target_freq=1)
    else:
        raise RuntimeError("Unsupported OS " + str(platform.system()))

    logger.log()


def sigterm_handler(s, f):
    print(s)
    time.sleep(10)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        time.sleep(10)

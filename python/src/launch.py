import time
import traceback

from logger.win32_process_logger import Win32ProcessLogger


def main():
    logger = Win32ProcessLogger()
    logger.log()

    time.sleep(100)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        time.sleep(10)

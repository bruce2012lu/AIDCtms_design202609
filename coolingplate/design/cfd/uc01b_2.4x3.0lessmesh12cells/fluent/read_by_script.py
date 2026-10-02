"""Read a Fluent journal through the console text prompt. No File menu."""
import sys
import time

import send_tui

def main():
    path = sys.argv[1].replace("\\", "/")
    send_tui.main_send("/file/read-journal")
    time.sleep(0.4)
    send_tui.main_send(path)
    time.sleep(0.3)
    send_tui.main_send("()")
    print("queued", path)

if __name__ == "__main__":
    main()

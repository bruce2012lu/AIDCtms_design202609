# -*- coding: utf-8 -*-
"""After ANNO-PICK, switch to Graphics and place the annotation with one click."""
import sys
import time
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32


def click(x, y):
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.08)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)


def main():
    path = sys.argv[1]
    start = 0
    deadline = time.time() + 600
    while time.time() < deadline:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                handle.read(1)
            break
        except OSError:
            time.sleep(0.4)
    else:
        raise SystemExit("transcript missing")
    seen = False
    while time.time() < deadline:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            handle.seek(start)
            if "ANNO-PICK" in handle.read():
                seen = True
                break
        time.sleep(0.4)
    if not seen:
        raise SystemExit("ANNO-PICK not seen")
    time.sleep(0.6)
    user32.keybd_event(0x12, 0, 0, 0)
    time.sleep(0.05)
    click(555, 898)
    time.sleep(0.35)
    user32.keybd_event(0x12, 0, 2, 0)
    click(1180, 240)
    print("annotation click 1180 240")


if __name__ == "__main__":
    main()

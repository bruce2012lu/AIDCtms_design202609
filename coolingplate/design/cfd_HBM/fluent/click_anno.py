"""Wait until the transcript shows ANNO-PICK, then one click in the graphics view."""
import ctypes
import sys
import time
from ctypes import wintypes

user32 = ctypes.windll.user32
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.IsWindowVisible.argtypes = [wintypes.HWND]


def click(x, y):
    user32.SetCursorPos(x, y)
    time.sleep(0.08)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)


def largest_child(parent):
    best = None
    best_area = 0

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, lparam):
        nonlocal best, best_area
        if not user32.IsWindowVisible(hwnd):
            return True
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        area = w * h
        # Ignore docks parked off the primary monitor.
        if rect.left < -100 or rect.top < -100:
            return True
        if w > 400 and h > 300 and area > best_area:
            best_area = area
            best = (hwnd, rect.left, rect.top, rect.right, rect.bottom)
        return True

    user32.EnumChildWindows(parent, cb, 0)
    return best


def fluent_hwnd():
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, lparam):
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        if "Fluent" in buf.value and user32.IsWindowVisible(hwnd):
            found.append(hwnd)
        return True

    user32.EnumWindows(cb, 0)
    if not found:
        raise SystemExit("no Fluent window")
    return found[0]


def main():
    path = sys.argv[1]
    marker = sys.argv[2] if len(sys.argv) > 2 else "ANNO-PICK"
    start = 0
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        start = handle.seek(0, 2)
    deadline = time.time() + 180
    seen = False
    while time.time() < deadline:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            handle.seek(start)
            chunk = handle.read()
        if marker in chunk:
            seen = True
            break
        time.sleep(0.4)
    if not seen:
        raise SystemExit("marker not seen: " + marker)
    time.sleep(0.8)
    parent = fluent_hwnd()
    child = largest_child(parent)
    if child:
        hwnd, left, top, right, bottom = child
        x = left + 180
        y = top + 70
        print("child", left, top, right, bottom, "click", x, y)
    else:
        rect = wintypes.RECT()
        user32.GetWindowRect(parent, ctypes.byref(rect))
        x = rect.left + 700
        y = rect.top + 280
        print("window click", x, y)
    click(x, y)
    print("clicked once")


if __name__ == "__main__":
    main()

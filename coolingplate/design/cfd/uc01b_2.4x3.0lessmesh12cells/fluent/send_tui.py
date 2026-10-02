"""Send one TUI/Scheme line into the open Fluent console. No menu clicks."""
import ctypes
import sys
import time
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
WM_CHAR = 0x0102


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("ki", KEYBDINPUT), ("pad", wintypes.DWORD * 2)]


def console_hwnd():
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def child(hwnd, lparam):
        buf = ctypes.create_unicode_buffer(80)
        user32.GetWindowTextW(hwnd, buf, 80)
        if buf.value == "Console":
            found.append(hwnd)
        return True

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def top(hwnd, lparam):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == 67480 and user32.IsWindowVisible(hwnd):
            user32.EnumChildWindows(hwnd, child, 0)
        return True

    user32.EnumWindows(top, 0)
    if not found:
        raise SystemExit("Console window not found")
    return found[0]


def tap(vk):
    down = INPUT(type=INPUT_KEYBOARD)
    down.ki.wVk = vk
    up = INPUT(type=INPUT_KEYBOARD)
    up.ki.wVk = vk
    up.ki.dwFlags = KEYEVENTF_KEYUP
    user32.SendInput(1, ctypes.byref(down), ctypes.sizeof(INPUT))
    user32.SendInput(1, ctypes.byref(up), ctypes.sizeof(INPUT))


def ctrl(vk):
    user32.keybd_event(0x11, 0, 0, 0)
    tap(vk)
    user32.keybd_event(0x11, 0, KEYEVENTF_KEYUP, 0)


def send_unicode(text):
    pair = (INPUT * 2)()
    for ch in text:
        # Unicode hyphen is doubled by this Fluent console. Use the OEM minus key.
        if ch == "-":
            tap(0xBD)
            time.sleep(0.012)
            continue
        pair[0].type = INPUT_KEYBOARD
        pair[0].ki.wScan = ord(ch)
        pair[0].ki.dwFlags = KEYEVENTF_UNICODE
        pair[1].type = INPUT_KEYBOARD
        pair[1].ki.wScan = ord(ch)
        pair[1].ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
        if user32.SendInput(2, pair, ctypes.sizeof(INPUT)) != 2:
            raise SystemExit("SendInput failed")
        time.sleep(0.012)


class RECT(ctypes.Structure):
    _fields_ = [("l", ctypes.c_long), ("t", ctypes.c_long), ("r", ctypes.c_long), ("b", ctypes.c_long)]


def click(x, y):
    user32.SetCursorPos(x, y)
    time.sleep(0.05)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.02)
    user32.mouse_event(0x0004, 0, 0, 0, 0)


def main_send(line):
    hwnd = console_hwnd()
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    main_hwnd = user32.GetAncestor(hwnd, 2)
    this = kernel32.GetCurrentThreadId()
    target = user32.GetWindowThreadProcessId(main_hwnd, None)
    user32.AttachThreadInput(this, target, True)
    user32.ShowWindow(main_hwnd, 3)
    user32.SetForegroundWindow(main_hwnd)
    time.sleep(0.25)
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    click((rect.l + rect.r) // 2, rect.b - 18)
    time.sleep(0.12)
    if line != "-":
        send_unicode(line)
        time.sleep(0.04)
    tap(0x0D)
    user32.AttachThreadInput(this, target, False)


def main():
    line = sys.argv[1]
    main_send(line)
    print("sent")


if __name__ == "__main__":
    main()

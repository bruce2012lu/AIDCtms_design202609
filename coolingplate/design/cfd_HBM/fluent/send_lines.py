# -*- coding: utf-8 -*-
"""Focus the Fluent console and send a few TUI lines with Unicode input."""
import ctypes
import time
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]

    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _U)]


def fluent_hwnd():
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        n = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(n + 1)
        user32.GetWindowTextW(hwnd, buf, n + 1)
        if "Fluent" in (buf.value or ""):
            found.append(hwnd)
        return True

    user32.EnumWindows(cb, 0)
    if not found:
        raise SystemExit("no Fluent window")
    return found[0]


def tap_unicode(ch):
    down = INPUT(type=INPUT_KEYBOARD)
    down.ki = KEYBDINPUT(0, ord(ch), KEYEVENTF_UNICODE, 0, None)
    up = INPUT(type=INPUT_KEYBOARD)
    up.ki = KEYBDINPUT(0, ord(ch), KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, None)
    user32.SendInput(1, ctypes.byref(down), ctypes.sizeof(INPUT))
    user32.SendInput(1, ctypes.byref(up), ctypes.sizeof(INPUT))


def tap_vk(vk):
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def click(x, y):
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.05)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.04)
    user32.mouse_event(0x0004, 0, 0, 0, 0)


def send_line(text):
    for ch in text:
        tap_unicode(ch)
        time.sleep(0.01)
    tap_vk(0x0D)
    time.sleep(0.15)


def main():
    hwnd = fluent_hwnd()
    this = kernel32.GetCurrentThreadId()
    target = user32.GetWindowThreadProcessId(hwnd, None)
    user32.AttachThreadInput(this, target, True)
    user32.keybd_event(0x12, 0, 0, 0)
    time.sleep(0.05)
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.15)
    user32.keybd_event(0x12, 0, 2, 0)
    click(470, 888)
    time.sleep(0.25)
    click(800, 640)
    time.sleep(0.2)
    fg = user32.GetForegroundWindow()
    n = user32.GetWindowTextLengthW(fg)
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(fg, buf, n + 1)
    print("foreground", fg, buf.value[:80])
    jou = "D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd_HBM/fluent/hbm_cf_capture.jou"
    for line in ("/file/read-journal", jou, "()"):
        send_line(line)
        time.sleep(0.4)
    user32.AttachThreadInput(this, target, False)
    print("lines sent")


if __name__ == "__main__":
    main()

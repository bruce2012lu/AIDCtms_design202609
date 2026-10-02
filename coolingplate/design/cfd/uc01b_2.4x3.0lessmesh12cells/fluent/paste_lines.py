"""Paste TUI lines through the clipboard so hyphens stay intact."""
import ctypes
import sys
import time
from ctypes import wintypes

import send_tui

user32 = send_tui.user32
kernel32 = send_tui.kernel32
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

kernel32.GlobalAlloc.restype = ctypes.c_void_p
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
user32.SetClipboardData.argtypes = [wintypes.UINT, ctypes.c_void_p]
user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.EmptyClipboard.argtypes = []
user32.CloseClipboard.argtypes = []


def set_clip(text):
    raw = (text + "\0").encode("utf-16-le")
    if not user32.OpenClipboard(None):
        raise SystemExit("OpenClipboard failed")
    try:
        user32.EmptyClipboard()
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(raw))
        locked = kernel32.GlobalLock(handle)
        ctypes.memmove(locked, raw, len(raw))
        kernel32.GlobalUnlock(handle)
        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
            raise SystemExit("SetClipboardData failed")
    finally:
        user32.CloseClipboard()


def fluent_console():
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
        if not user32.IsWindowVisible(hwnd):
            return True
        buf = ctypes.create_unicode_buffer(200)
        user32.GetWindowTextW(hwnd, buf, 200)
        if "Fluent" in buf.value and "uc01b" in buf.value:
            user32.EnumChildWindows(hwnd, child, 0)
            found.append(("main", hwnd))
        return True

    user32.EnumWindows(top, 0)
    consoles = [item for item in found if not isinstance(item, tuple)]
    mains = [item[1] for item in found if isinstance(item, tuple)]
    if not consoles or not mains:
        raise SystemExit("Fluent console not found")
    return mains[0], consoles[0]


def focus(main, console):
    user32.keybd_event(0x12, 0, 0, 0)
    user32.SetForegroundWindow(main)
    user32.keybd_event(0x12, 0, 2, 0)
    time.sleep(0.25)
    rect = send_tui.RECT()
    user32.GetWindowRect(console, ctypes.byref(rect))
    send_tui.click((rect.l + rect.r) // 2, rect.b - 18)
    time.sleep(0.12)


def paste_line(main, console, line):
    set_clip(line)
    focus(main, console)
    user32.keybd_event(0x11, 0, 0, 0)
    send_tui.tap(0x56)
    user32.keybd_event(0x11, 0, 2, 0)
    time.sleep(0.08)
    send_tui.tap(0x0D)
    time.sleep(0.7)


def main():
    lines = sys.argv[1:]
    main_hwnd = 1511948
    user32.keybd_event(0x12, 0, 0, 0)
    user32.SetForegroundWindow(main_hwnd)
    user32.keybd_event(0x12, 0, 2, 0)
    time.sleep(0.2)
    for line in lines:
        set_clip(line)
        user32.keybd_event(0x12, 0, 0, 0)
        user32.SetForegroundWindow(main_hwnd)
        user32.keybd_event(0x12, 0, 2, 0)
        time.sleep(0.2)
        send_tui.click(750, 955)
        time.sleep(0.15)
        user32.keybd_event(0x11, 0, 0, 0)
        send_tui.tap(0x56)
        user32.keybd_event(0x11, 0, 2, 0)
        time.sleep(0.1)
        send_tui.tap(0x0D)
        time.sleep(0.8)
    print("pasted", len(lines))


if __name__ == "__main__":
    main()

"""Bring the Fluent window forward, then paste one journal carrier."""
import ctypes
import sys
import time
from ctypes import wintypes

import console_paste

user32 = console_paste.user32
kernel32 = console_paste.kernel32
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
user32.AttachThreadInput.restype = wintypes.BOOL
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.BringWindowToTop.argtypes = [wintypes.HWND]


def force_front(hwnd):
    fg = user32.GetForegroundWindow()
    fg_thread = user32.GetWindowThreadProcessId(fg, None)
    this_thread = kernel32.GetCurrentThreadId()
    user32.AttachThreadInput(this_thread, fg_thread, True)
    user32.ShowWindow(hwnd, 9)
    user32.BringWindowToTop(hwnd)
    ok = user32.SetForegroundWindow(hwnd)
    user32.AttachThreadInput(this_thread, fg_thread, False)
    time.sleep(0.3)
    print("foreground", user32.GetForegroundWindow(), "ok", ok)


def main():
    force_front(console_paste.MAIN)
    # Reuse the one-block paste.
    sys.argv = ["console_paste.py", "--file", sys.argv[1]]
    console_paste.main()
    time.sleep(0.4)
    print("foreground_after", user32.GetForegroundWindow())


if __name__ == "__main__":
    main()

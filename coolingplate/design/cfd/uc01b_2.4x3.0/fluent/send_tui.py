# -*- coding: utf-8 -*-
"""Type one TUI line into the live Fluent console (cx2610 PID 7688)."""
from __future__ import annotations

import ctypes
import sys
import time
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
ULONG_PTR = ctypes.c_ulonglong

HWND = 9703802
# Console Qt pane is screen 620,792-1263,966. Click the input line.
CLICK_X = 800
CLICK_Y = 930


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]


def send_char(ch: str) -> None:
    inp = INPUT()
    inp.type = 1
    inp.union.ki = KEYBDINPUT(0, ord(ch), 0x0004, 0, 0)
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    inp.union.ki.dwFlags = 0x0004 | 0x0002
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


def send_vk(vk: int) -> None:
    inp = INPUT()
    inp.type = 1
    inp.union.ki = KEYBDINPUT(vk, 0, 0, 0, 0)
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    inp.union.ki.dwFlags = 0x0002
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


def force_foreground(hwnd: int) -> int:
    fg = user32.GetForegroundWindow()
    this_thread = kernel32.GetCurrentThreadId()
    fg_thread = user32.GetWindowThreadProcessId(fg, None)
    target_thread = user32.GetWindowThreadProcessId(hwnd, None)
    user32.AttachThreadInput(this_thread, fg_thread, True)
    user32.AttachThreadInput(this_thread, target_thread, True)
    user32.keybd_event(0x12, 0, 0, 0)
    user32.keybd_event(0x12, 0, 2, 0)
    user32.ShowWindow(hwnd, 9)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    user32.AttachThreadInput(this_thread, fg_thread, False)
    user32.AttachThreadInput(this_thread, target_thread, False)
    time.sleep(0.25)
    return user32.GetForegroundWindow()


def focus_console(hwnd: int = HWND) -> int:
    fg = force_foreground(hwnd)
    user32.SetCursorPos(CLICK_X, CLICK_Y)
    time.sleep(0.08)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.06)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.25)
    return fg


def main() -> None:
    src = sys.argv[1]
    line = open(src, encoding="utf-8").read().replace("\r", "").replace("\n", "")
    hwnd = int(sys.argv[2]) if len(sys.argv) > 2 else HWND
    fg = focus_console(hwnd)
    print("fg", fg, "want", hwnd)
    if fg != hwnd:
        print("ABORT focus failed")
        sys.exit(2)
    for ch in line:
        send_char(ch)
        time.sleep(0.008)
    time.sleep(0.15)
    send_vk(0x0D)
    print("sent", len(line))


if __name__ == "__main__":
    main()

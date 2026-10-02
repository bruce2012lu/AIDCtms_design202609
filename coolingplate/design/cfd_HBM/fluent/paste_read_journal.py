"""Paste /file/read-journal into the open HBM Fluent console. One paste, then Enter."""
import ctypes
import time
from ctypes import wintypes

import comtypes.client
from comtypes.gen import UIAutomationClient

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002

kernel32.GlobalAlloc.restype = ctypes.c_void_p
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
user32.SetClipboardData.argtypes = [wintypes.UINT, ctypes.c_void_p]
user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.EmptyClipboard.argtypes = []
user32.CloseClipboard.argtypes = []


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


def key_event(vk, up=False):
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP if up else 0, 0)


def chord(vk):
    key_event(0x11, False)
    time.sleep(0.02)
    key_event(vk, False)
    key_event(vk, True)
    key_event(0x11, True)
    time.sleep(0.05)


def main_window():
    uia = comtypes.client.CreateObject(
        "{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIAutomationClient.IUIAutomation
    )
    root = uia.GetRootElement()
    cond = uia.CreatePropertyCondition(
        UIAutomationClient.UIA_NamePropertyId,
        "hbm_array_laminar_i400 Fluent@DESKTOP-JHEHF28  [3d, pbns, lam, single-process] ",
    )
    win = root.FindFirst(UIAutomationClient.TreeScope_Children, cond)
    if not win:
        cond = uia.CreatePropertyCondition(
            UIAutomationClient.UIA_ClassNamePropertyId, "Qt5QWindowIcon"
        )
        nodes = root.FindAll(UIAutomationClient.TreeScope_Children, cond)
        for i in range(nodes.Length):
            el = nodes.GetElement(i)
            name = el.CurrentName or ""
            if "hbm_array_laminar_i400" in name:
                win = el
                break
    if not win:
        raise SystemExit("Fluent window not found")
    print("window", win.CurrentName)
    return uia, win


def console_edit(uia, win):
    cond = uia.CreatePropertyCondition(
        UIAutomationClient.UIA_AutomationIdPropertyId,
        "ConsoleDockWidget.ConsoleParentWidget.CxConsole",
    )
    edit = win.FindFirst(UIAutomationClient.TreeScope_Descendants, cond)
    if not edit:
        raise SystemExit("CxConsole not found")
    return edit


def main():
    text = (
        "/file/read-journal\n"
        "D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd_HBM/fluent/sample_i400.jou\n"
        "()\n"
    )
    uia, win = main_window()
    edit = console_edit(uia, win)
    hwnd = win.CurrentNativeWindowHandle
    user32.keybd_event(0x12, 0, 0, 0)
    user32.SetForegroundWindow(hwnd)
    user32.keybd_event(0x12, 0, 2, 0)
    edit.SetFocus()
    time.sleep(0.3)
    chord(0x23)
    set_clip(text)
    time.sleep(0.2)
    chord(0x56)
    time.sleep(1.2)
    key_event(0x11, True)
    time.sleep(0.2)
    key_event(0x0D, False)
    key_event(0x0D, True)
    print("pasted")


if __name__ == "__main__":
    main()

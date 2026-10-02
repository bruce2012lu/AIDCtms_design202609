"""Paste one /file/read-journal blob into the open Fluent console, then Enter."""
import ctypes
import sys
import time
from ctypes import wintypes

import comtypes.client
from comtypes.gen import UIAutomationClient

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
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


def fluent_hwnd():
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        if "Fluent" in (buf.value or ""):
            found.append(hwnd)
        return True

    user32.EnumWindows(cb, 0)
    if not found:
        raise SystemExit("Fluent window not found")
    return found[0]


def fluent_window(uia):
    hwnd = fluent_hwnd()
    el = uia.ElementFromHandle(hwnd)
    print("window", el.CurrentName)
    return el


def invoke_console(uia, win):
    cond = uia.CreatePropertyCondition(UIAutomationClient.UIA_NamePropertyId, "Console")
    nodes = win.FindAll(UIAutomationClient.TreeScope_Descendants, cond)
    for i in range(nodes.Length):
        el = nodes.GetElement(i)
        if el.CurrentControlType != UIAutomationClient.UIA_TabItemControlTypeId:
            continue
        pattern = el.GetCurrentPattern(UIAutomationClient.UIA_InvokePatternId)
        pattern.QueryInterface(UIAutomationClient.IUIAutomationInvokePattern).Invoke()
        print("invoked console tab")
        return
    print("console tab not invoked")


def main():
    jou = sys.argv[1]
    text = "/file/read-journal\n%s\n()\n" % jou.replace("\\", "/")
    uia = comtypes.client.CreateObject(
        "{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIAutomationClient.IUIAutomation
    )
    win = fluent_window(uia)
    hwnd = win.CurrentNativeWindowHandle
    this = kernel32.GetCurrentThreadId()
    target = user32.GetWindowThreadProcessId(hwnd, None)
    user32.AttachThreadInput(this, target, True)
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    x, y = 780, 968
    print("click console", x, y)
    user32.SetCursorPos(x, y)
    time.sleep(0.05)
    user32.mouse_event(2, 0, 0, 0, 0)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.25)
    chord(0x23)
    set_clip(text)
    time.sleep(0.2)
    chord(0x56)
    time.sleep(1.2)
    key_event(0x11, True)
    time.sleep(0.2)
    key_event(0x0D, False)
    key_event(0x0D, True)
    user32.AttachThreadInput(this, target, False)
    print("pasted", jou, "at", x, y)


if __name__ == "__main__":
    main()

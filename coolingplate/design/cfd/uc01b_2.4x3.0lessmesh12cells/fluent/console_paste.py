"""Paste TUI lines into the open Fluent console. No mouse, Fluent stays open."""
import ctypes
import sys
import time
from ctypes import wintypes

import comtypes.client
from comtypes.gen import UIAutomationClient

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

PANE = 12845504
MAIN = 1511948


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


def console_edit():
    uia = comtypes.client.CreateObject(
        "{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIAutomationClient.IUIAutomation
    )
    pane = uia.ElementFromHandle(PANE)
    cond = uia.CreatePropertyCondition(
        UIAutomationClient.UIA_AutomationIdPropertyId,
        "ConsoleDockWidget.ConsoleParentWidget.CxConsole",
    )
    edit = pane.FindFirst(UIAutomationClient.TreeScope_Descendants, cond)
    if not edit:
        raise SystemExit("CxConsole not found")
    return edit


def key_event(vk, up=False):
    event = send_tui.INPUT(type=send_tui.INPUT_KEYBOARD)
    event.ki.wVk = vk
    if up:
        event.ki.dwFlags = send_tui.KEYEVENTF_KEYUP
    if user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(send_tui.INPUT)) != 1:
        raise SystemExit("SendInput failed")


def chord(vk):
    key_event(0x11, False)
    time.sleep(0.02)
    key_event(vk, False)
    key_event(vk, True)
    key_event(0x11, True)
    time.sleep(0.05)


def console_value(edit):
    unknown = edit.GetCurrentPattern(UIAutomationClient.UIA_ValuePatternId)
    pattern = unknown.QueryInterface(UIAutomationClient.IUIAutomationValuePattern)
    return pattern.CurrentValue


def focus_console():
    edit = console_edit()
    user32.keybd_event(0x11, 0, 2, 0)
    user32.keybd_event(0x12, 0, 0, 0)
    user32.SetForegroundWindow(MAIN)
    user32.keybd_event(0x12, 0, 2, 0)
    edit.SetFocus()
    time.sleep(0.2)
    chord(0x23)  # Ctrl+End, caret at the prompt
    return edit


def paste_line(line):
    focus_console()
    set_clip(line)
    time.sleep(0.12)
    chord(0x56)
    time.sleep(1.2)
    key_event(0x11, True)
    key_event(0x0D, False)
    key_event(0x0D, True)
    time.sleep(1.6)


def main():
    if len(sys.argv) != 3 or sys.argv[1] != "--file":
        raise SystemExit("usage: console_paste.py --file lines.txt")
    text = open(sys.argv[2], encoding="utf-8").read().replace("\r\n", "\n")
    if not text.endswith("\n"):
        text += "\n"
    # One paste. Per-line Enter concatenates into read-journalD: when the console is busy.
    focus_console()
    set_clip(text)
    time.sleep(0.2)
    chord(0x56)
    time.sleep(1.4)
    key_event(0x11, True)
    time.sleep(0.2)
    key_event(0x0D, False)
    key_event(0x0D, True)
    time.sleep(1.6)
    print("pasted", text.count("\n"))


if __name__ == "__main__":
    main()

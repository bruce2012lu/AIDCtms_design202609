# -*- coding: utf-8 -*-
"""Foreground Fluent, open the Console tab, paste one read-journal blob."""
import sys
import time

import paste_journal as p

CONSOLE_TAB = (500, 870)
PROMPT = (800, 700)


def click(x, y):
    p.user32.SetCursorPos(x, y)
    time.sleep(0.05)
    p.user32.mouse_event(2, 0, 0, 0, 0)
    p.user32.mouse_event(4, 0, 0, 0, 0)


def main():
    jou = sys.argv[1].replace("\\", "/")
    text = "/file/read-journal\n%s\n()\n" % jou
    hwnd = p.fluent_hwnd()
    print("hwnd", hwnd)
    this = p.kernel32.GetCurrentThreadId()
    target = p.user32.GetWindowThreadProcessId(hwnd, None)
    p.user32.AttachThreadInput(this, target, True)
    p.user32.keybd_event(0x12, 0, 0, 0)
    time.sleep(0.05)
    p.user32.ShowWindow(hwnd, 9)
    p.user32.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    p.user32.keybd_event(0x12, 0, 2, 0)
    click(*CONSOLE_TAB)
    time.sleep(0.3)
    click(*PROMPT)
    time.sleep(0.2)
    p.key_event(0x1B, False)
    p.key_event(0x1B, True)
    time.sleep(0.2)
    p.chord(0x23)
    p.set_clip(text)
    time.sleep(0.2)
    p.chord(0x56)
    time.sleep(1.0)
    p.key_event(0x11, True)
    time.sleep(0.2)
    p.key_event(0x0D, False)
    p.key_event(0x0D, True)
    p.user32.AttachThreadInput(this, target, False)
    print("pasted", jou)


if __name__ == "__main__":
    main()

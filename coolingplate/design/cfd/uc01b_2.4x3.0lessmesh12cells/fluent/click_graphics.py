"""One click, no drag, in the upper blank of the graphics view."""
import time

import comtypes.client
from comtypes.gen import UIAutomationClient

import send_tui

MAIN = 1511948


def invoke_graphics():
    uia = comtypes.client.CreateObject(
        "{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIAutomationClient.IUIAutomation
    )
    root = uia.ElementFromHandle(MAIN)
    cond = uia.CreatePropertyCondition(UIAutomationClient.UIA_NamePropertyId, "Graphics")
    found = root.FindAll(UIAutomationClient.TreeScope_Descendants, cond)
    for i in range(found.Length):
        el = found.GetElement(i)
        if el.CurrentControlType != UIAutomationClient.UIA_TabItemControlTypeId:
            continue
        pattern = el.GetCurrentPattern(UIAutomationClient.UIA_InvokePatternId)
        pattern.QueryInterface(UIAutomationClient.IUIAutomationInvokePattern).Invoke()
        print("invoked graphics tab")
        return
    raise SystemExit("graphics tab not found")


def click_blank():
    send_tui.user32.SetCursorPos(1200, 320)
    time.sleep(0.08)
    send_tui.user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    send_tui.user32.mouse_event(0x0004, 0, 0, 0, 0)
    print("clicked")


if __name__ == "__main__":
    invoke_graphics()
    time.sleep(0.3)
    click_blank()

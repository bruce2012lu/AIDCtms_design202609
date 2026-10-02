import time

import comtypes.client
from comtypes.gen import UIAutomationClient

import console_paste
import send_tui

uia = comtypes.client.CreateObject(
    "{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIAutomationClient.IUIAutomation
)
root = uia.ElementFromHandle(2365066)
walker = uia.RawViewWalker
child = walker.GetFirstChildElement(root)
graphics = None
while child:
    if child.CurrentName == "Graphics":
        graphics = child
        break
    child = walker.GetNextSiblingElement(child)
if graphics is None:
    raise SystemExit("no graphics tab")
pattern = graphics.GetCurrentPattern(UIAutomationClient.UIA_InvokePatternId)
pattern.QueryInterface(UIAutomationClient.IUIAutomationInvokePattern).Invoke()
print("tab invoked")
time.sleep(0.6)
user32 = send_tui.user32
rect = send_tui.RECT()
user32.GetWindowRect(1512752, send_tui.ctypes.byref(rect))
print("gfx", rect.l, rect.t, rect.r, rect.b)
x = (rect.l + rect.r) // 2
y = rect.t + 80
user32.SetCursorPos(x, y)
time.sleep(0.1)
user32.mouse_event(0x0002, 0, 0, 0, 0)
time.sleep(0.05)
user32.mouse_event(0x0004, 0, 0, 0, 0)
print("clicked", x, y)
time.sleep(1.5)
value = console_paste.console_value(console_paste.console_edit())
print(value[-500:])

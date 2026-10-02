import comtypes.client
from comtypes.gen import UIAutomationClient

MAIN = 1511948
uia = comtypes.client.CreateObject(
    "{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIAutomationClient.IUIAutomation
)
root = uia.ElementFromHandle(MAIN)
cond = uia.CreatePropertyCondition(UIAutomationClient.UIA_NamePropertyId, "Graphics")
el = root.FindFirst(UIAutomationClient.TreeScope_Descendants, cond)
if not el:
    raise SystemExit("no Graphics")
rect = el.CurrentBoundingRectangle
print(el.CurrentControlType, el.CurrentAutomationId, int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))

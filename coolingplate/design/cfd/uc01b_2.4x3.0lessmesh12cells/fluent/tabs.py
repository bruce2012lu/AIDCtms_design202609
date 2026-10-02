import comtypes.client
from comtypes.gen import UIAutomationClient

uia = comtypes.client.CreateObject(
    "{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIAutomationClient.IUIAutomation
)
root = uia.ElementFromHandle(2365066)
print("root", root.CurrentName, root.CurrentControlType)
walker = uia.RawViewWalker
child = walker.GetFirstChildElement(root)
n = 0
while child and n < 15:
    rect = child.CurrentBoundingRectangle
    print(n, child.CurrentControlType, repr(child.CurrentName), int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))
    child = walker.GetNextSiblingElement(child)
    n += 1

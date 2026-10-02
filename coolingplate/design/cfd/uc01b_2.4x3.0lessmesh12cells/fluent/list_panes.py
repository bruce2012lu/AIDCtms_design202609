import comtypes.client
from comtypes.gen import UIAutomationClient

MAIN = 1511948
uia = comtypes.client.CreateObject(
    "{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIAutomationClient.IUIAutomation
)
root = uia.ElementFromHandle(MAIN)
cond = uia.CreateTrueCondition()
walker = uia.RawViewWalker
child = walker.GetFirstChildElement(root)
n = 0
while child and n < 40:
    name = child.CurrentName or ""
    aid = child.CurrentAutomationId or ""
    rect = child.CurrentBoundingRectangle
    print(
        "%s | %s | %s | %s,%s %sx%s"
        % (
            child.CurrentControlType,
            name[:40],
            aid[:60],
            int(rect.left),
            int(rect.top),
            int(rect.right - rect.left),
            int(rect.bottom - rect.top),
        )
    )
    child = walker.GetNextSiblingElement(child)
    n += 1

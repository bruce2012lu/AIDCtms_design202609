import ctypes
import time
from ctypes import wintypes

user32 = ctypes.windll.user32
MAIN = 1511948
GFX = 1512752
SW_RESTORE = 9
SW_MAXIMIZE = 3
SWP_NOZORDER = 0x0004


class RECT(ctypes.Structure):
    _fields_ = [("l", ctypes.c_long), ("t", ctypes.c_long), ("r", ctypes.c_long), ("b", ctypes.c_long)]


def size(hwnd):
    r = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r.r - r.l, r.b - r.t


print("before", "main", size(MAIN), "gfx", size(GFX), "zoomed", user32.IsZoomed(MAIN))
user32.ShowWindow(MAIN, SW_RESTORE)
time.sleep(0.4)
user32.SetWindowPos(MAIN, 0, 0, 0, 2560, 430, SWP_NOZORDER)
time.sleep(0.8)
print("after", "main", size(MAIN), "gfx", size(GFX))

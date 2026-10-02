import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
MAIN = 1511948
GFX = 1512752


class RECT(ctypes.Structure):
    _fields_ = [("l", ctypes.c_long), ("t", ctypes.c_long), ("r", ctypes.c_long), ("b", ctypes.c_long)]


def rect(hwnd):
    r = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r.l, r.t, r.r, r.b, r.r - r.l, r.b - r.t


print("main", user32.IsWindow(MAIN), rect(MAIN))
print("gfx", user32.IsWindow(GFX), rect(GFX))
print("zoom", user32.IsZoomed(MAIN))

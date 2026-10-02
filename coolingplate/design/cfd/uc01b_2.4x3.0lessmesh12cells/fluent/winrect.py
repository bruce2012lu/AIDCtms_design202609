import send_tui

user32 = send_tui.user32
rect = send_tui.RECT()
for hwnd in (1511948, 1512752, 2365066):
    ok = user32.GetWindowRect(hwnd, send_tui.ctypes.byref(rect))
    print(hwnd, ok, rect.l, rect.t, rect.r, rect.b)

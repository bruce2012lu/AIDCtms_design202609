"""Dismiss a popup, then print a marker at the top-level prompt."""
import time
import send_tui

send_tui.main_send("-")
time.sleep(0.3)
hwnd = send_tui.console_hwnd()
send_tui.tap(0x1B)
time.sleep(0.2)
send_tui.main_send('(display "PING2")')
print("sent-ping")

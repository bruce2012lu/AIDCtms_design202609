"""Accept coloring, then list the range-option submenu."""
import time
import send_tui

for line in ("smooth", "range-option", "auto-range-on", "-"):
    send_tui.main_send(line)
    time.sleep(0.55)
print("sent-rangeopt")

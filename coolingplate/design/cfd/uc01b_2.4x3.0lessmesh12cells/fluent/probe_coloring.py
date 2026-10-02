"""Leave color-map and list the coloring submenu."""
import time
import send_tui

for line in ("quit", "coloring", "-"):
    send_tui.main_send(line)
    time.sleep(0.45)
print("sent-coloring")

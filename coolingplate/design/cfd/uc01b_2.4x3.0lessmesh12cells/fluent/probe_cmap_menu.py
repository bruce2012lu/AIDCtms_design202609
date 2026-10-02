"""Enter color-map and list its settings. Assumes the object editor is open."""
import time
import send_tui

for line in ("color-map", "-"):
    send_tui.main_send(line)
    time.sleep(0.45)
print("sent-cmap")

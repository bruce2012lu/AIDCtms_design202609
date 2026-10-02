"""Open the p001t editor and press Enter so Fluent lists settings."""
import time
import send_tui

for line in ("/display/objects/edit", "p001t", "-"):
    send_tui.main_send(line)
    time.sleep(0.45)
print("sent-menu")

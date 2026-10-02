"""Try a readable object name. Stop before quit so a bad name cannot exit Fluent."""
import time
import send_tui

lines = [
    '(display "PING3")',
    "/display/objects/edit",
    "p001t",
    "name",
    "wall_heat",
]
for line in lines:
    send_tui.main_send(line)
    time.sleep(0.5)
print("sent-name-try")

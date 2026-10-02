"""Turn off global range on p001t and resave the wall_heat picture."""
import time
import send_tui

lines = [
    "global-range?",
    "no",
    "quit",
    "quit",
    "/display/objects/display",
    "p001t",
    "/display/save-picture",
    "D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd/uc01b_2.4x3.0lessmesh12cells/figs12cells/i300/wall_heat_temperature.png",
    "yes",
    '(display "AR5-DONE")',
]
for line in lines:
    send_tui.main_send(line)
    time.sleep(0.7 if line != "yes" else 1.2)
print("sent-local")

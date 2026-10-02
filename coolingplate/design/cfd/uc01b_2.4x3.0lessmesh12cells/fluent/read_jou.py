"""Read one journal from the top-level Fluent prompt. Path must contain no hyphen."""
import sys
import time
import send_tui

path = sys.argv[1].replace("\\", "/")
for line in ("/file/read-journal", path, "()"):
    send_tui.main_send(line)
    time.sleep(0.8)
print("sent-read")

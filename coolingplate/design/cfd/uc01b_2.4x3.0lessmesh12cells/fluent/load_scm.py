"""Load a Scheme file. The typed line has no hyphen."""
import sys
import send_tui

path = sys.argv[1].replace("\\", "/")
send_tui.main_send('(load "%s")' % path)
print("sent-load")

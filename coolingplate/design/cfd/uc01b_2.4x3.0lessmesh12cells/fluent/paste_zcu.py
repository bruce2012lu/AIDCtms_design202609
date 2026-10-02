import sys
import time
import console_paste
import force_paste

force_paste.force_front(console_paste.MAIN)
name = sys.argv[1] if len(sys.argv) > 1 else "read_zcu.txt"
text = open(name, encoding="utf-8").read().replace("\r\n", "\n")
if not text.endswith("\n"):
    text += "\n"
console_paste.focus_console()
console_paste.set_clip(text)
time.sleep(0.2)
console_paste.chord(0x56)
time.sleep(0.4)
force_paste.force_front(console_paste.MAIN)
console_paste.focus_console()
time.sleep(0.15)
console_paste.key_event(0x0D, False)
console_paste.key_event(0x0D, True)
print("pasted", console_paste.user32.GetForegroundWindow())

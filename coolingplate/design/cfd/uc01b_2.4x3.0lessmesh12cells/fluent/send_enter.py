import time
import console_paste
import force_paste

force_paste.force_front(console_paste.MAIN)
console_paste.focus_console()
time.sleep(0.2)
console_paste.key_event(0x0D, False)
console_paste.key_event(0x0D, True)
print("sent", console_paste.user32.GetForegroundWindow())

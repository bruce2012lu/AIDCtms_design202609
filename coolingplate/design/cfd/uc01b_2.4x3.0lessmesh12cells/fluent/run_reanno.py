import pathlib
import time

import console_paste
import click_graphics

for name in ("reanno.jou", "read_reanno.txt"):
    path = pathlib.Path(name)
    path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n"))

text = pathlib.Path("read_reanno.txt").read_text(encoding="ascii")
console_paste.focus_console()
console_paste.set_clip(text)
time.sleep(0.2)
console_paste.chord(0x56)
time.sleep(1.4)
console_paste.key_event(0x11, True)
time.sleep(0.2)
console_paste.key_event(0x0D, False)
console_paste.key_event(0x0D, True)

for _ in range(20):
    time.sleep(0.5)
    value = console_paste.console_value(console_paste.console_edit())
    if "attachment line" in value[-2500:] or "Pick a screen" in value[-2500:]:
        print("waiting for click")
        click_graphics.invoke_graphics()
        time.sleep(0.4)
        click_graphics.click_blank()
        break
    if "Interrupted" in value[-600:]:
        print(value[-900:])
        break
else:
    print(value[-900:])

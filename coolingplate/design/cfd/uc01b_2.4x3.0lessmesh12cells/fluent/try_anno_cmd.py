"""Try one annotation-edit command. Print whether Fluent accepts it."""
import pathlib
import sys
import time

import console_paste

CASE = pathlib.Path(__file__).resolve().parent
CMD = sys.argv[1]
JOU = CASE / "anno_cmd.jou"
READ = CASE / "read_anno_cmd.txt"
JOU.write_bytes(
    (
        '(display "CMD-%s")\n/display/annotation/edit\ntext-0\n%s\n' % (CMD, CMD)
    ).encode("ascii")
)
READ.write_bytes(
    (
        "/file/read-journal\n%s\n()\n" % JOU.as_posix()
    ).encode("ascii")
)
text = READ.read_text(encoding="ascii")
console_paste.focus_console()
console_paste.set_clip(text)
time.sleep(0.2)
console_paste.chord(0x56)
time.sleep(1.4)
console_paste.key_event(0x11, True)
time.sleep(0.2)
console_paste.key_event(0x0D, False)
console_paste.key_event(0x0D, True)
time.sleep(2.2)
v = console_paste.console_value(console_paste.console_edit())
i = v.rfind('CMD-%s' % CMD)
print(v[i:] if i >= 0 else v[-500:])

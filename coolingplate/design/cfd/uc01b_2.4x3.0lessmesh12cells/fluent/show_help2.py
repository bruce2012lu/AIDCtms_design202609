import console_paste

v = console_paste.console_value(console_paste.console_edit())
key = '(display "HELP2")'
i = v.rfind(key)
print("idx", i, "len", len(v))
print(v[i : i + 8000] if i >= 0 else "missing")

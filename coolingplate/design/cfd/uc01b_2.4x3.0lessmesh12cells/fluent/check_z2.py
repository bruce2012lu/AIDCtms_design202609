import console_paste

value = console_paste.console_value(console_paste.console_edit())
start = value.rfind("Z2-RECAP")
print("len", len(value), "start", start)
print(value[start:][-1600:] if start >= 0 else value[-600:])

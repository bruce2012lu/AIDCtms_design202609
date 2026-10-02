import console_paste

value = console_paste.console_value(console_paste.console_edit())
start = value.rfind("ZCU-BIG")
print(value[start:start + 2200])

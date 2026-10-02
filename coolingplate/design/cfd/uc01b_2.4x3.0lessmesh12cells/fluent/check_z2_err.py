import console_paste

value = console_paste.console_value(console_paste.console_edit())
start = value.rfind("Z2-RECAP")
chunk = value[start:]
print("errors", chunk.count("Error:"))
print(chunk[:1200])

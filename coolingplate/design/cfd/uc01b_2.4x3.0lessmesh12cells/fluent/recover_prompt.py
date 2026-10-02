"""Close the stuck (display \" TUI3\\) reader, then confirm the top prompt."""
import send_tui

send_tui.main_send('x")')
print("sent-close")

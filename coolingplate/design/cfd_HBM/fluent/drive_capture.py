# -*- coding: utf-8 -*-
"""Send the capture journal one line at a time, waiting until each line is echoed."""
import sys
import time
import paste_journal as p

user32 = p.user32
HWND = 9965858
CHILD = 4002548
JOU = r"d:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\fluent\hbm_cf_capture.jou"
TRANS = r"d:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\logs\hbm_cf_qfix.log"
PROGRESS = r"d:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd_HBM\logs\drive_capture.log"


def click(x, y):
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.12)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.06)
    user32.mouse_event(0x0004, 0, 0, 0, 0)


def focus_console():
    for vk in (0x11, 0x12, 0x10):
        user32.keybd_event(vk, 0, 2, 0)
    this = p.kernel32.GetCurrentThreadId()
    target = user32.GetWindowThreadProcessId(CHILD, None)
    user32.AttachThreadInput(this, target, True)
    user32.keybd_event(0x12, 0, 0, 0)
    time.sleep(0.04)
    user32.SetForegroundWindow(HWND)
    user32.SetFocus(CHILD)
    time.sleep(0.08)
    user32.keybd_event(0x12, 0, 2, 0)
    click(700, 830)
    return this, target


def send_line(text):
    for vk in (0x11, 0x12, 0x10):
        user32.keybd_event(vk, 0, 2, 0)
    p.set_clip(text)
    time.sleep(0.12)
    p.chord(0x56)
    time.sleep(0.12)
    p.key_event(0x11, True)
    time.sleep(0.05)
    p.key_event(0x0D, False)
    time.sleep(0.04)
    p.key_event(0x0D, True)


def read_trans():
    try:
        with open(TRANS, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def wait_for(token, pos, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = read_trans()
        tail = data[pos:]
        if (
            "enter choice again" in tail
            or "invalid command" in tail
            or "Invalid Surface" in tail
            or "unknown --" in tail
        ):
            raise SystemExit("console rejected a command")
        idx = data.find(token, pos)
        if idx >= 0:
            return idx + len(token)
        time.sleep(0.25)
    raise SystemExit("timeout waiting for " + token)


def timeout_for(text):
    if "save-picture" in text or "objects/display" in text or "auto-scale" in text:
        return 90
    if "plane-surface" in text or "iso-clip" in text or "objects/create" in text:
        return 40
    return 20


def main():
    lines = []
    for number, raw in enumerate(open(JOU, encoding="ascii"), start=1):
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith(";"):
            continue
        if line.startswith("/file/start-transcript"):
            continue
        if line.startswith("D:/agents2026") and line.endswith("hbm_cf_capture.log"):
            continue
        lines.append((number, line))
    start_jou = int(sys.argv[1]) if len(sys.argv) > 1 else 61
    lines = [(number, line) for number, line in lines if number >= start_jou]
    this, target = focus_console()
    progress = open(PROGRESS, "w", encoding="ascii")
    try:
        if start_jou > 1850:
            send_line("/file/start-transcript")
            time.sleep(0.4)
            send_line(TRANS.replace("\\", "/"))
            deadline = time.time() + 20
            while time.time() < deadline and "Opening" not in read_trans():
                time.sleep(0.3)
        pos = len(read_trans())
        progress.write("resume jou %d %s pos %d\n" % (lines[0][0], lines[0][1], pos))
        progress.flush()
        for index, (number, line) in enumerate(lines):
            send_line(line)
            pos = wait_for(line, pos, timeout_for(line))
            progress.write("%d %s\n" % (number, line))
            progress.flush()
            if line.strip() == '"None"':
                time.sleep(0.5)
                user32.keybd_event(0x12, 0, 0, 0)
                time.sleep(0.05)
                click(560, 902)
                time.sleep(0.4)
                user32.keybd_event(0x12, 0, 2, 0)
                click(1180, 240)
                time.sleep(0.5)
                click(460, 902)
                time.sleep(0.3)
                user32.AttachThreadInput(this, target, False)
                this, target = focus_console()
                progress.write("CLICK\n")
                progress.flush()
        progress.write("DRIVER-DONE\n")
    finally:
        user32.AttachThreadInput(this, target, False)
        progress.close()


if __name__ == "__main__":
    main()

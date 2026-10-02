p = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\fluent-20260927-160935-64124.trn"
raw = open(p, "rb").read()
key = b"report_resume.jou"
i = raw.rfind(key)
part = raw[i:]
print("errors after", part.count(b"Error:"))
print("interrupted after", part.count(b"Interrupted."))
print("pick after", part.count(b"Pick a screen"))
j = part.rfind(b"Error:")
if j >= 0:
    open(r"C:\Users\Administrator\trn_tail.txt", "w", encoding="utf-8").write(
        part[max(0, j - 500) : j + 250].decode("gbk", "replace")
    )
else:
    open(r"C:\Users\Administrator\trn_tail.txt", "w", encoding="utf-8").write(
        part[-400:].decode("gbk", "replace")
    )
print("tail written", len(part))

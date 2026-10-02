import time
p = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\fluent-20260927-160935-64124.trn"
raw = open(p, "rb").read()
i = raw.rfind(b"report_resume.jou")
part = raw[i:]
print("part", len(part))
for key in (
    b"Pick a screen",
    b"ANNO-PLACED",
    b"FONT24-DONE",
    b"CASE-I600-LOADED",
    b"SURFACES-I600-DONE",
    b"CAPTURE-I600-DONE",
    b"CAPTURE-ALL-DONE",
    b"Error:",
    b"Interrupted.",
):
    print(key.decode(), part.count(key))
k = part.rfind(b"SHOT ")
print("LAST", part[k : k + 80].decode("gbk", "replace").replace("\n", " | "))
print("END", part[-180:].decode("gbk", "replace"))

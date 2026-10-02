import pathlib
root = pathlib.Path(r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\fluent")
for name in ("read_i600_smooth.txt",):
    path = root / name
    path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
    print(name, path.read_bytes())

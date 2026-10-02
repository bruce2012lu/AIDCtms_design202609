import math
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LIB / "tools"))
sys.stdout.reconfigure(encoding="utf-8")
import correlations as c  # noqa: E402

N, SX, SY, H = 216, 3.0, 2.4, 2.0
L = math.sqrt(SX * SY)
A_GPU = 2 * 27e-3 * 28e-3
fluids = {
    "水 40°C NIST": dict(rho=992.216, mu=6.52729e-4, k=0.628486, cp=4179.41),
    "PG25 内部 PG25_40": dict(rho=1022, mu=1.15e-3, k=0.452, cp=3900),
    "PG25 Dow LC 0623 40°C(二手)": dict(rho=1022.5, mu=1.58e-3, k=0.476, cp=3920),
}
cases = [("水基线 v2.0", "水 40°C NIST", 1.60), ("PG25 设计点 v2.1", "PG25 内部 PG25_40", 2.283),
         ("PG25 设计点 v2.1", "PG25 Dow LC 0623 40°C(二手)", 2.283),
         ("PG25 原分配表上沿", "PG25 内部 PG25_40", 2.6), ("PG25 原分配表上沿", "PG25 Dow LC 0623 40°C(二手)", 2.6)]
print("| 工况 | 物性 | D mm | Q L/min | V m/s | Re | Pr | Nu_f(Wei,水) | Pr 修正后 Nu | h W/(m²K) | R_conv 平板 °C/W |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for name, fl, q in cases:
    f = fluids[fl]
    pr = f["mu"] * f["cp"] / f["k"]
    for d in (0.50, 0.40):
        v = q / 60000 / (N * math.pi * (d * 1e-3) ** 2 / 4)
        re = f["rho"] * v * d * 1e-3 / f["mu"]
        r = c.wei2021(d, L, H, re, pr, f["k"])
        rconv = 1 / (r["h_W_m2K"] * A_GPU)
        print(f"| {name} | {fl} | {d:.2f} | {q} | {v:.3f} | {re:.0f} | {pr:.2f} | {r['Nu_f_water']:.2f} | "
              f"{r['Nu_f']:.2f} | {r['h_W_m2K']:.0f} | {rconv:.4f} |")
print("L =", round(L, 3), "mm; H/L =", round(H / L, 3), "; A_GPU =", A_GPU, "m2")

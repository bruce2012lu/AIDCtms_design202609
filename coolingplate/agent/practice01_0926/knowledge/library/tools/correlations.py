"""射流冲击换热关联式（只收录已对照原文页面核对过的式子），带适用范围检查。

1. Wei et al. 2021, IJHMT 182:121865, Eq.(19), p.11（条目 pap-2021-wei-microjet-correlations-feed-drain）
   交替进液/排液（分布式出口）微射流阵列，单元胞 CFD 拟合 + 实验验证，误差 ±30 %：
       Nu_f = (5.64 a² + 0.031 a − 0.000632) · (H/L)^(−0.29) · Re_d^(0.48 · a^(−0.16))
       a = d_i/L = d_o/L，Nu_f = q·d_i / ((T_s − T_in)·k)，Re_d = ρ V_in d_i / μ，q 按单元胞（芯片）面积
   适用：0.01 ≤ a ≤ 0.4；0.01 ≤ H/L ≤ 0.4；32 ≤ Re_d ≤ 2048；0.05 ≤ H/d_i ≤ 20；0.01 ≤ t/L ≤ 0.4；
         Pr 固定 7.56（去离子水）。

2. Robinson & Schnitzler 2007（ETFS 32:1–13），转引自 Whelan & Robinson 2009 Eq.(2), p.10
   （条目 pap-2009-whelan-nozzle-geometry-jet-array；原文付费，条目 pap-2007-robinson-schnitzler-jet-array）
   受限淹没水射流阵列，边缘排液：
       Nu_L / Pr^0.4 = 23.39 · Re_d^0.46 · (S/d)^(−0.442) · (H/d)^(−0.00716)
       Nu_L 以加热面特征长度 L（原实验 L = 15.75 mm）为基准，不是孔径。
   适用：650 ≤ Re_d ≤ 6500；3 ≤ S/d ≤ 7；2 ≤ H/d ≤ 3；水。

可选 Pr 修正：Nu ∝ Pr^n。Li & Garimella 2001 给 n ≈ 0.44（Pr 0.7–25.2，单孔，Re 4000–23000；
条目 pap-2001-li-garimella-prandtl-jet，指数符号待原文核对），Robinson & Schnitzler 用 0.4。
把 Wei 式从 Pr = 7.56 外推到 PG25 时乘 (Pr/7.56)^n，这一步本身是外推。

用法
  python correlations.py wei --D 0.5 --Sx 3.0 --Sy 2.4 --H 2.0 --Re 478 --Pr 4.34 --k 0.6285
  python correlations.py rs  --D 0.5 --S 2.68 --H 2.0 --Re 478 --Pr 4.34
"""

from __future__ import annotations

import argparse
import json
import math
import sys

WEI_PR = 7.56


def _check(name: str, value: float, lo: float, hi: float) -> dict:
    return {"param": name, "value": round(value, 4), "range": [lo, hi], "in_range": lo <= value <= hi}


def wei2021_nu(a: float, h_over_l: float, re: float) -> float:
    return (5.64 * a ** 2 + 0.031 * a - 0.000632) * h_over_l ** -0.29 * re ** (0.48 * a ** -0.16)


def wei2021(D_mm: float, L_mm: float, H_mm: float, Re: float, Pr: float | None = None,
            k: float | None = None, t_mm: float | None = None, pr_exp: float = 0.44) -> dict:
    a = D_mm / L_mm
    hl = H_mm / L_mm
    checks = [_check("d_i/L", a, 0.01, 0.4), _check("H/L", hl, 0.01, 0.4),
              _check("Re_d", Re, 32, 2048), _check("H/d_i", H_mm / D_mm, 0.05, 20)]
    if t_mm is not None:
        checks.append(_check("t/L", t_mm / L_mm, 0.01, 0.4))
    nu = wei2021_nu(a, hl, Re)
    out = {"source": "pap-2021-wei-microjet-correlations-feed-drain Eq.(19) p.11", "uncertainty": "±30 %",
           "Nu_f_water": nu, "checks": checks, "all_in_range": all(c["in_range"] for c in checks)}
    if Pr is not None:
        corr = (Pr / WEI_PR) ** pr_exp
        out.update({"Pr": Pr, "Pr_correction": corr, "Pr_exponent": pr_exp, "Nu_f": nu * corr,
                    "Pr_note": "原式 Pr 固定 7.56；Pr 修正为外推"})
        out["all_in_range"] = out["all_in_range"] and abs(Pr - WEI_PR) < 1e-9
    if k is not None:
        nu_used = out.get("Nu_f", nu)
        out["h_W_m2K"] = nu_used * k / (D_mm * 1e-3)
    return out


def robinson_schnitzler(D_mm: float, S_mm: float, H_mm: float, Re: float, Pr: float) -> dict:
    s = S_mm / D_mm
    hd = H_mm / D_mm
    checks = [_check("Re_d", Re, 650, 6500), _check("S/d", s, 3, 7), _check("H/d", hd, 2, 3)]
    nu_l = 23.39 * Re ** 0.46 * s ** -0.442 * hd ** -0.00716 * Pr ** 0.4
    return {"source": "Whelan & Robinson 2009 Eq.(2) p.10（转引 Robinson & Schnitzler 2007）",
            "Nu_L": nu_l, "note": "Nu_L 以加热面特征长度为基准（原实验 L = 15.75 mm），换算 h 需用同一 L",
            "checks": checks, "all_in_range": all(c["in_range"] for c in checks)}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="correlations", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("wei", help="Wei 2021 Eq.(19)")
    w.add_argument("--D", type=float, required=True, help="进液孔径 mm")
    w.add_argument("--L", type=float, help="单元胞边长 mm；不给则用 sqrt(Sx·Sy)")
    w.add_argument("--Sx", type=float)
    w.add_argument("--Sy", type=float)
    w.add_argument("--H", type=float, required=True)
    w.add_argument("--Re", type=float, required=True)
    w.add_argument("--Pr", type=float)
    w.add_argument("--k", type=float, help="流体导热 W/(m·K)，给出则输出 h")
    w.add_argument("--t", type=float, help="喷嘴板厚 mm")
    w.add_argument("--pr-exp", type=float, default=0.44)
    r = sub.add_parser("rs", help="Robinson & Schnitzler 2007")
    r.add_argument("--D", type=float, required=True)
    r.add_argument("--S", type=float, required=True)
    r.add_argument("--H", type=float, required=True)
    r.add_argument("--Re", type=float, required=True)
    r.add_argument("--Pr", type=float, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "wei":
        L = a.L or (math.sqrt(a.Sx * a.Sy) if a.Sx and a.Sy else None)
        if L is None:
            ap.error("需要 --L 或 --Sx --Sy")
        res = wei2021(a.D, L, a.H, a.Re, a.Pr, a.k, a.t, a.pr_exp)
    else:
        res = robinson_schnitzler(a.D, a.S, a.H, a.Re, a.Pr)
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

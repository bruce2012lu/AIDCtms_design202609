"""网格收敛指数（GCI）计算器，按 Celik et al. 2008 的五步法（Roache 1994 GCI 的标准化写法）。

出处
  Celik, I.B., Ghia, U., Roache, P.J., Freitas, C.J., Coleman, H., Raad, P.E. (2008)
  "Procedure for Estimation and Reporting of Uncertainty Due to Discretization in CFD Applications",
  J. Fluids Eng. 130(7):078001. 知识库条目 pap-2008-celik-gci-procedure。
  Roache, P.J. (1994) "Perspective: A Method for Uniform Reporting of Grid Refinement Studies",
  J. Fluids Eng. 116(3):405–413。

记号：下标 1 为最细网格，3 为最粗。φ 为关心的量（如 TIM 面平均温度、压降）。

  第 1 步  代表网格尺寸   h = [ (1/N) Σ ΔV_i ]^(1/3)      （三维；也可直接给 h）
  第 2 步  加密比         r21 = h2/h1，r32 = h3/h2，建议 r > 1.3
  第 3 步  表观阶数 p（定点迭代）
           ε21 = φ2 − φ1，ε32 = φ3 − φ2，s = sign(ε32/ε21)
           p = | ln|ε32/ε21| + q(p) | / ln r21
           q(p) = ln( (r21^p − s) / (r32^p − s) )
  第 4 步  外推值         φ_ext^21 = (r21^p φ1 − φ2) / (r21^p − 1)
  第 5 步  相对误差与 GCI
           e_a^21   = |(φ1 − φ2)/φ1|
           e_ext^21 = |(φ_ext^21 − φ1)/φ_ext^21|
           GCI_fine^21 = Fs · e_a^21 / (r21^p − 1)，三套网格 Fs = 1.25
  渐近范围检查  GCI^32 / (r21^p · GCI^21) ≈ 1
           本工具按绝对量计算：(GCI^32·|φ2|) / (r21^p · GCI^21·|φ1|) = |ε32| / (r21^p · |ε21|)·(r21^p−1)/(r32^p−1)

  s < 0（振荡收敛）时 Celik 建议报告振荡，并按 |ε| 的范围给不确定度；本工具标出 oscillatory=True。
  只有两套网格时不能求 p，用 Roache 的 Fs = 3.0 与理论阶数 p_formal：GCI = 3.0·e_a/(r^p_formal − 1)。

用法
  python gci.py --phi 6.063 5.972 5.863 --N 18000 8000 4500
  python gci.py --phi 341.385 342.096 --r 1.3 --p-formal 2
"""

from __future__ import annotations

import argparse
import json
import math
import sys


def rep_h(n_cells: float, volume: float = 1.0, dim: int = 3) -> float:
    return (volume / n_cells) ** (1.0 / dim)


def apparent_order(e21: float, e32: float, r21: float, r32: float, tol: float = 1e-10, max_iter: int = 200) -> tuple[float, int, bool]:
    if e21 == 0 or e32 == 0:
        raise ValueError("相邻两套网格结果相同，无法求表观阶数")
    s = math.copysign(1.0, e32 / e21)
    ratio = abs(e32 / e21)
    p = abs(math.log(ratio)) / math.log(r21)
    for it in range(1, max_iter + 1):
        q = math.log((r21 ** p - s) / (r32 ** p - s))
        p_new = abs(math.log(ratio) + q) / math.log(r21)
        if abs(p_new - p) < tol:
            return p_new, it, s < 0
        p = p_new
    return p, max_iter, s < 0


def gci3(phi1: float, phi2: float, phi3: float, r21: float, r32: float, fs: float = 1.25) -> dict:
    e21, e32 = phi2 - phi1, phi3 - phi2
    p, iters, osc = apparent_order(e21, e32, r21, r32)
    a21 = r21 ** p
    a32 = r32 ** p
    phi_ext21 = (a21 * phi1 - phi2) / (a21 - 1)
    phi_ext32 = (a32 * phi2 - phi3) / (a32 - 1)
    ea21 = abs((phi1 - phi2) / phi1)
    ea32 = abs((phi2 - phi3) / phi2)
    eext21 = abs((phi_ext21 - phi1) / phi_ext21)
    gci21 = fs * ea21 / (a21 - 1)
    gci32 = fs * ea32 / (a32 - 1)
    return {
        "r21": r21, "r32": r32, "p": p, "iterations": iters, "oscillatory": osc,
        "phi_ext21": phi_ext21, "phi_ext32": phi_ext32,
        "ea21": ea21, "ea32": ea32, "eext21": eext21,
        "gci_fine21": gci21, "gci_32": gci32,
        "asymptotic_ratio": (gci32 * abs(phi2)) / (a21 * gci21 * abs(phi1)) if gci21 else float("nan"),
        "uncertainty_abs": gci21 * abs(phi1),
        "Fs": fs,
    }


def gci2(phi1: float, phi2: float, r: float, p_formal: float, fs: float = 3.0) -> dict:
    ea = abs((phi1 - phi2) / phi1)
    gci = fs * ea / (r ** p_formal - 1)
    return {"r": r, "p_formal": p_formal, "ea21": ea, "gci_fine21": gci,
            "uncertainty_abs": gci * abs(phi1), "Fs": fs,
            "warning": "两套网格不能验证渐近收敛，只能作保守估计"}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="gci", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phi", type=float, nargs="+", required=True, help="由细到粗：φ1 φ2 [φ3]")
    ap.add_argument("--N", type=float, nargs="+", help="由细到粗的网格数，三维下由 N 求 h")
    ap.add_argument("--h", type=float, nargs="+", help="由细到粗的代表尺寸，优先于 --N")
    ap.add_argument("--r", type=float, nargs="+", help="直接给加密比 r21 [r32]")
    ap.add_argument("--dim", type=int, default=3)
    ap.add_argument("--p-formal", type=float, default=2.0, help="两套网格时的理论阶数")
    ap.add_argument("--fs", type=float, help="安全系数，三网格默认 1.25，两网格默认 3.0")
    a = ap.parse_args(argv)
    if a.h:
        hs = a.h
    elif a.N:
        hs = [rep_h(n, dim=a.dim) for n in a.N]
    else:
        hs = None
    if hs:
        rs = [hs[i + 1] / hs[i] for i in range(len(hs) - 1)]
    elif a.r:
        rs = a.r
    else:
        ap.error("需要 --N、--h 或 --r 之一")
    if len(a.phi) == 3:
        res = gci3(*a.phi, rs[0], rs[1], a.fs or 1.25)
    elif len(a.phi) == 2:
        res = gci2(*a.phi, rs[0], a.p_formal, a.fs or 3.0)
    else:
        ap.error("--phi 给 2 或 3 个值")
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

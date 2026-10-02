# -*- coding: utf-8 -*-
"""PG25 物性对照、拟合与流量重算（2026-10-02，只读核算，不被其他模块引用）。

数据：
  TDS   DOWFROST LC 25 技术数据表（25 vol%），与 INTERCOOL DC-300 25% 公告同表
  GUIDE DOWFROST LC 工程与操作指南表 2（25 vol%）
  MPG   CoolProp INCOMP::MPG（Melinder 2010，质量分数），按 MPG.json 系数手算，未安装 CoolProp
  MODEL design/calc/model.py 的 PG25_40
运行：python pg25_props_calc_20261002.py
"""
import math

import numpy as np

T_TAB = [20, 25, 30, 35, 40, 45, 50, 55]
TDS = {  # rho kg/m3, cp kJ/kgK, k W/mK, mu mPa s
    20: (1032.7, 3.87, 0.456, 2.84), 25: (1030.3, 3.88, 0.462, 2.39),
    30: (1027.8, 3.89, 0.467, 2.05), 35: (1025.2, 3.90, 0.472, 1.78),
    40: (1022.5, 3.92, 0.476, 1.58), 45: (1019.7, 3.93, 0.481, 1.41),
    50: (1016.8, 3.94, 0.485, 1.27), 55: (1013.7, 3.95, 0.488, 1.15),
}
GUIDE = {
    20: (1033.7, 3.87, 0.456, 2.48), 25: (1031.5, 3.88, 0.462, 2.12),
    30: (1029.3, 3.89, 0.467, 1.82), 35: (1026.9, 3.90, 0.472, 1.59),
    40: (1024.4, 3.92, 0.476, 1.39), 45: (1021.7, 3.93, 0.481, 1.23),
    50: (1019.0, 3.94, 0.485, 1.10), 55: (1016.1, 3.95, 0.488, 0.99),
}
MODEL = (1022.0, 3.900, 0.452, 1.15)

# CoolProp MPG.json：行 = (T-Tbase) 幂次 0..3，列 = (x-xbase) 幂次 0..5
TBASE, XBASE = 305.8583, 0.307031
C_RHO = [[1018.0, 76.04, -24.98, -155.0, -113.1, 234.2],
         [-0.5406, -0.945, 0.27, 2.829, -2.221, 0.0],
         [-0.002666, 0.005541, -0.004018, -0.007175, 0.0, 0.0],
         [1.347e-05, -1.343e-05, 3.376e-05, 0.0, 0.0, 0.0]]
C_CP = [[3882.0, -1304.0, -1598.0, 353.9, 5000.0, -4959.0],
        [2.699, 5.07, 0.9534, 31.02, -71.35, 0.0],
        [-0.001659, -0.004752, 0.1167, -0.295, 0.0, 0.0],
        [-1.032e-05, 0.0001522, -0.000487, 0.0, 0.0, 0.0]]
C_K = [[0.4513, -0.4795, 0.2076, -0.09083, -0.05952, 0.2104],
       [0.0007955, -0.001678, 0.001563, -0.002518, -0.003605, 0.0],
       [3.482e-08, 8.941e-06, -4.615e-05, 6.543e-05, 0.0, 0.0],
       [-5.966e-09, 1.493e-08, 9.897e-08, 0.0, 0.0, 0.0]]
C_MU = [[-6.224055, 3.328, 0.5453, -3.9, -1.587, 35.64],
        [-0.03045, -0.03984, -0.00086, 0.1054, 0.04475, 0.0],
        [0.0002525, 0.0004332, -0.0001593, -0.001589, 0.0, 0.0],
        [-1.399e-06, -1.86e-06, -4.465e-07, 0.0, 0.0, 0.0]]
C_TF = [259.9, -66.31, -109.4, -228.3, -340.9, 146.5]


def _poly(c, t_c, x):
    dt, dx = t_c + 273.15 - TBASE, x - XBASE
    return sum(c[i][j] * dt ** i * dx ** j for i in range(len(c)) for j in range(len(c[0])))


def mpg(t_c, x):
    """返回 rho, cp(kJ/kgK), k, mu(mPa s)，x 为质量分数。"""
    return (_poly(C_RHO, t_c, x), _poly(C_CP, t_c, x) / 1000.0,
            _poly(C_K, t_c, x), math.exp(_poly(C_MU, t_c, x)) * 1000.0)


def mpg_tfreeze(x):
    dx = x - XBASE
    return sum(c * dx ** j for j, c in enumerate(C_TF)) - 273.15


def interp(tab, t):
    ts = sorted(tab)
    for a, b in zip(ts, ts[1:]):
        if a <= t <= b:
            w = (t - a) / (b - a)
            ra, rb = tab[a], tab[b]
            out = [ra[i] + w * (rb[i] - ra[i]) for i in range(3)]
            out.append(math.exp(math.log(ra[3]) + w * (math.log(rb[3]) - math.log(ra[3]))))
            return tuple(out)
    raise ValueError(t)


def fit(tab):
    t = np.array(T_TAB, float)
    arr = np.array([tab[x] for x in T_TAB])
    rho = np.polyfit(t, arr[:, 0], 2)
    cp = np.polyfit(t, arr[:, 1], 1)
    k = np.polyfit(t, arr[:, 2], 2)
    # ln(mu) = A + B / (T + C)，C 网格搜索
    best = None
    for c in np.arange(10.0, 300.0, 0.5):
        b, a = np.polyfit(1.0 / (t + c), np.log(arr[:, 3]), 1)
        err = np.max(np.abs(np.exp(a + b / (t + c)) / arr[:, 3] - 1))
        if best is None or err < best[0]:
            best = (err, a, b, c)
    return rho, cp, k, best


def props_fit(f, t):
    rho, cp, k, (_, a, b, c) = f
    return (np.polyval(rho, t), np.polyval(cp, t), np.polyval(k, t), math.exp(a + b / (t + c)))


def pr(p):
    return p[3] * 1e-3 * p[1] * 1e3 / p[2]


def flow(f, power, dT, t_in):
    """返回按供液温度计的体积流量 L/min 与平均液温。"""
    tm = t_in + dT / 2.0
    rho_m, cp_m, _, _ = props_fit(f, tm)
    m = power / (cp_m * 1e3 * dT)
    rho_in = props_fit(f, t_in)[0]
    return m / rho_in * 60000.0, m / rho_m * 60000.0, tm


def dT_at(f, power, q_in_lpm, t_in):
    dT = 6.0
    for _ in range(30):
        rho_in = props_fit(f, t_in)[0]
        cp_m = props_fit(f, t_in + dT / 2.0)[1]
        dT = power / (rho_in * q_in_lpm / 60000.0 * cp_m * 1e3)
    return dT


def main():
    print("== 对照表 20..50 °C：rho cp k mu Pr")
    for t in [20, 25, 30, 35, 40, 45, 50]:
        row = [f"{t:>3}"]
        for name, p in (("TDS", TDS[t]), ("GUIDE", GUIDE[t]),
                        ("MPG25wt", mpg(t, 0.25)), ("MPG25.6wt", mpg(t, 0.256))):
            row.append(f"{name}: {p[0]:.1f} {p[1]:.3f} {p[2]:.3f} {p[3]:.3f} Pr={pr(p):.2f}")
        print(" | ".join(row))
    print("MODEL 40C:", MODEL, f"Pr={pr(MODEL):.2f}")
    print("MPG water check 40C:", [round(v, 4) for v in mpg(40, 0.0)])
    print(f"MPG Tfreeze 25wt / 25.6wt: {mpg_tfreeze(0.25):.2f} / {mpg_tfreeze(0.256):.2f}")

    print("\n== MODEL 每项对应的等值温度")
    for i, nm in enumerate(["rho", "cp", "k", "mu"]):
        hits = []
        for name, tab in (("TDS", TDS), ("GUIDE", GUIDE)):
            for t in np.arange(200, 551) / 10.0:
                if abs(interp(tab, t)[i] - MODEL[i]) / MODEL[i] < 0.002:
                    hits.append(f"{name}@{t:.1f}")
                    break
        print(nm, MODEL[i], hits)
    for x in np.arange(0.10, 0.40, 0.001):
        if abs(mpg(40, x)[3] - 1.15) < 0.005:
            print("MPG 40C mu=1.15 at x=%.3f wt" % x)
            break
    for x in np.arange(0.10, 0.40, 0.001):
        if abs(mpg(40, x)[2] - 0.452) < 0.0015:
            print("MPG 40C k=0.452 at x=%.3f wt" % x)
            break

    ftds, fguide = fit(TDS), fit(GUIDE)
    for nm, f in (("TDS", ftds), ("GUIDE", fguide)):
        rho, cp, k, (err, a, b, c) = f
        print(f"\n== 拟合 {nm}")
        print("rho =", np.round(rho, 6), " cp(kJ) =", np.round(cp, 6), " k =", np.round(k, 8))
        print(f"ln(mu_mPas) = {a:.5f} + {b:.3f}/(T+{c:.1f})  maxrelerr={err*100:.2f}%")
        for t in T_TAB:
            p, ref = props_fit(f, t), (TDS if nm == "TDS" else GUIDE)[t]
            print(t, [round(v, 4) for v in p], "tab", ref)

    print("\n== 推荐（TDS）35/40/43/44/45 °C")
    for t in [35, 40, 43, 44, 45, 48, 50]:
        p = props_fit(ftds, t)
        print(t, f"rho={p[0]:.1f} cp={p[1]*1e3:.0f} k={p[2]:.4f} mu={p[3]:.3f} Pr={pr(p):.2f}")

    for t_in in (40.0, 45.0):
        print(f"\n== 流量重算 供液 {t_in} °C")
        for nm, f in (("TDS", ftds), ("GUIDE", fguide)):
            for dT in (6.0, 8.0, 10.0):
                q_in, q_m, tm = flow(f, 1400.0, dT, t_in)
                dT11 = dT_at(f, 1100.0, q_in, t_in)
                print(f"{nm} dT={dT:.0f} Tm={tm:.1f} Q_in={q_in:.4f} Q_mean={q_m:.4f} L/min"
                      f"  1100W同流量 dT={dT11:.3f} K  vs3.512 {((q_in/3.512)-1)*100:+.2f}%")
        dT_v21 = dT_at(ftds, 1400.0, 3.512, t_in)
        print(f"3.512 L/min @1400W TDS dT={dT_v21:.3f}  @1100W dT={dT_at(ftds, 1100.0, 3.512, t_in):.3f}")
    q_model = 1400 / (MODEL[0] * MODEL[1] * 1e3 * 6) * 60000
    print("MODEL 6K:", round(q_model, 4))
    cdu = 1400 / (1025 * 3780 * 6) * 60000
    print("CDU set (1025, 3.78) 6K:", round(cdu, 4))

    print("\n== 粘度比（相对 MODEL 1.15）")
    for t in (40, 43, 44, 45):
        print(t, "TDS", round(props_fit(ftds, t)[3] / 1.15, 3), "GUIDE",
              round(props_fit(fguide, t)[3] / 1.15, 3), "MPG25", round(mpg(t, 0.25)[3] / 1.15, 3))


if __name__ == "__main__":
    main()

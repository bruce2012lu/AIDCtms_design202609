# -*- coding: utf-8 -*-
"""CP-GRACE-MC-01 one-dimensional check, Y-staggered channels.

Report axes: +X tray width (left fitting to right fitting),
+Y tray depth toward the rear panel, +z from the chip face into the cover.

Channels stay along Y. Odd channels (count from small X) flow +Y,
even channels flow -Y. Both Y-ends are walled. Fluid enters and leaves
through Z-ports. Water at 40 C.

Friction is fully developed laminar f = 64/Re. Each channel has two
Z-turns, K = 1.5 each. Nu = 4.8 is an assumption for a 3-side-heated
rectangular channel, not a fitted correlation.

The wall-temperature sweep is a lumped copper/fluid balance on one pair.
It is a screening estimate, not a conjugate CFD result.
"""
import math

rho = 992.0
cp = 4179.0
mu = 6.53e-4
k_f = 0.632
k_cu = 390.0
P = 300.0
dT_set = 8.0
mdot = P / (cp * dT_set)
Q = mdot / rho * 60 * 1000  # L/min
print("Q_L/min", round(Q, 4), "mdot", round(mdot, 6))

# Two 90-degree turns, inlet and outlet, referenced to channel velocity.
K_TURN = 1.5 + 1.5


def branch(name, power, n, w_mm, d_mm, L_fric_mm, L_heat_mm):
    q = Q * (power / P) / 1000.0 / 60.0
    w, d = w_mm * 1e-3, d_mm * 1e-3
    L_f, L_h = L_fric_mm * 1e-3, L_heat_mm * 1e-3
    Dh = 2 * w * d / (w + d)
    A = n * w * d
    V = q / A
    Re = rho * V * Dh / mu
    f = 64.0 / Re
    dP = (f * (L_f / Dh) + K_TURN) * rho * V * V / 2.0
    Nu = 4.8
    h = Nu * k_f / Dh
    Awet = n * L_h * (w + 2 * d)
    R = 1.0 / (h * Awet)
    print(
        name,
        "Q", round(q * 60 * 1000, 4),
        "V", round(V, 3),
        "Re", round(Re, 1),
        "Dh_mm", round(Dh * 1000, 3),
        "dP_kPa", round(dP / 1000, 3),
        "h", round(h, 0),
        "R", round(R, 4),
        "dT_conv", round(power * R, 2),
        "dT_fluid", round(power / (q * rho * cp), 2),
    )
    return dP, h, q


dP_cpu, h_cpu, q_cpu = branch("CPU", 260, 48, 0.40, 1.20, 40.0, 32.0)
dP_mem, h_mem, q_mem = branch("MEM_ONE", 20, 6, 1.20, 0.80, 78.0, 70.0)

gap = dP_cpu - dP_mem
w_s, d_s = 0.80e-3, 1.20e-3
Dh_s = 2 * w_s * d_s / (w_s + d_s)
V_s = q_mem / (w_s * d_s)
Re_s = rho * V_s * Dh_s / mu
dyn = rho * V_s * V_s / 2.0
L_s = (gap / dyn - K_TURN) * Dh_s * Re_s / 64.0
print(
    "MEM_SLIT",
    "gap_kPa", round(gap / 1000, 3),
    "V", round(V_s, 3),
    "L_mm", round(L_s * 1000, 2),
    "section_mm", "0.80x1.20",
)

Q_m3s = Q / 1000.0 / 60.0
dP_orifice = 10000.0 - dP_cpu
Cd = 0.62
A_o = Q_m3s / (Cd * math.sqrt(2 * dP_orifice / rho))
d_mm = math.sqrt(4 * A_o / math.pi) * 1000
print(
    "orifice dP_kPa", round(dP_orifice / 1000, 2),
    "ID_mm", round(d_mm, 2),
    "four_hole_mm", round(d_mm / math.sqrt(4), 2),
)
print("tube_V", round(Q_m3s / (math.pi * 0.003 ** 2), 3))
print("q_cpu_W_cm2", round(260 / (40 * 32 / 100.0), 2))
print("q_mem_W_cm2", round(20 / (50 * 70 / 100.0), 2))


def duct(name, flow_m3s, w_mm, d_mm, L_mm, k_minor):
    w, d, L = w_mm * 1e-3, d_mm * 1e-3, L_mm * 1e-3
    Dh = 2 * w * d / (w + d)
    V = flow_m3s / (w * d)
    Re = rho * V * Dh / mu
    f = 64.0 / Re if Re > 1.0 else 0.0
    dP = (f * (L / Dh) + k_minor) * rho * V * V / 2.0
    print(name, "V", round(V, 3), "Re", round(Re, 0), "dP_kPa", round(dP / 1000, 3))
    return dP


# Left rail is 7 mm wide and 5 mm deep (base plus cover), full flow, full length.
duct("LEFT_RAIL", Q_m3s, 7.0, 5.0, 84.0, 1.0)
# One CPU supply feeder carries half the CPU flow (one direction).
duct("CPU_FEEDER", q_cpu / 2.0, 8.0, 2.5, 40.0, 1.0)


def wall_sweep(counterflow, nseg=32):
    """One +Y/-Y pair, or two co-flow channels, under the 32 mm die."""
    L = 32e-3
    dx = L / nseg
    pitch = 0.80e-3
    t_base = 2.0e-3
    rib_w, rib_h = 0.40e-3, 1.20e-3
    A_cu = 2 * pitch * t_base + 2 * rib_w * rib_h
    perim = 0.40e-3 + 2 * 1.20e-3
    q_flux = 260.0 / (0.040 * 0.032)
    q_pair = q_flux * (2 * pitch) * dx
    m_ch = q_cpu * rho / 48.0
    h = h_cpu
    Tw = [52.0] * nseg
    TfA = [40.0] * nseg
    TfB = [40.0] * nseg
    for _ in range(8000):
        T_in_A = 40.0
        T_in_B = 40.0
        for i in range(nseg):
            Tf = T_in_A
            dTf = h * perim * dx * (Tw[i] - Tf) / (m_ch * cp + 0.5 * h * perim * dx)
            TfA[i] = Tf + 0.5 * dTf
            T_in_A = Tf + dTf
        if counterflow:
            for i in range(nseg - 1, -1, -1):
                Tf = T_in_B
                dTf = h * perim * dx * (Tw[i] - Tf) / (m_ch * cp + 0.5 * h * perim * dx)
                TfB[i] = Tf + 0.5 * dTf
                T_in_B = Tf + dTf
        else:
            for i in range(nseg):
                Tf = T_in_B
                dTf = h * perim * dx * (Tw[i] - Tf) / (m_ch * cp + 0.5 * h * perim * dx)
                TfB[i] = Tf + 0.5 * dTf
                T_in_B = Tf + dTf
        max_err = 0.0
        for i in range(nseg):
            G = k_cu * A_cu / dx
            cond = 0.0
            coef = 0.0
            if i > 0:
                cond += G * Tw[i - 1]
                coef += G
            if i < nseg - 1:
                cond += G * Tw[i + 1]
                coef += G
            conv = h * perim * dx
            rhs = q_pair + cond + conv * (TfA[i] + TfB[i])
            coef = coef + 2 * conv
            new = rhs / coef
            max_err = max(max_err, abs(new - Tw[i]))
            Tw[i] = 0.5 * Tw[i] + 0.5 * new
        if max_err < 1e-5:
            break
    return max(Tw) - min(Tw), Tw[0] - 40.0, Tw[-1] - 40.0, Tw


dT_ctr, t0_c, t1_c, Tw_c = wall_sweep(True)
dT_co, t0_p, t1_p, Tw_p = wall_sweep(False)
print(
    "WALL_COUNTER",
    "dTy", round(dT_ctr, 2),
    "rise_front", round(t0_c, 2),
    "rise_rear", round(t1_c, 2),
)
print(
    "WALL_COFLOW",
    "dTy", round(dT_co, 2),
    "rise_front", round(t0_p, 2),
    "rise_rear", round(t1_p, 2),
)
print("TW_C", " ".join(str(round(t - 40.0, 2)) for t in Tw_c[::4]))
print("TW_P", " ".join(str(round(t - 40.0, 2)) for t in Tw_p[::4]))

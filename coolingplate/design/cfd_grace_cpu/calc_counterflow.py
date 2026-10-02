# -*- coding: utf-8 -*-
"""Counterflow along plate Y versus the parallel-Y baseline.

Water at 40 C, same properties as CP-GRACE-MC-01_calc.py.
Nu = 4.8 is still an assumption for a 3-side-heated rectangle, not a CFD result.
The lateral-conduction estimate is lumped. It is not a substitute for the mesh.
"""
import math

rho = 992.0
cp = 4179.0
mu = 6.53e-4
k = 0.632
k_cu = 390.0
q_dot = 0.47  # L/min, CPU share
power = 260.0
q_flux = power / (0.040 * 0.032)


def hydraulics(name, n, w_mm, d_mm, L_mm):
    q = q_dot / 1000.0 / 60.0
    w, d, L = w_mm * 1e-3, d_mm * 1e-3, L_mm * 1e-3
    dh = 2 * w * d / (w + d)
    area = n * w * d
    v = q / area
    re = rho * v * dh / mu
    f = 64.0 / re
    k_loss = 0.5 + 0.81
    dp = (f * (L / dh) + k_loss) * rho * v * v / 2.0
    nu = 4.8
    h = nu * k / dh
    awet = n * L * (w + 2 * d)
    r_conv = 1.0 / (h * awet)
    mdot = q * rho
    dt_fluid = power / (mdot * cp)
    print(
        name,
        "n", n,
        "L_mm", L_mm,
        "V", round(v, 3),
        "Re", round(re, 1),
        "dP_kPa", round(dp / 1000, 3),
        "h", round(h, 0),
        "R", round(r_conv, 4),
        "dT_conv", round(power * r_conv, 2),
        "dT_fluid", round(dt_fluid, 2),
    )
    return {
        "v": v, "re": re, "dp": dp, "h": h, "dh": dh,
        "dt_fluid": dt_fluid, "dt_conv": power * r_conv,
        "perim": w + 2 * d, "pitch": 0.80e-3, "w": w, "d": d,
    }


print("q_flux_W_m2", round(q_flux, 1))
old = hydraulics("parallel_Y", 48, 0.40, 1.20, 32)
new = hydraulics("counter_Y", 48, 0.40, 1.20, 32)

# Two 90-degree turns per channel, K=1.5 each, based on channel velocity.
k_turn = 1.5 * 2
dp_turn = k_turn * rho * new["v"] ** 2 / 2.0
print("turn_dP_kPa", round(dp_turn / 1000, 3), "K_sum", k_turn)

# Lateral coupling between a +Y channel and its -Y neighbor.
# Rib: thickness = channel pitch - channel width. Floor: 2 mm over one pitch.
rib_t = 0.40e-3
g_rib = k_cu * new["d"] / rib_t
g_floor = k_cu * 2.0e-3 / new["pitch"]
g = g_rib + g_floor
c = new["h"] * new["perim"]
factor = c / (c + 2.0 * g)
dt_wall = factor * new["dt_fluid"]
print("G_rib", round(g_rib, 1), "G_floor", round(g_floor, 1), "C", round(c, 2))
print("wall_dT_over_fluid_dT", round(factor, 4))
print("counterflow_wall_to_wall_K", round(dt_wall, 3))
print("parallel_streamwise_copper_K", round(old["dt_fluid"], 2))

# Axial conduction along one pitch cannot flatten the parallel-flow rise.
a_floor = new["pitch"] * 2.0e-3
r_axial = 0.032 / (k_cu * a_floor)
print("axial_R_K_per_W", round(r_axial, 1), "axial_Q_for_8K_W", round(8.0 / r_axial, 3))

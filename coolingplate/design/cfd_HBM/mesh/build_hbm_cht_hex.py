# -*- coding: utf-8 -*-
"""HBM 冷却区共轭六面体网格（ICEM blocking 的边分布）。

几何来自 design/calc/model.py 与 cad/params/cp_b300_jm01.yaml，
封闭槽：上铜板 4.0 + 槽 2.0 + 余铜 2.0。肋从槽底接到上铜板。
上铜板厚度留给两端的进口腔和出口腔，加热段槽顶封死。
槽 0.80 x 2.00 mm，肋 0.80 mm，单侧 7 条，两岸各 0.30 mm，列长 50 mm。
流体壁面首层 8 um、增长比 <= 1.2、不少于 10 层，使 DP-B 槽道剪切下 y+ < 1。
固体界面第一层 <= 16 um、厚向不少于 6 层。流体/铜/TIM 共节点。

单位：脚本内 mm，写出的 msh 为 m。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ICEM = ROOT / "icem"

# ---- 封闭槽 mm：0.80 槽 + 0.80 肋，单侧 7 条，高 2.00；上铜板 4.00 ----
CH_W = 0.80
CH_H = 2.00
FIN_W = 0.80
PITCH = CH_W + FIN_W
N_CH = 7
LAND = (11.0 - ((N_CH - 1) * PITCH + CH_W)) / 2.0  # 0.30
COL_L = 50.0
T_LID = 4.0
T_BASE = 2.0
T_TIM = 0.080
DH_GROOVE = 2.0 * CH_W * CH_H / (CH_W + CH_H)  # 1.143 mm
LE = 10.0 * DH_GROOVE          # 延长段 >= 10 Dh

# 流体边界层（槽道剪切，不是射流驻点的 3 um）
H1_F = 0.008
GR_F = 1.20
HMAX_F = 0.12
# 固体：界面层不大于流体首层的 2 倍，厚向至少 6 层
H1_S = 0.016
GR_S = 1.50
HMAX_S = 0.40
N_TIM = 6

# 流向
H1_Y = 0.050
GR_Y = 1.20
HMAX_Y = 0.55
HMAX_EXT = 0.80

# 热源：四颗堆叠在列坐标内的位置（出口端为 0）
STACKS = ((0.0, 11.0), (13.0, 24.0), (26.0, 37.0), (39.0, 50.0))
Q_FLUX = 2.05e5  # W/m2 = 20.5 W/cm2
K_EFF_TIM = 8.818342  # 与 UC-01b 默认 TIM2（80 um，R=0.006）相同

RHO = 992.2
MU = 6.53e-4
NU = MU / RHO


def f_re_rect(alpha):
    """Shah & London，alpha = 短边/长边。"""
    return 24 * (1 - 1.3553 * alpha + 1.9467 * alpha ** 2
                 - 1.7012 * alpha ** 3 + 0.9564 * alpha ** 4
                 - 0.2537 * alpha ** 5)


FRE = f_re_rect(min(CH_W, CH_H) / max(CH_W, CH_H))
Q_SIDE_M3S = 0.20 / 60000.0
V_A = Q_SIDE_M3S / (N_CH * CH_W * CH_H * 1e-6)
V_B = V_A * 2.4 / 2.0


def _sum_geo(h1, r, m):
    if m <= 0:
        return 0.0
    if abs(r - 1.0) < 1e-9:
        return h1 * m
    return h1 * (r ** m - 1.0) / (r - 1.0)


def sizes_one_side(length, h1, gr, hmax):
    """从起点几何增长铺满 length。首格 = h1（段比 h1 短则更小），相邻比 <= gr，格不大于 hmax。"""
    if length <= 1e-12:
        return []
    if length <= h1 * (1.0 + 1e-9):
        return [length]
    h1 = min(h1, hmax)
    # 纯几何、尚未顶到 hmax 时，用恰好铺满的公比
    m = 1
    while _sum_geo(h1, gr, m) < length - 1e-8:
        nxt = h1 * gr ** m
        if nxt > hmax * (1.0 + 1e-8):
            break
        m += 1
        if m > 500:
            break
    if h1 * (gr ** (m - 1)) <= hmax * (1.0 + 1e-6) and _sum_geo(h1, gr, m) >= length - 1e-8:
        lo, hi = 1.0, gr
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if _sum_geo(h1, mid, m) < length:
                lo = mid
            else:
                hi = mid
        r = hi
        sizes = [h1 * (r ** i) for i in range(m)]
        sizes[-1] += length - sum(sizes)
        return sizes
    sizes = []
    h = h1
    left = length
    while left > h * (1.0 + 1e-9) and h * gr <= hmax * (1.0 + 1e-8):
        sizes.append(h)
        left -= h
        h *= gr
    step = min(hmax, h)
    prev = sizes[-1] if sizes else step
    if step > prev * gr:
        step = prev * gr
    n = max(1, int(round(left / step)))
    step = left / n
    while step > hmax * (1.0 + 1e-6) or (sizes and step > sizes[-1] * gr * (1.0 + 1e-6)):
        n += 1
        step = left / n
    sizes.extend([step] * n)
    drift = length - sum(sizes)
    sizes[-1] += drift
    return sizes


def sizes_both(length, h1, gr, hmax, h1_right=None):
    right = h1 if h1_right is None else h1_right
    left = sizes_one_side(length / 2.0, h1, gr, hmax)
    rev = sizes_one_side(length / 2.0, right, gr, hmax)
    return left + list(reversed(rev))


def coords_of(a, b, sizes):
    xs = [a]
    for h in sizes:
        xs.append(xs[-1] + h)
    xs[-1] = b
    return xs


def uniform(a, b, h):
    span = b - a
    n = max(1, int(span / h + 0.999999))
    step = span / n
    return [a + i * step for i in range(n + 1)]


def max_ratio(xs):
    sizes = [b - a for a, b in zip(xs, xs[1:])]
    ratio = 1.0
    for a, b in zip(sizes, sizes[1:]):
        if a > 1e-12 and b > 1e-12:
            ratio = max(ratio, b / a, a / b)
    return ratio, (sizes[0] if sizes else 0.0), (min(sizes) if sizes else 0.0), (max(sizes) if sizes else 0.0)


def wall_layers(xs, h1, gr):
    """从起点数连续、增长不超过 gr、且首格 <= h1*1.01 的层数。"""
    sizes = [b - a for a, b in zip(xs, xs[1:])]
    if not sizes or sizes[0] > h1 * 1.05:
        return 0
    n = 1
    for a, b in zip(sizes, sizes[1:]):
        if b <= a * gr * 1.02 + 1e-9:
            n += 1
        else:
            break
    return n


def cat(parts):
    out = list(parts[0])
    for p in parts[1:]:
        out.extend(p[1:])
    return out


def build_y():
    """局部 y：0 在列的下游端（靠出液），50 在上游端（靠进液）。"""
    down = coords_of(0.0, LE, sizes_one_side(LE, HMAX_Y, GR_Y, HMAX_EXT))
    ext_out = [-v for v in reversed(down)]
    ext_in = [COL_L + v for v in coords_of(0.0, LE, sizes_one_side(LE, H1_Y, GR_Y, HMAX_EXT))]
    stack_up = [COL_L - v for v in reversed(
        coords_of(0.0, 11.0, sizes_one_side(11.0, H1_Y, GR_Y, HMAX_Y))
    )]
    parts = [
        ext_out,
        uniform(0.0, 11.0, HMAX_Y),
        uniform(11.0, 13.0, HMAX_Y),
        uniform(13.0, 24.0, HMAX_Y),
        uniform(24.0, 26.0, HMAX_Y),
        uniform(26.0, 37.0, HMAX_Y),
        uniform(37.0, 39.0, HMAX_Y),
        stack_up,
        ext_in,
    ]
    y = cat(parts)
    for a, b in zip(y, y[1:]):
        if b <= a + 1e-9:
            raise RuntimeError(f"y 不单调: {a} -> {b}")
    return y


def build_z():
    z_tim0 = -(T_BASE + T_TIM)
    z_cu0 = -T_BASE
    z0 = 0.0
    z_fin = CH_H
    z_lid1 = z_fin + T_LID
    tim = uniform(z_tim0, z_cu0, T_TIM / N_TIM)
    base = coords_of(z_cu0, z0, sizes_both(T_BASE, H1_S, GR_S, HMAX_S))
    groove = coords_of(z0, z_fin, sizes_both(CH_H, H1_F, GR_F, HMAX_F))
    lid = coords_of(z_fin, z_lid1, sizes_one_side(T_LID, H1_S, GR_S, HMAX_S))
    z = cat([tim, base, groove, lid])
    bands = {
        "tim": (z_tim0, z_cu0),
        "base": (z_cu0, z0),
        "groove": (z0, z_fin),
        "lid": (z_fin, z_lid1),
    }
    return z, bands


def x_nodes_single():
    # 肋的横向节点也按流体边界层排。间隙是通的，肋顶上方仍是流体，
    # 节点必须和槽壁第一层对齐，否则间隙内相邻格子比会大于 1.2。
    half = FIN_W / 2.0
    fin_l = coords_of(0.0, half, sizes_both(half, H1_F, GR_F, HMAX_F))
    ch = coords_of(half, half + CH_W, sizes_both(CH_W, H1_F, GR_F, HMAX_F))
    fin_r = coords_of(half + CH_W, PITCH, sizes_both(half, H1_F, GR_F, HMAX_F))
    x = cat([fin_l, ch, fin_r])
    fluid_x = [(half, half + CH_W)]
    return x, fluid_x, PITCH


def x_nodes_array():
    # 0.65 岸 + (0.60 槽 + 0.70 肋) x 7 + 0.60 槽 + 0.65 岸
    pieces = []
    fluid_x = []
    x0 = 0.0
    land_s = sizes_both(LAND, H1_F, GR_F, HMAX_F)
    pieces.append(coords_of(x0, x0 + LAND, land_s))
    x0 += LAND
    fin_s = sizes_both(FIN_W, H1_F, GR_F, HMAX_F)
    ch_s = sizes_both(CH_W, H1_F, GR_F, HMAX_F)
    for i in range(N_CH):
        pieces.append(coords_of(x0, x0 + CH_W, ch_s))
        fluid_x.append((x0, x0 + CH_W))
        x0 += CH_W
        if i < N_CH - 1:
            pieces.append(coords_of(x0, x0 + FIN_W, fin_s))
            x0 += FIN_W
    pieces.append(coords_of(x0, x0 + LAND, list(reversed(land_s))))
    x0 += LAND
    if abs(x0 - 11.0) > 1e-6:
        raise RuntimeError(f"阵列宽度 {x0} != 11")
    return cat(pieces), fluid_x, 11.0


def in_fluid_x(xc, fluid_x):
    return any(a - 1e-9 <= xc <= b + 1e-9 for a, b in fluid_x)


def band_of(zc, bands):
    hit = None
    for name, (a, b) in bands.items():
        if a - 1e-8 <= zc <= b + 1e-8:
            hit = name
    if hit is None:
        raise RuntimeError(f"z={zc} 不在任何带内")
    return hit


def heated_flags(y):
    flags = []
    for a, b in zip(y, y[1:]):
        yc = 0.5 * (a + b)
        flags.append(any(lo - 1e-9 <= yc <= hi + 1e-9 for lo, hi in STACKS))
    return flags


def classify(x, y, z, bands, fluid_x):
    """返回 (nx,ny,nz) 上的区名，空字符串表示不建（TIM 只铺在四颗堆叠下）。"""
    nx, ny, nz = len(x) - 1, len(y) - 1, len(z) - 1
    heat = heated_flags(y)
    kinds = []
    for k in range(nz):
        zc = 0.5 * (z[k] + z[k + 1])
        band = band_of(zc, bands)
        row = []
        for i in range(nx):
            xc = 0.5 * (x[i] + x[i + 1])
            if band == "tim":
                row.append("tim")
            elif band == "groove":
                row.append("fluid" if in_fluid_x(xc, fluid_x) else "cu")
            elif band == "gap":
                row.append("fluid")
            else:
                row.append("cu")
        kinds.append(row)  # [k][i]
    return kinds, heat


def count_cells(kinds, heat):
    nz = len(kinds)
    nx = len(kinds[0])
    ny = len(heat)
    n_f = n_c = n_t = 0
    for j in range(ny):
        for k in range(nz):
            for i in range(nx):
                name = kinds[k][i]
                if name == "tim" and not heat[j]:
                    continue
                if name == "fluid":
                    n_f += 1
                elif name == "cu":
                    n_c += 1
                else:
                    n_t += 1
    return n_f, n_c, n_t


def yplus(h1_mm, v):
    h1 = h1_mm * 1e-3
    re = RHO * v * (DH_GROOVE * 1e-3) / MU
    f = FRE / re
    tau = f * RHO * v * v / 2.0
    utau = (tau / RHO) ** 0.5
    return h1 * utau / NU, re, tau


def audit(tag, x, y, z, bands, fluid_x):
    kinds, heat = classify(x, y, z, bands, fluid_x)
    n_f, n_c, n_t = count_cells(kinds, heat)
    lines = [f"case {tag}", f"nx {len(x)-1}", f"ny {len(y)-1}", f"nz {len(z)-1}",
             f"cells_fluid {n_f}", f"cells_cu {n_c}", f"cells_tim {n_t}",
             f"cells_total {n_f+n_c+n_t}"]
    # 流体首层：槽宽两侧、槽底、间隙底、间隙顶
    half = FIN_W / 2.0
    # 这些检查用整条坐标上贴壁的第一格，见各分段
    rx, h1x, _, _ = max_ratio(x)
    ry, h1y, _, _ = max_ratio(y)
    rz, _, _, _ = max_ratio(z)
    lines.append(f"ratio_x {rx:.4f}")
    lines.append(f"ratio_y {ry:.4f}")
    lines.append(f"ratio_z {rz:.4f}")
    for label, v in (("DP-A", V_A), ("DP-B", V_B)):
        yp, re, tau = yplus(H1_F, v)
        lines.append(f"yplus_{label} {yp:.3f} Re {re:.1f} tau {tau:.3f}")
    lines.append(f"first_fluid_mm {H1_F}")
    lines.append(f"first_solid_mm {H1_S}")
    lines.append(f"Le_mm {LE:.4f}")
    lines.append(f"heated_cells_y {sum(heat)}")
    return "\n".join(lines) + "\n", kinds, heat, n_f + n_c + n_t


def cell_ids(kinds, heat):
    nz = len(kinds)
    nx = len(kinds[0])
    ny = len(heat)
    ids = [[[0] * nx for _ in range(ny)] for _ in range(nz)]
    n_f = n_c = n_t = 0
    for j in range(ny):
        hot = heat[j]
        for k in range(nz):
            row = kinds[k]
            for i in range(nx):
                name = row[i]
                if name == "tim" and not hot:
                    continue
                if name == "fluid":
                    n_f += 1
                elif name == "cu":
                    n_c += 1
                elif name == "tim":
                    n_t += 1
    c_f = c_c = c_t = 0
    for j in range(ny):
        hot = heat[j]
        for k in range(nz):
            row = kinds[k]
            idrow = ids[k][j]
            for i in range(nx):
                name = row[i]
                if name == "tim" and not hot:
                    continue
                if name == "fluid":
                    c_f += 1
                    idrow[i] = c_f
                elif name == "cu":
                    c_c += 1
                    idrow[i] = n_f + c_c
                elif name == "tim":
                    c_t += 1
                    idrow[i] = n_f + n_c + c_t
    return ids, n_f, n_c, n_t


def write_msh(path, x, y, z, kinds, heat, ids, n_f, n_c, n_t, title, side_zone, bnd=None):
    """面数据按区写入临时文件，避免把整套面表留在内存里。

    kinds[k] 可以是长度 nx 的材料名，也可以是 kinds[k][j][i]。
    bnd(axis, i, j, k, material) 只用于交错流的进口、出口；缺省时仍是
    y 最小端出口、y 最大端进口。
    """
    nx, ny, nz = len(x) - 1, len(y) - 1, len(z) - 1
    n_cells = n_f + n_c + n_t
    names = (
        "interior", "wall_cu_fluid", "wall_tim_cu", "inlet", "outlet",
        "inlet_lo", "inlet_hi", "inlet_mid", "outlet_lo", "outlet_hi",
        "wall_heat", "wall_adiabat", side_zone,
    )
    bc = {
        "interior": 2, "wall_cu_fluid": 3, "wall_tim_cu": 3, "wall_heat": 3,
        "wall_adiabat": 3, "wall_side": 3, "sym": 7, "outlet": 5, "inlet": 10,
        "outlet_lo": 5, "outlet_hi": 5, "inlet_lo": 10, "inlet_hi": 10, "inlet_mid": 10,
    }
    kind_map = {2: "interior", 3: "wall", 5: "pressure-outlet", 7: "symmetry", 10: "mass-flow-inlet"}

    def cid(i, j, k):
        if i < 0 or j < 0 or k < 0 or i >= nx:
            return 0
        return ids[k][j][i]

    def nid(i, j, k):
        return 1 + i + (nx + 1) * (j + (ny + 1) * k)

    def zname(i, j, k):
        if ids[k][j][i] == 0:
            return ""
        level = kinds[k]
        if level and isinstance(level[0], (list, tuple)):
            return level[j][i]
        return level[i]

    centers = [None] * (n_cells + 1)
    for k in range(nz):
        zc = 0.5 * (z[k] + z[k + 1])
        for j in range(ny):
            yc = 0.5 * (y[j] + y[j + 1])
            idrow = ids[k][j]
            for i in range(nx):
                c = idrow[i]
                if c:
                    centers[c] = (0.5 * (x[i] + x[i + 1]), yc, zc)
    z_bot = z[0]
    z_top = z[-1]
    tmp = path.with_suffix(".faces")
    handles = {name: tmp.with_name(tmp.name + "." + name).open("w", encoding="ascii", newline="\n")
               for name in names}
    counts = {name: 0 for name in names}
    buf = {name: [] for name in names}

    def node_xyz(n):
        n -= 1
        sx, sy = nx + 1, ny + 1
        i = n % sx
        t = n // sx
        j = t % sy
        k = t // sy
        return x[i], y[j], z[k]

    def emit(name, n0, n1, n2, n3, c0, c1):
        # 右手定则法向指向 c0，与已读通的 12 槽网格相同。编号用十六进制。
        if c0:
            p0, p1, p2, p3 = (node_xyz(n) for n in (n0, n1, n2, n3))
            ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
            vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
            nx_ = uy * vz - uz * vy
            ny_ = uz * vx - ux * vz
            nz_ = ux * vy - uy * vx
            if nx_ * nx_ + ny_ * ny_ + nz_ * nz_ < 1e-30:
                vx, vy, vz = p3[0] - p0[0], p3[1] - p0[1], p3[2] - p0[2]
                nx_ = uy * vz - uz * vy
                ny_ = uz * vx - ux * vz
                nz_ = ux * vy - uy * vx
            fc = ((p0[0] + p1[0] + p2[0] + p3[0]) * 0.25,
                  (p0[1] + p1[1] + p2[1] + p3[1]) * 0.25,
                  (p0[2] + p1[2] + p2[2] + p3[2]) * 0.25)
            gx, gy, gz = centers[c0]
            if nx_ * (gx - fc[0]) + ny_ * (gy - fc[1]) + nz_ * (gz - fc[2]) < 0.0:
                n0, n1, n2, n3 = n0, n3, n2, n1
        buf[name].append(f"{n0:x} {n1:x} {n2:x} {n3:x} {c0:x} {c1:x}\n")
        counts[name] += 1
        if len(buf[name]) >= 20000:
            handles[name].write("".join(buf[name]))
            buf[name].clear()

    def pair(n0, n1, n2, n3, c0, c1, za, zb):
        if za == zb:
            emit("interior", n0, n1, n2, n3, c0, c1)
        elif za == "fluid" and zb == "cu" or za == "cu" and zb == "fluid":
            emit("wall_cu_fluid", n0, n1, n2, n3, c0, c1)
        elif za == "cu" and zb == "tim" or za == "tim" and zb == "cu":
            emit("wall_tim_cu", n0, n1, n2, n3, c0, c1)
        else:
            emit("wall_adiabat", n0, n1, n2, n3, c0, c1)

    try:
        for i in range(nx + 1):
            for j in range(ny):
                for k in range(nz):
                    left = cid(i - 1, j, k) if i else 0
                    right = cid(i, j, k) if i < nx else 0
                    if not left and not right:
                        continue
                    n0, n1 = nid(i, j, k), nid(i, j + 1, k)
                    n2, n3 = nid(i, j + 1, k + 1), nid(i, j, k + 1)
                    if left and right:
                        pair(n0, n1, n2, n3, left, right, zname(i - 1, j, k), zname(i, j, k))
                    else:
                        owner_i = i - 1 if left else i
                        if owner_i >= nx:
                            owner_i = nx - 1
                        if owner_i < 0:
                            owner_i = 0
                        zone = None
                        if bnd is not None and zname(owner_i, j, k) == "fluid":
                            zone = bnd("x", i, j, k, "fluid")
                        if zone in ("inlet", "inlet_lo", "inlet_hi", "inlet_mid", "outlet", "outlet_lo", "outlet_hi"):
                            emit(zone, n0, n1, n2, n3, left or right, 0)
                        else:
                            emit(side_zone, n0, n1, n2, n3, left or right, 0)
        for j in range(ny + 1):
            for i in range(nx):
                for k in range(nz):
                    back = cid(i, j - 1, k) if j else 0
                    fwd = cid(i, j, k) if j < ny else 0
                    if not back and not fwd:
                        continue
                    n0, n1 = nid(i, j, k), nid(i + 1, j, k)
                    n2, n3 = nid(i + 1, j, k + 1), nid(i, j, k + 1)
                    if back and fwd:
                        za = zname(i, j - 1, k)
                        zb = zname(i, j, k)
                        zone = None
                        if bnd is not None and za != zb and (za == "fluid" or zb == "fluid"):
                            zone = bnd("y", i, j, k, "fluid")
                        if zone in ("inlet_lo", "inlet_hi", "inlet_mid"):
                            # 进口在槽道中部，一侧是流体、一侧是封死的铜。
                            # 拆成进口面和铜侧壁，不能写成两侧耦合壁。
                            fluid_c = back if za == "fluid" else fwd
                            solid_c = fwd if za == "fluid" else back
                            emit(zone, n0, n1, n2, n3, fluid_c, 0)
                            emit("wall_adiabat", n0, n1, n2, n3, solid_c, 0)
                        else:
                            pair(n0, n1, n2, n3, back, fwd, za, zb)
                    else:
                        owner_j = j - 1 if back else j
                        if owner_j >= ny:
                            owner_j = ny - 1
                        if owner_j < 0:
                            owner_j = 0
                        name = zname(i, owner_j, k)
                        if bnd is not None and name == "fluid":
                            zone = bnd("y", i, j, k, name)
                        else:
                            zone = ("outlet" if j == 0 else "inlet") if name == "fluid" else "wall_adiabat"
                        emit(zone, n0, n1, n2, n3, back or fwd, 0)
        for k in range(nz + 1):
            at_bot = abs(z[k] - z_bot) < 1e-9
            at_top = abs(z[k] - z_top) < 1e-9
            for j in range(ny):
                hot = heat[j]
                for i in range(nx):
                    below = cid(i, j, k - 1) if k else 0
                    above = cid(i, j, k) if k < nz else 0
                    if not below and not above:
                        continue
                    n0, n1 = nid(i, j, k), nid(i + 1, j, k)
                    n2, n3 = nid(i + 1, j + 1, k), nid(i, j + 1, k)
                    if below and above:
                        pair(n0, n1, n2, n3, below, above, zname(i, j, k - 1), zname(i, j, k))
                    elif above and at_bot:
                        emit("wall_heat" if hot else "wall_adiabat", n0, n1, n2, n3, above, 0)
                    else:
                        owner_k = k - 1 if below else k
                        if owner_k >= nz:
                            owner_k = nz - 1
                        if owner_k < 0:
                            owner_k = 0
                        name = zname(i, j, owner_k)
                        if bnd is not None and name == "fluid":
                            zone = bnd("z", i, j, k, name)
                        else:
                            zone = "wall_adiabat"
                        emit(zone, n0, n1, n2, n3, below or above, 0)
        for name in names:
            if buf[name]:
                handles[name].write("".join(buf[name]))
                buf[name].clear()
            handles[name].close()
    except Exception:
        for h in handles.values():
            h.close()
        raise

    n_nodes = (nx + 1) * (ny + 1) * (nz + 1)
    n_faces = sum(counts.values())
    path.parent.mkdir(parents=True, exist_ok=True)
    zone_ids = {}
    with path.open("w", encoding="ascii", newline="\n") as f:
        f.write(f'(0 "{title}")\n(2 3)\n')
        f.write(f"(10 (0 1 {n_nodes:x} 0 3))\n")
        f.write(f"(12 (0 1 {n_cells:x} 0 0))\n")
        f.write(f"(13 (0 1 {n_faces:x} 0 0))\n")
        f.write(f"(10 (1 1 {n_nodes:x} 1 3)\n(\n")
        for k in range(nz + 1):
            zk = z[k] * 1e-3
            for j in range(ny + 1):
                yj = y[j] * 1e-3
                f.write("".join(f"{x[i]*1e-3:.8e} {yj:.8e} {zk:.8e}\n" for i in range(nx + 1)))
        f.write(")\n)\n")
        if n_f:
            f.write(f"(12 (2 1 {n_f:x} 1 4))\n")
        if n_c:
            f.write(f"(12 (3 {n_f + 1:x} {n_f + n_c:x} 1 4))\n")
        if n_t:
            f.write(f"(12 (4 {n_f + n_c + 1:x} {n_cells:x} 1 4))\n")
        f0 = 1
        zid = 5
        for name in names:
            n = counts[name]
            if not n:
                continue
            f1 = f0 + n - 1
            zone_ids[name] = zid
            f.write(f"(13 ({zid:x} {f0:x} {f1:x} {bc[name]:x} 4)\n(\n")
            src = tmp.with_name(tmp.name + "." + name)
            with src.open("r", encoding="ascii", newline="\n") as srcf:
                while True:
                    block = srcf.read(1 << 20)
                    if not block:
                        break
                    f.write(block)
            f.write(")\n)\n")
            src.unlink()
            f0 = f1 + 1
            zid += 1
        if n_f:
            f.write("(39 (2 fluid fluid)())\n")
        if n_c:
            f.write("(39 (3 solid solid_cu)())\n")
        if n_t:
            f.write("(39 (4 solid solid_tim2)())\n")
        for name, zid in zone_ids.items():
            # 39 节的区域号按十进制写。面段里的同一编号仍是十六进制。
            f.write(f"(39 ({zid} {kind_map[bc[name]]} {name})())\n")
    return n_nodes, n_faces, {name: counts[name] for name in zone_ids}


def write_info(path, text, extra):
    path.write_text(text + extra, encoding="utf-8")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "count"
    y = build_y()
    z, bands = build_z()
    jobs = []
    if mode in ("count", "single", "both"):
        jobs.append(("single",) + x_nodes_single())
    if mode in ("count", "array", "both"):
        jobs.append(("array",) + x_nodes_array())
    for tag, x, fluid_x, width in jobs:
        text, kinds, heat, ntot = audit(tag, x, y, z, bands, fluid_x)
        print(text)
        if mode == "count":
            write_info(HERE / f"hbm_{tag}_count.txt", text, f"width_mm {width}\n")
            continue
        print(f"numbering {tag} ...", flush=True)
        ids, n_f, n_c, n_t = cell_ids(kinds, heat)
        side = "sym" if tag == "single" else "wall_side"
        msh = HERE / ("hbm_w08h20.msh" if tag == "array" else f"hbm_{tag}.msh")
        print(f"writing {msh} ...", flush=True)
        n_nodes, n_faces, zones = write_msh(
            msh, x, y, z, kinds, heat, ids, n_f, n_c, n_t,
            f"HBM CHT hex {tag}; first fluid {H1_F} mm; GR {GR_F}",
            side,
        )
        zone_txt = "".join(f"zone {k} {v}\n" for k, v in zones.items())
        mdot_ch = RHO * (0.40 / (2.0 * N_CH)) / 60000.0
        mdot = mdot_ch if tag == "single" else mdot_ch * N_CH
        extra = (
            f"nodes {n_nodes}\nfaces {n_faces}\nmsh {msh}\n"
            f"mdot_kg_s {mdot:.8e}\nq_Wm2 {Q_FLUX:.1f}\n"
            f"k_tim {K_EFF_TIM}\nwidth_mm {width}\n" + zone_txt
        )
        write_info(HERE / f"hbm_{tag}_info.txt", text, extra)
        print(f"WROTE {msh} cells={n_f+n_c+n_t} nodes={n_nodes} faces={n_faces}")


if __name__ == "__main__":
    main()

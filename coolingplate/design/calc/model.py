# -*- coding: utf-8 -*-
"""
CP-B300-JM-01 冷板一维模型（唯一数值来源）
本模块只做计算，不打印。被 cp_b300_1d.py（计算书）与 build_report.py（报告生成）共用。
"""
import math

# ============================================================
# 工质物性
# ============================================================
class Fluid:
    def __init__(self, name, rho, cp, mu, k):
        self.name = name
        self.rho = rho      # kg/m3
        self.cp = cp        # J/kgK
        self.mu = mu        # Pa.s
        self.k = k          # W/mK
        self.Pr = mu * cp / k

WATER40 = Fluid("DI 水 40 °C", 992.2, 4179.0, 6.53e-4, 0.631)
PG25_40 = Fluid("PG25 40 °C", 1022.0, 3900.0, 1.15e-3, 0.452)

K_CU = 390.0        # C110 紫铜 W/mK
E_CU = 110e9        # 铜弹性模量 Pa
SY_CU = 70e6        # 退火铜屈服强度 Pa（保守）

# ============================================================
# 设计点
# ============================================================
DESIGN_POINTS = {
    "DP-A": dict(P=1100.0, Q_lpm=2.0, Tin=40.0, target_R=0.028,
                 role="保证点（Lenovo SXM DLC TGP）"),
    "DP-B": dict(P=1400.0, Q_lpm=2.4, Tin=40.0, target_R=0.025,
                 role="包络（NVIDIA 最大 TGP）"),
}
SPLIT_GPU = 0.80

# 功率拆分（封装假设）。1100 W 整板仍是 429+429+198+44。
FRAC = dict(die=0.39, hbm_total=0.18, other=0.04)
# 边界热流冗余：只乘在施加 q'' 上，不乘流量，不改 1100 W 板规格。
Q_FLUX_MARGIN = 1.05

# ============================================================
# 几何（冻结候选 · CP-B300-JM-01）
# ============================================================
GEO = dict(
    plate_L=95.0, plate_W=75.0, plate_T=8.5,
    die_w=27.0, die_h=28.0, n_die=2,
    die_a_x=19.0, die_a_y=23.5, hbi=3.0,
    hbm_w=11.0, hbm_h=11.0, n_hbm=8,
    hbm_x_l=5.0, hbm_x_r=79.0, hbm_y0=12.5, hbm_dy=13.0,
    D_jet=0.50, H_jet=2.0,
    # X = 沿铜肋槽。Sx=3.0，die_w=27 mm，9 格刚好 27.0 mm。
    # Y = 出流导流槽长向。Sy=2.4，12 格 = 28.8 mm，比 die_h=28 mm 宽 0.8 mm。
    # 板在该向的外包络 = 28+1.2 = 29.2 mm，胞列放进外包络后还剩 0.4 mm。
    # Covered length = n*pitch. Center span = (n-1)*pitch.
    S_jet_x=3.0, S_jet_y=2.4,
    n_jet_x=9, n_jet_y=12,
    envelope_allowance_y=1.2,
    ch_w=0.40, ch_h=1.50, ch_p=0.80, L_flow=3.0, L_flow_max=8.0,
    hbm_ch_w=0.60, hbm_ch_h=1.50, n_hbm_ch=16,
    t_lid=2.5, t_base=3.5, base_cu=2.0, t_braze=0.5,
    rib=2.0, rib_x_l=16.5, rib_x_r=76.5, rib_y0=12.5, rib_len=50.0,
    man_x=8.0, man_w=79.0, man_h=7.0, man_in_y=66.0, man_out_y=2.0,
    V_cap_hbm=0.80,
    dP_target=18.0, dP_limit=20.0,
)

K_ORIFICE = 1.8          # 孔口局部阻力系数

GEO["n_jet_per_die"] = GEO["n_jet_x"] * GEO["n_jet_y"]
GEO["jet_span_x"] = (GEO["n_jet_x"] - 1) * GEO["S_jet_x"]
GEO["jet_span_y"] = (GEO["n_jet_y"] - 1) * GEO["S_jet_y"]
GEO["covered_x"] = GEO["n_jet_x"] * GEO["S_jet_x"]
GEO["covered_y"] = GEO["n_jet_y"] * GEO["S_jet_y"]
GEO["remainder_x"] = GEO["die_w"] - GEO["covered_x"]
GEO["overhang_y"] = GEO["covered_y"] - GEO["die_h"]
GEO["envelope_y"] = GEO["die_h"] + GEO["envelope_allowance_y"]
GEO["envelope_margin_y"] = GEO["envelope_y"] - GEO["covered_y"]
GEO["jet_a_x"] = (GEO["die_a_x"] + GEO["S_jet_x"] / 2.0
                  + GEO["remainder_x"] / 2.0)
GEO["jet_a_y"] = (GEO["die_a_y"] + GEO["S_jet_y"] / 2.0
                  + (GEO["die_h"] - GEO["covered_y"]) / 2.0)
GEO["jet_span"] = max(GEO["jet_span_x"], GEO["jet_span_y"])

N_JET = GEO["n_jet_per_die"] * GEO["n_die"]

# ---- 派生面积 ----
A_JET_1 = math.pi / 4 * (GEO["D_jet"] * 1e-3) ** 2
A_JET = N_JET * A_JET_1
_CELL_PITCH = GEO["S_jet_x"] * GEO["S_jet_y"]
F_AREA = (math.pi / 4 * GEO["D_jet"] ** 2) / _CELL_PITCH
HD = GEO["H_jet"] / GEO["D_jet"]
SD_X = GEO["S_jet_x"] / GEO["D_jet"]
SD_Y = GEO["S_jet_y"] / GEO["D_jet"]

A_CELL = _CELL_PITCH * 1e-6
A_COVERED_DIE = GEO["n_jet_per_die"] * A_CELL
A_COVERED = N_JET * A_CELL

A_DIE = GEO["die_w"] * GEO["die_h"] * 1e-6          # m2 单 die
A_2DIE = A_DIE * GEO["n_die"]
A_HBM = GEO["hbm_w"] * GEO["hbm_h"] * 1e-6
A_PLATE = GEO["plate_L"] * GEO["plate_W"] * 1e-6

A_CH = GEO["ch_w"] * GEO["ch_h"] * 1e-6
DH_CH = 2 * GEO["ch_w"] * GEO["ch_h"] / (GEO["ch_w"] + GEO["ch_h"]) * 1e-3
N_CH_DIE = int(round(GEO["die_h"] / GEO["ch_p"]))    # 35
A_HBM_CH = GEO["hbm_ch_w"] * GEO["hbm_ch_h"] * 1e-6
DH_HBM = 2 * GEO["hbm_ch_w"] * GEO["hbm_ch_h"] / \
    (GEO["hbm_ch_w"] + GEO["hbm_ch_h"]) * 1e-3

# 射流胞湿润面积（跨槽节距 Sy 内的短槽；Y 向胞列允许比 die 宽 0.8 mm）
CH_PER_CELL = GEO["S_jet_y"] / GEO["ch_p"]
_Lx_cell = GEO["S_jet_x"] * 1e-3
A_FIN_CELL = CH_PER_CELL * 2 * (GEO["ch_h"] * 1e-3) * _Lx_cell
A_BOT_CELL = CH_PER_CELL * (GEO["ch_w"] * 1e-3) * _Lx_cell
A_FIN_DIE = A_FIN_CELL * GEO["n_jet_per_die"]
A_BOT_DIE = A_BOT_CELL * GEO["n_jet_per_die"]
A_WET_DIE = A_FIN_DIE + A_BOT_DIE
AREA_GAIN = A_WET_DIE / A_COVERED_DIE

R_WALL = (GEO["base_cu"] * 1e-3) / (K_CU * A_2DIE)

# 热阻链假设区间
R_PKG = (0.008, 0.012)
R_TIM2 = (0.004, 0.008)


# ============================================================
# 关联式
# ============================================================
def f_re_rect(alpha):
    """Shah & London 矩形通道层流 f*Re（alpha = 短/长）"""
    return 24 * (1 - 1.3553 * alpha + 1.9467 * alpha ** 2
                 - 1.7012 * alpha ** 3 + 0.9564 * alpha ** 4
                 - 0.2537 * alpha ** 5)

FRE_CH = f_re_rect(min(GEO["ch_w"], GEO["ch_h"]) / max(GEO["ch_w"], GEO["ch_h"]))
FRE_HBM = f_re_rect(min(GEO["hbm_ch_w"], GEO["hbm_ch_h"]) /
                    max(GEO["hbm_ch_w"], GEO["hbm_ch_h"]))


def nu_stagnation(Re, Pr):
    """驻点层流量级式 Nu0 = 0.5 Re^0.5 Pr^0.4"""
    return 0.5 * Re ** 0.5 * Pr ** 0.4


def nu_martin(Re, Pr, f=F_AREA, hd=HD):
    """Martin(1977) 圆孔阵列面平均 Nu。
    有效域 2000<=Re<=1e5, 0.004<=f<=0.04, 2<=H/D<=12"""
    sf = math.sqrt(f)
    K = ((1 + (hd / (0.6 / sf)) ** 6) ** -0.05) * sf * \
        (2 - 2.2 * sf) / (1 + 0.2 * (hd - 6) * sf)
    return K * Re ** (2.0 / 3.0) * Pr ** 0.42, K


MARTIN_RE_MIN = 2000


def nu_duct_developing(Re, Pr, Dh, L):
    """短槽层流热入口（Hausen 型），恒热流全发展下界 Nu=4.0"""
    Gz = Dh / L * Re * Pr
    return max(4.0, 1.86 * Gz ** (1.0 / 3.0))


def fin_efficiency(h, t, H):
    m = math.sqrt(2 * h / (K_CU * t))
    mL = m * H
    return math.tanh(mL) / mL, m


# ============================================================
# 工况求解
# ============================================================
def mass_flow(fl, Q_lpm):
    return fl.rho * Q_lpm / 60000.0


def delta_tf(fl, Q_lpm, P):
    return P / (mass_flow(fl, Q_lpm) * fl.cp)


def jet_state(fl, Q_lpm_gpu, D=None, N=None):
    D = GEO["D_jet"] if D is None else D
    N = N_JET if N is None else N
    A = N * math.pi / 4 * (D * 1e-3) ** 2
    V = (Q_lpm_gpu / 60000.0) / A
    Re = fl.rho * V * (D * 1e-3) / fl.mu
    dP = K_ORIFICE * fl.rho * V ** 2 / 2
    return dict(A=A, V=V, Re=Re, dP=dP, D=D, N=N)


def channel_state(fl, Q_lpm_gpu, model="cell"):
    """model='cell': 单孔就近排走（真实拓扑，槽=肋）
       model='bank': 全流量单向穿全部槽（保守上界，用于对比）"""
    Q = Q_lpm_gpu / 60000.0
    if model == "bank":
        A_tot = N_CH_DIE * GEO["n_die"] * A_CH
        L = GEO["L_flow_max"] * 1e-3
    else:
        A_tot = N_JET * CH_PER_CELL * A_CH * 2
        L = GEO["L_flow"] * 1e-3
    V = Q / A_tot
    Re = fl.rho * V * DH_CH / fl.mu
    f = FRE_CH / Re
    dP = f * (L / DH_CH) * fl.rho * V ** 2 / 2
    return dict(V=V, Re=Re, f=f, dP=dP, L=L)


def hbm_state(fl, Q_lpm_total):
    Q = Q_lpm_total * (1 - SPLIT_GPU) / 60000.0
    V = Q / (GEO["n_hbm_ch"] * A_HBM_CH)
    Re = fl.rho * V * DH_HBM / fl.mu
    f = FRE_HBM / Re
    L = GEO["rib_len"] * 1e-3
    dP = f * (L / DH_HBM) * fl.rho * V ** 2 / 2
    return dict(V=V, Re=Re, f=f, dP=dP, Q_lpm=Q_lpm_total * (1 - SPLIT_GPU),
                ok=V <= GEO["V_cap_hbm"])


def h_model_optimistic(fl, Q_lpm_gpu):
    """模型 B：Martin 阵列面平均 h，面积为两 die 全部射流胞。Re<2000 不采用。"""
    js = jet_state(fl, Q_lpm_gpu)
    applied = js["Re"] >= MARTIN_RE_MIN
    if not applied:
        return dict(h=None, Nu=None, K=None, hA=None, R=None, Re=js["Re"],
                    extrapolated=True, applied=False)
    Nu, K = nu_martin(js["Re"], fl.Pr)
    h = Nu * fl.k / (GEO["D_jet"] * 1e-3)
    hA = h * A_COVERED
    return dict(h=h, Nu=Nu, K=K, hA=hA, R=1 / hA, Re=js["Re"],
                extrapolated=False, applied=True)


def h_model_conservative(fl, Q_lpm_gpu):
    """模型 C：短槽当肋 + 导管对流，叠加驻点核强化"""
    cs = channel_state(fl, Q_lpm_gpu, "cell")
    Nu = nu_duct_developing(cs["Re"], fl.Pr, DH_CH, cs["L"])
    h_ch = Nu * fl.k / DH_CH
    eta, m = fin_efficiency(h_ch, GEO["ch_w"] * 1e-3, GEO["ch_h"] * 1e-3)
    js = jet_state(fl, Q_lpm_gpu)
    h_stag = nu_stagnation(js["Re"], fl.Pr) * fl.k / (GEO["D_jet"] * 1e-3)
    A_stag_die = GEO["n_jet_per_die"] * math.pi / 4 * \
        (2 * GEO["D_jet"] * 1e-3) ** 2
    hA = (h_ch * (A_FIN_DIE * eta + A_BOT_DIE)
          + max(0.0, h_stag - h_ch) * A_stag_die) * GEO["n_die"]
    return dict(h_ch=h_ch, Nu=Nu, eta=eta, h_stag=h_stag, hA=hA, R=1 / hA,
                h_eff=hA / A_COVERED, Re_ch=cs["Re"], V_ch=cs["V"])


def r_chain(R_conv, R_tim2):
    return R_WALL + R_tim2 + R_conv


def h_required(target_R, R_tim2):
    left = target_R - R_WALL - R_tim2
    if left <= 0:
        return float("inf")
    return 1.0 / (left * A_COVERED)


def dp_budget(fl, Q_lpm):
    """板内压降预算。歧管/隔墙段按 CFD 前区间给"""
    js = jet_state(fl, Q_lpm * SPLIT_GPU)
    cs = channel_state(fl, Q_lpm * SPLIT_GPU, "cell")
    hs = hbm_state(fl, Q_lpm)
    man_lo, man_hi = 3000.0, 5000.0
    lo = js["dP"] + cs["dP"] + hs["dP"] + man_lo
    hi = js["dP"] + cs["dP"] + hs["dP"] + man_hi
    return dict(orifice=js["dP"], channel=cs["dP"], hbm=hs["dP"],
                manifold=(man_lo, man_hi), total=(lo, hi))


def solve(name, fl=WATER40):
    """给出某设计点的完整解"""
    d = DESIGN_POINTS[name]
    P, Q = d["P"], d["Q_lpm"]
    Qg = Q * SPLIT_GPU
    opt = h_model_optimistic(fl, Qg)
    con = h_model_conservative(fl, Qg)
    # Martin 无效时，上下界都用短槽模型，只留 TIM2 区间，不再外推 Martin。
    r_conv_lo = opt["R"] if opt["applied"] else con["R"]
    r_lo = r_chain(r_conv_lo, R_TIM2[0])
    r_hi = r_chain(con["R"], R_TIM2[1])
    p_die = P * FRAC["die"]
    p_gpu = p_die * GEO["n_die"]
    p_cell = p_gpu / N_JET
    mdot_hole = mass_flow(fl, Qg) / N_JET
    q_cell = p_cell / (A_CELL * 1e4)
    q_cell_si = p_cell / A_CELL
    return dict(
        name=name, P=P, Q=Q, Qg=Qg, Tin=d["Tin"], target=d["target_R"],
        role=d["role"], fluid=fl,
        dTf=delta_tf(fl, Q, P),
        dT_hole=p_cell / (mdot_hole * fl.cp),
        mdot_hole=mdot_hole,
        mdot_gpu=mass_flow(fl, Qg),
        jet=jet_state(fl, Qg), ch=channel_state(fl, Qg, "cell"),
        ch_bank=channel_state(fl, Qg, "bank"), hbm=hbm_state(fl, Q),
        opt=opt, con=con, dp=dp_budget(fl, Q),
        martin_applied=opt["applied"],
        R_lo=r_lo, R_hi=r_hi,
        dTc=(r_lo * P, r_hi * P),
        Tc=(d["Tin"] + r_lo * P, d["Tin"] + r_hi * P),
        Tj=(d["Tin"] + (r_lo + R_PKG[0]) * P,
            d["Tin"] + (r_hi + R_PKG[1]) * P),
        pass_lo=r_lo < d["target_R"], pass_hi=r_hi < d["target_R"],
        q_die=p_die / (A_DIE * 1e4),
        q_cell=q_cell,
        q_cell_si=q_cell_si,
        q_bc=Q_FLUX_MARGIN * q_cell,
        q_bc_si=Q_FLUX_MARGIN * q_cell_si,
        p_cell_bc=Q_FLUX_MARGIN * p_cell,
        p_gpu_bc=Q_FLUX_MARGIN * p_gpu,
        flux_margin=Q_FLUX_MARGIN,
        q_hbm=P * FRAC["hbm_total"] / GEO["n_hbm"] / (A_HBM * 1e4),
        q_plate=P / (A_PLATE * 1e4),
        p_die=p_die,
        p_gpu=p_gpu,
        p_cell=p_cell,
        p_hbm=P * FRAC["hbm_total"] / GEO["n_hbm"],
        p_other=P * FRAC["other"],
    )


def orifice_sweep(fl=WATER40, Q_lpm_gpu=1.6, N=N_JET, R_tim2=0.004,
                  diameters=(0.50, 0.45, 0.40, 0.35, 0.30)):
    rows = []
    for D in diameters:
        js = jet_state(fl, Q_lpm_gpu, D=D, N=N)
        f_a = (math.pi / 4 * D ** 2) / _CELL_PITCH
        applied = js["Re"] >= MARTIN_RE_MIN
        if applied:
            Nu, _ = nu_martin(js["Re"], fl.Pr, f=f_a, hd=GEO["H_jet"] / D)
            h = Nu * fl.k / (D * 1e-3)
            R = r_chain(1 / (h * A_COVERED), R_tim2)
            dTc = R * 1100
        else:
            h, R, dTc = None, None, None
        rows.append(dict(D=D, V=js["V"], Re=js["Re"], h=h, dP=js["dP"],
                         R=R, dTc=dTc, f=f_a, hd=GEO["H_jet"] / D,
                         sd_x=GEO["S_jet_x"] / D, sd_y=GEO["S_jet_y"] / D,
                         martin_applied=applied))
    return rows


def mech_checks(p_test=300e3):
    """机械校核：承压应力、变形、质量。p_test 默认 3 bar（表压）。
    模型：两端固支板条（保守），σ = p·L²/(2t²)，w = p·L⁴/(32·E·t³)"""
    def strip(L, t):
        sigma = p_test * L ** 2 / (2 * t ** 2)
        w = p_test * L ** 4 / (32 * E_CU * t ** 3)
        return sigma, w, SY_CU / sigma

    # 余铜跨单条槽
    s1, w1, n1 = strip(GEO["ch_p"] * 1e-3, GEO["base_cu"] * 1e-3)
    # 盖板跨射流阵无支撑区（保守：按阵面宽度）
    s2, w2, n2 = strip(GEO["jet_span"] * 1e-3, GEO["t_lid"] * 1e-3)
    # 盖板跨 HBM 区宽度
    s3, w3, n3 = strip(GEO["hbm_w"] * 1e-3, GEO["t_lid"] * 1e-3)

    V = GEO["plate_L"] * GEO["plate_W"] * GEO["plate_T"] * 1e-9
    fill = 0.82
    mass = V * 8900 * fill

    return dict(
        cases=[
            (f"余铜跨槽（跨 {GEO['ch_p']:.1f} mm，t={GEO['base_cu']:.1f} mm）",
             s1, w1, n1),
            (f"盖板跨射流阵（跨 {GEO['jet_span']:.0f} mm，"
             f"t={GEO['t_lid']:.1f} mm）", s2, w2, n2),
            (f"盖板跨 HBM 区（跨 {GEO['hbm_w']:.0f} mm，"
             f"t={GEO['t_lid']:.1f} mm）", s3, w3, n3),
        ],
        p_test=p_test, volume=V, fill=fill, mass=mass, sy=SY_CU)


def geometry_checks():
    g = GEO
    x = (g["hbm_x_l"] + g["hbm_w"] + 0.5 + g["rib"] + 0.5 + g["die_w"]
         + g["hbi"] + g["die_w"] + 0.5 + g["rib"] + 0.5 + g["hbm_w"]
         + g["hbm_x_l"])
    y = g["hbm_y0"] + g["rib_len"] + g["hbm_y0"]
    cav = g["base_cu"] + g["ch_h"] + g["H_jet"] + g["t_lid"]
    return [
        ("X 向链", f"5+11+0.5+2+0.5+27+3+27+0.5+2+0.5+11+5", x, g["plate_L"]),
        ("Y 向链", f"12.5+50+12.5", y, g["plate_W"]),
        ("腔体厚度", f"2.0+1.5+2.0+2.5", cav, 8.0),
        ("射流中心距 X", f"(9-1)x3.0", g["jet_span_x"], g["jet_span_x"]),
        ("射流中心距 Y", f"(12-1)x2.4", g["jet_span_y"], g["jet_span_y"]),
        ("覆盖长度 X", f"9x3.0", g["covered_x"], g["die_w"]),
        ("覆盖长度 Y", f"12x2.4", g["covered_y"], 28.8),
        ("Y 向超出 die", f"28.8-28", g["overhang_y"], 0.8),
        ("Y 向板外包络", f"28+1.2", g["envelope_y"], 29.2),
        ("外包络余量", f"29.2-28.8", g["envelope_margin_y"], 0.4),
        ("单 die 槽覆盖", f"{N_CH_DIE}x0.8", N_CH_DIE * g["ch_p"], g["die_h"]),
    ]

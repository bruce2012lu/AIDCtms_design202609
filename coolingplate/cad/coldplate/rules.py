"""设计规则校验：几何闭合、可制造性、热工水力自洽、与设计报告对账。

为什么必须有这一层：AI 改一个参数（比如把孔径从 0.50 压到 0.35 提高换热）
在 CAD 里照样能画出来，但钻头、过滤精度、压降窗口会同时被破坏。
几何画得出来 != 做得出来，所以判断放在建模之前。

三个等级：
  ERROR  几何或工艺硬冲突，禁止进 CAD
  WARN   落在文献 / 报告推荐窗之外，需人工确认
  INFO   与设计报告对账通过的数字，用于回归
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .model import Derived, Spec, x_symmetry_error

Level = Literal["ERROR", "WARN", "INFO"]

# 设计报告 v1.0 已公布的数字，用于反向对账。
# 任何一条对不上，说明参数集被改动过而报告没跟着更新。
REPORT_REFERENCE = {
    "jet_velocity_m_s": (1.06, 0.02),
    "jet_reynolds": (810.0, 20.0),
    "jet_area_total_mm2": (25.1, 0.1),
    "jet_count": (128, 0),
    "groove_velocity_m_s": (0.74, 0.02),
    "groove_reynolds": (710.0, 15.0),
    "groove_count_total": (60, 0),
    "hbm_channel_velocity_m_s": (0.46, 0.02),
    "fluid_temp_rise_k": (7.9, 0.15),
    "outlet_temp_c": (48.0, 0.2),
    "cavity_thickness": (8.0, 1e-6),
    "x_budget": (95.0, 1e-6),
}

# 工艺下限：底板铲齿 / CNC + 盖板微钻，不走整板金属 3D 打印
MIN_DRILL_DIA = 0.30        # 微钻可行下限
MIN_RIB_WIDTH = 0.30        # 齿壁最薄
MAX_GROOVE_ASPECT = 5.0     # 槽深 / 槽宽，再高铲齿会倒齿
MIN_BASE_REMAINING = 1.8    # 报告硬要求：扩热 + 刚度 + 防铣穿

# 文献窗（报告 §6 锁定表引用）
SD_WINDOW = (4.0, 8.0)
HD_WINDOW = (2.0, 6.0)


@dataclass(frozen=True)
class Finding:
    level: Level
    code: str
    message: str


class RuleViolation(RuntimeError):
    """存在 ERROR 级问题时由 require_clean 抛出。"""


def _approx(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol


def validate(spec: Spec, derived: Derived | None = None) -> list[Finding]:
    d = derived or spec.derive()
    out: list[Finding] = []
    out += _check_envelope(spec, d)
    out += _check_manufacturing(spec, d)
    out += _check_layout(spec, d)
    out += _check_hydraulics(spec, d)
    out += _check_against_report(d)
    return out


def require_clean(findings: list[Finding]) -> None:
    errors = [f for f in findings if f.level == "ERROR"]
    if errors:
        detail = "\n".join(f"  [{f.code}] {f.message}" for f in errors)
        raise RuleViolation(f"{len(errors)} 条 ERROR 级规则未通过，拒绝建模：\n{detail}")


# --- 外形与厚度栈 ---------------------------------------------------------

def _check_envelope(spec: Spec, d: Derived) -> list[Finding]:
    out: list[Finding] = []
    plate = spec.plate
    grooves = spec.grooves

    width = float(plate["width"])
    if not _approx(d.x_budget, width, 1e-6):
        out.append(Finding(
            "ERROR", "X_BUDGET",
            f"X 向尺寸链不闭合：逐段累加 {d.x_budget:.3f} mm，板宽 {width:.3f} mm",
        ))

    skew = x_symmetry_error(spec)
    if not _approx(skew, 0.0, 1e-6):
        out.append(Finding(
            "ERROR", "X_SYMMETRY",
            f"左右 HBM 列不对称，右列偏移 {skew:+.3f} mm；压装会偏载",
        ))

    outline = float(plate["thickness"])
    stack = d.cavity_thickness + float(plate["braze_seam"])
    if not _approx(stack, outline, 1e-6):
        out.append(Finding(
            "ERROR", "Z_STACK",
            f"厚度栈不闭合：腔 {d.cavity_thickness:.3f} + 钎缝 "
            f"{float(plate['braze_seam']):.3f} = {stack:.3f} mm，外形 {outline:.3f} mm",
        ))

    base_sum = float(plate["base_remaining"]) + float(grooves["depth"])
    if not _approx(base_sum, float(plate["base_plate_t"]), 1e-6):
        out.append(Finding(
            "ERROR", "BASE_PLATE",
            f"底板厚度对不上：余铜 {plate['base_remaining']} + 槽深 "
            f"{grooves['depth']} = {base_sum:.3f} mm，声明 {plate['base_plate_t']} mm",
        ))

    remaining = float(plate["base_remaining"])
    if remaining < MIN_BASE_REMAINING:
        out.append(Finding(
            "ERROR", "BASE_REMAINING",
            f"接触面余铜 {remaining} mm < 下限 {MIN_BASE_REMAINING} mm，"
            "扩热不足且有铣穿风险",
        ))
    return out


# --- 可制造性 -------------------------------------------------------------

def _check_manufacturing(spec: Spec, d: Derived) -> list[Finding]:
    out: list[Finding] = []
    jets, grooves, hbm = spec.jets, spec.grooves, spec.hbm

    dia = float(jets["diameter"])
    if dia < MIN_DRILL_DIA:
        out.append(Finding(
            "ERROR", "DRILL_DIA",
            f"喷嘴孔径 {dia} mm < 微钻下限 {MIN_DRILL_DIA} mm",
        ))

    rib = float(grooves["pitch"]) - float(grooves["width"])
    if rib < MIN_RIB_WIDTH:
        out.append(Finding(
            "ERROR", "GROOVE_RIB",
            f"GPU 槽齿壁 {rib:.3f} mm（节距 {grooves['pitch']} - 槽宽 "
            f"{grooves['width']}）< 下限 {MIN_RIB_WIDTH} mm",
        ))

    aspect = float(grooves["depth"]) / float(grooves["width"])
    if aspect > MAX_GROOVE_ASPECT:
        out.append(Finding(
            "ERROR", "GROOVE_ASPECT",
            f"GPU 槽深宽比 {aspect:.2f} > {MAX_GROOVE_ASPECT}，铲齿会倒齿",
        ))

    hbm_rib = float(hbm["channel_pitch"]) - float(hbm["channel_width"])
    if hbm_rib < MIN_RIB_WIDTH:
        out.append(Finding(
            "ERROR", "HBM_RIB",
            f"HBM 槽齿壁 {hbm_rib:.3f} mm < 下限 {MIN_RIB_WIDTH} mm",
        ))

    if d.groove_segment_length > float(grooves["max_length"]) + 1e-9:
        out.append(Finding(
            "ERROR", "GROOVE_LEN",
            f"短槽分段后单段 {d.groove_segment_length:.3f} mm > 上限 "
            f"{grooves['max_length']} mm，驻点后废液走太远会形成交叉流",
        ))

    # 过滤按最小孔径 1/10 校核，报告明确要求
    need_um = dia / 10.0 * 1000.0
    have_um = float(spec.raw["hydraulics"]["filtration_um"])
    if have_um > need_um:
        out.append(Finding(
            "ERROR", "FILTRATION",
            f"系统过滤 {have_um:.0f} μm 粗于最小孔径 1/10 判据 {need_um:.0f} μm，喷嘴会堵",
        ))
    return out


# --- 版图冲突 -------------------------------------------------------------

def _check_layout(spec: Spec, d: Derived) -> list[Finding]:
    out: list[Finding] = []
    plate = spec.plate
    pw, ph = float(plate["width"]), float(plate["height"])
    die_w, die_h = (float(v) for v in spec.raw["dies"]["size"])
    span_x, span_y = d.jet_array_span
    dia = float(spec.jets["diameter"])

    boxes: list[tuple[str, float, float, float, float]] = []

    for die in spec.dies:
        ox, oy = (float(v) for v in die["origin"])
        boxes.append((die["id"], ox, oy, die_w, die_h))
        if ox < 0 or oy < 0 or ox + die_w > pw or oy + die_h > ph:
            out.append(Finding(
                "ERROR", "DIE_OUT_OF_PLATE",
                f"{die['id']} 超出板外形：origin ({ox}, {oy})，尺寸 {die_w}x{die_h}",
            ))

        # 射流阵必须整个落在 die 投影内，否则打在空盖板上白费流量
        jx, jy = spec.jet_origin(die["id"])
        lo_x, hi_x = jx - dia / 2, jx + span_x + dia / 2
        lo_y, hi_y = jy - dia / 2, jy + span_y + dia / 2
        if lo_x < ox or hi_x > ox + die_w or lo_y < oy or hi_y > oy + die_h:
            out.append(Finding(
                "ERROR", "JET_ARRAY_OFF_DIE",
                f"{die['id']} 射流阵 [{lo_x:.2f},{hi_x:.2f}]x[{lo_y:.2f},{hi_y:.2f}] "
                f"越出 die 投影 [{ox},{ox + die_w}]x[{oy},{oy + die_h}]",
            ))

    # 不得对着 NV-HBI 缝打密孔
    if len(spec.dies) == 2:
        a, b = spec.dies[0], spec.dies[1]
        seam_lo = float(a["origin"][0]) + die_w
        seam_hi = float(b["origin"][0])
        actual_gap = seam_hi - seam_lo
        declared = float(spec.raw["dies"]["hbi_gap"])
        if not _approx(actual_gap, declared, 1e-6):
            out.append(Finding(
                "ERROR", "HBI_GAP",
                f"两 die 实际间距 {actual_gap:.3f} mm 与声明 HBI 缝 {declared} mm 不一致",
            ))
        for die in spec.dies:
            jx, _ = spec.jet_origin(die["id"])
            hi = jx + span_x + dia / 2
            if jx - dia / 2 < seam_hi and hi > seam_lo:
                out.append(Finding(
                    "ERROR", "JET_OVER_HBI",
                    f"{die['id']} 射流阵跨过 NV-HBI 缝 [{seam_lo}, {seam_hi}]",
                ))

    hbm_w, hbm_h = (float(v) for v in spec.hbm["size"])
    for idx, (ox, oy) in enumerate(spec.hbm_origins(), start=1):
        boxes.append((f"HBM-{idx}", ox, oy, hbm_w, hbm_h))
        if ox < 0 or oy < 0 or ox + hbm_w > pw or oy + hbm_h > ph:
            out.append(Finding(
                "ERROR", "HBM_OUT_OF_PLATE",
                f"HBM-{idx} 超出板外形：origin ({ox}, {oy})",
            ))

    if d.hbm_channel_span > hbm_w + 1e-9:
        out.append(Finding(
            "ERROR", "HBM_CHANNEL_SPAN",
            f"HBM 槽组宽 {d.hbm_channel_span:.3f} mm 超过 HBM 宽 {hbm_w} mm",
        ))

    groove_span = ((int(spec.grooves["count_per_die"]) - 1) * float(spec.grooves["pitch"])
                   + float(spec.grooves["width"]))
    if groove_span > die_h + 1e-9:
        out.append(Finding(
            "ERROR", "GROOVE_SPAN",
            f"GPU 槽组跨度 {groove_span:.3f} mm 超过 die 高 {die_h} mm",
        ))

    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            n1, x1, y1, w1, h1 = boxes[i]
            n2, x2, y2, w2, h2 = boxes[j]
            if x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1:
                out.append(Finding(
                    "ERROR", "FOOTPRINT_OVERLAP",
                    f"{n1} 与 {n2} 投影重叠",
                ))
    return out


# --- 热工水力 -------------------------------------------------------------

def _check_hydraulics(spec: Spec, d: Derived) -> list[Finding]:
    out: list[Finding] = []
    hyd = spec.raw["hydraulics"]
    jets, hbm = spec.jets, spec.hbm

    split_sum = float(hyd["split"]["gpu"]) + float(hyd["split"]["hbm"])
    if not _approx(split_sum, float(hyd["flow_total"]), 1e-9):
        out.append(Finding(
            "ERROR", "FLOW_SPLIT",
            f"分流之和 {split_sum:.3f} L/min != 设计流量 {hyd['flow_total']} L/min",
        ))

    th = spec.raw["thermal"]
    p = th["power_split_dp_a"]
    p_sum = 2 * float(p["die_each"]) + float(p["hbm_total"]) + float(p["io_other"])
    if not _approx(p_sum, float(th["dp_a_guarantee_w"]), 1e-6):
        out.append(Finding(
            "ERROR", "POWER_SPLIT",
            f"功率拆分之和 {p_sum:.1f} W != 保证点 {th['dp_a_guarantee_w']} W",
        ))

    cap = float(hbm["velocity_cap"])
    if d.hbm_channel_velocity_m_s > cap:
        out.append(Finding(
            "ERROR", "HBM_EROSION",
            f"HBM 槽内流速 {d.hbm_channel_velocity_m_s:.3f} m/s 超过冲蚀帽 {cap} m/s",
        ))

    sd = float(jets["pitch"]) / float(jets["diameter"])
    if not SD_WINDOW[0] <= sd <= SD_WINDOW[1]:
        out.append(Finding(
            "WARN", "SD_RATIO",
            f"S/D = {sd:.2f} 落在文献窗 {SD_WINDOW} 之外",
        ))

    hd = float(spec.plate["jet_standoff"]) / float(jets["diameter"])
    if not HD_WINDOW[0] <= hd <= HD_WINDOW[1]:
        out.append(Finding(
            "WARN", "HD_RATIO",
            f"H/D = {hd:.2f} 落在文献窗 {HD_WINDOW} 之外",
        ))

    lo, hi = (float(v) for v in hyd["dp_design"])
    target = float(hyd["dp_sample_target"])
    limit = float(hyd["dp_limit"])
    if not lo <= hi <= target <= limit:
        out.append(Finding(
            "ERROR", "DP_WINDOW",
            f"压降窗口不单调：设计 {lo}-{hi} / 送样目标 {target} / 上限 {limit} kPa",
        ))
    return out


# --- 与设计报告对账 -------------------------------------------------------

def _check_against_report(d: Derived) -> list[Finding]:
    out: list[Finding] = []
    for field, (expected, tol) in REPORT_REFERENCE.items():
        actual = float(getattr(d, field))
        if _approx(actual, float(expected), tol):
            out.append(Finding(
                "INFO", f"REF_{field.upper()}",
                f"{field} = {actual:.4g}，与报告 {expected:.4g} 一致",
            ))
        else:
            out.append(Finding(
                "WARN", f"REF_{field.upper()}",
                f"{field} = {actual:.4g}，与报告 {expected:.4g} 不一致"
                f"（容差 {tol:g}）——参数集已偏离 v1.0，请同步更新设计报告",
            ))
    return out

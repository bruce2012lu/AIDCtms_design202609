"""参数化建模：把冻结参数集变成实体。

坐标系与设计报告一致：原点在冷板左下角，X 向右，Y 向上，Z 向上为厚度方向。

Z 向栈（报告 图 P2b 为厚度基准）：
    0.0 - 2.0   接触面余铜
    2.0 - 3.5   GPU 短槽 / HBM 平槽（槽深 1.5）
    3.5 - 5.5   喷距 H = 2.0（隔离肋在此高度封死横流）
    5.5 - 8.0   喷嘴盖板 2.5
    8.0 - 8.5   周边钎缝 / 水嘴台阶

刻意不建的东西（报告已注明须 CFD 才能定，不在此处编造）：
    盖板静压箱与隔墙、进出液水嘴、UQD 接口。
"""

from __future__ import annotations

from dataclasses import dataclass

from build123d import Align, Box, Compound, Cylinder, Part, Pos

from .model import Derived, Spec

_MIN3 = (Align.MIN, Align.MIN, Align.MIN)

# 切除体必须冲出被切面，否则 OCC 在共面布尔上会直接段错误。
# 槽顶本来就和底板顶面同在 z=3.5，不加过切必崩。
_OVERSHOOT = 1.0

# 一次性拿 200+ 个工具体做布尔，OCC 会间歇性访问越界（实测约 1/12 概率的
# 进程级崩溃，且崩溃点不固定）。分批切除后未再复现。
_CUT_BATCH = 24


def _cut_batched(solid: Part, cutters: list[Part], batch: int = _CUT_BATCH) -> Part:
    for i in range(0, len(cutters), batch):
        solid = solid - Compound(cutters[i:i + batch])
    return solid


@dataclass
class ColdPlateBuild:
    """一次建模的全部产物。"""

    base_plate: Part
    nozzle_plate: Part
    seal_frame: Part

    @property
    def parts(self) -> dict[str, Part]:
        return {
            "JM01-100_base_plate": self.base_plate,
            "JM01-200_nozzle_plate": self.nozzle_plate,
            "JM01-400_seal_frame": self.seal_frame,
        }


def _groove_y_centers(die_origin_y: float, die_h: float,
                      count: int, pitch: float, width: float) -> list[float]:
    """短槽沿 Y 等距排布并在 die 高度内居中。"""
    span = (count - 1) * pitch + width
    start = die_origin_y + (die_h - span) / 2.0 + width / 2.0
    return [start + k * pitch for k in range(count)]


def _groove_x_segments(die_origin_x: float, die_w: float,
                       segments: int, seg_len: float, land: float) -> list[float]:
    """返回每段短槽的中心 X。段间铜岛是抽吸位，也切断了沿程交叉流。"""
    return [die_origin_x + i * (seg_len + land) + seg_len / 2.0
            for i in range(segments)]


def _rib_x_origins(spec: Spec) -> list[float]:
    """隔离肋左下角 X：夹在 HBM 列与 die 之间，两侧对称。"""
    hbm_w = float(spec.hbm["size"][0])
    rib_w = float(spec.raw["rib"]["width"])
    hbm_left_right_edge = float(spec.hbm["columns_x"][0]) + hbm_w
    die_a_x = float(spec.dies[0]["origin"][0])
    gap = die_a_x - hbm_left_right_edge - rib_w

    die_w = float(spec.raw["dies"]["size"][0])
    die_b_right = float(spec.dies[-1]["origin"][0]) + die_w
    return [hbm_left_right_edge + gap / 2.0, die_b_right + gap / 2.0]


def build_base_plate(spec: Spec, d: Derived) -> Part:
    """换热底板：余铜 + GPU 短槽 + HBM 平槽 + 立起的隔离肋。"""
    plate = spec.plate
    pw, ph = float(plate["width"]), float(plate["height"])
    base_t = float(plate["base_plate_t"])
    remaining = float(plate["base_remaining"])

    solid = Box(pw, ph, base_t, align=_MIN3)

    grooves = spec.grooves
    gw, gd = float(grooves["width"]), float(grooves["depth"])
    # 槽底停在余铜面，槽顶冲出板顶
    cut_h = gd + _OVERSHOOT
    z_mid = remaining + cut_h / 2.0
    die_w, die_h = (float(v) for v in spec.raw["dies"]["size"])

    cutters: list[Part] = []

    for die in spec.dies:
        ox, oy = (float(v) for v in die["origin"])
        ys = _groove_y_centers(oy, die_h, int(grooves["count_per_die"]),
                               float(grooves["pitch"]), gw)
        xs = _groove_x_segments(ox, die_w, d.groove_segments,
                                d.groove_segment_length, float(grooves["segment_land"]))
        for y in ys:
            for x in xs:
                cutters.append(Pos(x, y, z_mid)
                               * Box(d.groove_segment_length, gw, cut_h))

    # HBM 侧：无喷嘴，只走贯通整列的平槽，流程沿 HBM 列长边（Y）
    hbm = spec.hbm
    hw, hh = (float(v) for v in hbm["size"])
    hbm_ch_w, hbm_ch_d = float(hbm["channel_width"]), float(hbm["channel_depth"])
    col_lo = float(hbm["rows_y"][0])
    col_hi = float(hbm["rows_y"][-1]) + hh
    col_len = col_hi - col_lo
    col_mid = (col_lo + col_hi) / 2.0
    n_ch = int(hbm["channels_per_side"])
    ch_pitch = float(hbm["channel_pitch"])

    hbm_cut_h = hbm_ch_d + _OVERSHOOT
    for col_x in hbm["columns_x"]:
        start = float(col_x) + (hw - d.hbm_channel_span) / 2.0 + hbm_ch_w / 2.0
        for k in range(n_ch):
            cutters.append(Pos(start + k * ch_pitch, col_mid,
                               remaining + hbm_cut_h / 2.0)
                           * Box(hbm_ch_w, col_len, hbm_cut_h))

    solid = _cut_batched(solid, cutters)

    # 隔离肋填满 H 间隙，从槽底连到盖板，横流过不去。
    # 肋向下埋进底板 _OVERSHOOT：肋所在的 X 带位于 HBM 列与 die 之间，本来就是
    # 实心铜，重叠融合比面贴面融合稳，外形结果一致。
    rib_w = float(spec.raw["rib"]["width"])
    rib_h = float(plate["jet_standoff"]) + _OVERSHOOT
    ribs = [Pos(rx, 0.0, base_t - _OVERSHOOT) * Box(rib_w, ph, rib_h, align=_MIN3)
            for rx in _rib_x_origins(spec)]
    return solid + Compound(ribs)


def build_nozzle_plate(spec: Spec, d: Derived) -> Part:
    """喷嘴盖板：128 个 GPU 喷嘴 + 错排抽吸孔。HBM 区不开孔。

    本地坐标 z 从 0 起，装配时再抬到 5.5。
    """
    plate = spec.plate
    pw, ph = float(plate["width"]), float(plate["height"])
    t = float(plate["nozzle_plate_t"])

    solid = Box(pw, ph, t, align=_MIN3)

    jets = spec.jets
    dia = float(jets["diameter"])
    pitch = float(jets["pitch"])
    nx, ny = int(jets["count_x"]), int(jets["count_y"])
    suction_dia = float(jets["suction_diameter"])

    through = t * 2.0  # 留穿透余量，避免共面布尔
    cutters: list[Part] = []

    for die in spec.dies:
        jx, jy = spec.jet_origin(die["id"])
        for i in range(nx):
            for j in range(ny):
                cutters.append(Pos(jx + i * pitch, jy + j * pitch, t / 2.0)
                               * Cylinder(dia / 2.0, through))
        # 抽吸孔错排在每四个喷嘴的中心
        for i in range(nx - 1):
            for j in range(ny - 1):
                cutters.append(
                    Pos(jx + (i + 0.5) * pitch, jy + (j + 0.5) * pitch, t / 2.0)
                    * Cylinder(suction_dia / 2.0, through)
                )

    return _cut_batched(solid, cutters)


def build_seal_frame(spec: Spec) -> Part:
    """周边钎缝 / 水嘴台阶，占掉外形 8.5 与腔 8.0 之间那 0.5 mm。"""
    plate = spec.plate
    pw, ph = float(plate["width"]), float(plate["height"])
    t = float(plate["braze_seam"])
    rib_w = float(spec.raw["rib"]["width"])

    outer = Box(pw, ph, t, align=_MIN3)
    inner = Pos(rib_w, rib_w, -t) * Box(pw - 2 * rib_w, ph - 2 * rib_w, t * 3,
                                        align=_MIN3)
    return outer - inner


def build(spec: Spec, d: Derived | None = None) -> ColdPlateBuild:
    """建出三个零件，各自本地坐标 z 从 0 起。"""
    dv = d or spec.derive()
    return ColdPlateBuild(
        base_plate=build_base_plate(spec, dv),
        nozzle_plate=build_nozzle_plate(spec, dv),
        seal_frame=build_seal_frame(spec),
    )


def assemble(spec: Spec, build_result: ColdPlateBuild) -> Compound:
    """按 Z 栈把三个零件叠成总装，外形应为 95 x 75 x 8.5。"""
    plate = spec.plate
    base_t = float(plate["base_plate_t"])
    standoff = float(plate["jet_standoff"])
    nozzle_t = float(plate["nozzle_plate_t"])

    nozzle_z = base_t + standoff
    seal_z = nozzle_z + nozzle_t

    # 一律经 Pos 生成副本再挂进总装。直接把零件塞进 Compound 会给它指定父节点，
    # 之后单独导出该零件的 STEP 就会失败。
    base = Pos(0, 0, 0) * build_result.base_plate
    nozzle = Pos(0, 0, nozzle_z) * build_result.nozzle_plate
    seal = Pos(0, 0, seal_z) * build_result.seal_frame

    base.label = "JM01-100_base_plate"
    nozzle.label = "JM01-200_nozzle_plate"
    seal.label = "JM01-400_seal_frame"

    return Compound(children=[base, nozzle, seal], label=spec.model)

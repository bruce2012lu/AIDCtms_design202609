"""AutoCAD 后端：把锁定布置输出成分层 DXF 顶视图。

DXF 走 ezdxf 直写，不需要装 AutoCAD 就能生成，装了 AutoCAD / 中望 / DWG
TrueView 直接能开。图层按功能拆开，方便审图时单独关掉射流阵看槽。

这张图对齐的是设计报告 §图纸与尺寸 的锁定封装坐标，比例 1:1 mm。
"""

from __future__ import annotations

from pathlib import Path

import ezdxf
from ezdxf.enums import TextEntityAlignment

from ..model import Derived, Spec

# 图层名 : (AutoCAD 颜色号, 说明)
# 不用 ACI 7：它是「随背景反色」，光栅化到白底会变成白线直接看不见。
LAYERS = {
    "PLATE_OUTLINE": (250, "冷板外形 95x75"),
    "DIE": (1, "计算 die 投影 27x28"),
    "HBM": (3, "HBM 堆叠投影 11x11"),
    "RIB": (5, "隔离肋 2.0 宽"),
    "GPU_GROOVE": (4, "GPU 短槽 0.40x1.50"),
    "HBM_CHANNEL": (6, "HBM 平槽 0.60x1.50"),
    "JET": (2, "微射流孔 D0.50"),
    "SUCTION": (30, "抽吸孔（候选）"),
    "LABEL": (250, "零件标注（ASCII）"),
    "NOTE": (250, "图注（中文）"),
}

# 中文图注单独占一个图层：AutoCAD 侧靠 CJK 文字样式解析，
# 光栅化预览侧则关掉本层、由 preview 用 matplotlib 重绘，
# 因为 ezdxf 的字体管理器不一定认得到系统中文字体。
CJK_STYLE = "CJK"
CJK_FONT = "msyh.ttf"  # 微软雅黑
NOTE_LAYER = "NOTE"


def export(spec: Spec, d: Derived, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = build_doc(spec, d)
    path = out_dir / f"{spec.model}_top_view.dxf"
    doc.saveas(path)
    return [path]


def build_doc(spec: Spec, d: Derived):
    """构造顶视图 DXF 文档。preview 后端复用它，保证图纸与预览图不会分叉。"""
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4  # mm
    msp = doc.modelspace()

    for name, (color, _desc) in LAYERS.items():
        doc.layers.add(name=name, color=color)
    doc.styles.add(CJK_STYLE, font=CJK_FONT)

    plate = spec.plate
    pw, ph = float(plate["width"]), float(plate["height"])
    _rect(msp, 0, 0, pw, ph, "PLATE_OUTLINE")

    die_w, die_h = (float(v) for v in spec.raw["dies"]["size"])
    grooves = spec.grooves
    gw = float(grooves["width"])

    from ..geometry import _groove_x_segments, _groove_y_centers, _rib_x_origins

    for die in spec.dies:
        ox, oy = (float(v) for v in die["origin"])
        _rect(msp, ox, oy, die_w, die_h, "DIE")
        _label(msp, ox + die_w / 2, oy + die_h + 1.2, die["id"], 2.2)

        for y in _groove_y_centers(oy, die_h, int(grooves["count_per_die"]),
                                   float(grooves["pitch"]), gw):
            for x in _groove_x_segments(ox, die_w, d.groove_segments,
                                        d.groove_segment_length,
                                        float(grooves["segment_land"])):
                _rect(msp, x - d.groove_segment_length / 2, y - gw / 2,
                      d.groove_segment_length, gw, "GPU_GROOVE")

        jx, jy = spec.jet_origin(die["id"])
        pitch = float(spec.jets["pitch"])
        r_jet = float(spec.jets["diameter"]) / 2
        r_suc = float(spec.jets["suction_diameter"]) / 2
        for i in range(int(spec.jets["count_x"])):
            for j in range(int(spec.jets["count_y"])):
                msp.add_circle((jx + i * pitch, jy + j * pitch), r_jet,
                               dxfattribs={"layer": "JET"})
        for i in range(int(spec.jets["count_x"]) - 1):
            for j in range(int(spec.jets["count_y"]) - 1):
                msp.add_circle((jx + (i + 0.5) * pitch, jy + (j + 0.5) * pitch),
                               r_suc, dxfattribs={"layer": "SUCTION"})

    hbm = spec.hbm
    hw, hh = (float(v) for v in hbm["size"])
    for idx, (ox, oy) in enumerate(spec.hbm_origins(), start=1):
        _rect(msp, ox, oy, hw, hh, "HBM")
        _label(msp, ox + hw / 2, oy + hh / 2, f"H{idx}", 1.6)

    ch_w = float(hbm["channel_width"])
    ch_pitch = float(hbm["channel_pitch"])
    col_lo = float(hbm["rows_y"][0])
    col_hi = float(hbm["rows_y"][-1]) + hh
    for col_x in hbm["columns_x"]:
        start = float(col_x) + (hw - d.hbm_channel_span) / 2.0
        for k in range(int(hbm["channels_per_side"])):
            x0 = start + k * ch_pitch
            _rect(msp, x0, col_lo, ch_w, col_hi - col_lo, "HBM_CHANNEL")

    rib_w = float(spec.raw["rib"]["width"])
    for rx in _rib_x_origins(spec):
        _rect(msp, rx, 0, rib_w, ph, "RIB")

    _notes(msp, spec, d, pw, ph)
    return doc


def _rect(msp, x: float, y: float, w: float, h: float, layer: str) -> None:
    msp.add_lwpolyline(
        [(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
        close=True, dxfattribs={"layer": layer},
    )


def _label(msp, x: float, y: float, text: str, height: float) -> None:
    msp.add_text(
        text, height=height, dxfattribs={"layer": "LABEL"},
    ).set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)


def note_lines(spec: Spec, d: Derived) -> list[str]:
    """图注内容。DXF 与 PNG 预览共用，避免两处各写一版说明。"""
    pw, ph = float(spec.plate["width"]), float(spec.plate["height"])
    return [
        f"{spec.model} · {spec.raw['meta']['title']}",
        f"外形 {pw}x{ph}x{spec.plate['thickness']} mm · 材料 {spec.raw['material']['body']}",
        f"射流 D{spec.jets['diameter']} x {d.jet_count} 孔 · S/D="
        f"{float(spec.jets['pitch']) / float(spec.jets['diameter']):.0f} · H/D="
        f"{float(spec.plate['jet_standoff']) / float(spec.jets['diameter']):.0f}",
        f"孔速 {d.jet_velocity_m_s:.2f} m/s · Re_D {d.jet_reynolds:.0f}"
        f" · 短槽 {d.groove_velocity_m_s:.2f} m/s",
        f"设计流量 {spec.raw['hydraulics']['flow_total']} L/min"
        f"（GPU {spec.raw['hydraulics']['split']['gpu']} / HBM"
        f" {spec.raw['hydraulics']['split']['hbm']}）",
        f"混合温升 {d.fluid_temp_rise_k:.1f} K · 出口 {d.outlet_temp_c:.1f} C"
        f"（0 维，非壁温非结温）",
        f"状态 {spec.raw['meta']['status']} · 几何为候选，待订单 ICD 冻结",
    ]


NOTE_LINE_PITCH = 3.4
NOTE_TOP_Y = -6.0


def _notes(msp, spec: Spec, d: Derived, pw: float, ph: float) -> None:
    del pw, ph
    for i, text in enumerate(note_lines(spec, d)):
        msp.add_text(
            text, height=2.0,
            dxfattribs={"layer": NOTE_LAYER, "style": CJK_STYLE},
        ).set_placement((0, NOTE_TOP_Y - i * NOTE_LINE_PITCH),
                        align=TextEntityAlignment.LEFT)

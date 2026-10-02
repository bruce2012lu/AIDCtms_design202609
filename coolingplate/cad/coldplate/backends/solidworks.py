"""SOLIDWORKS 后端：COM 程序合成，不走 GUI 点击。

为什么是 COM 而不是让 agent 点鼠标：ComAct（arXiv 2606.13239）在真实工业
CAD 上测出纯 GUI 交互的成功率接近于零——视觉定位脆、长程误差累积；换成
COM 把任务变成确定性的程序合成后才有实质提升。所以本后端把「AI 调用 CAD」
实现为「AI 生成并执行 COM 调用」，几何正确性由 rules.py 在调用之前保证。

两条路径：
    emit_vba()  纯文本生成 VBA 宏，任何机器都能产出，拿到装了 SOLIDWORKS
                的机器上直接跑。宏内部用 For 循环建几何，保持可读可改。
    drive()     本机实时 COM。导入中性 STEP + 把参数集写成 SOLIDWORKS 全局
                变量，存成 SLDPRT，得到一个带参数表、可继续编辑的原生模型。

注意：本机未安装 SOLIDWORKS，因此本模块的 COM 调用与 VBA 宏均**未经实机
验证**。API 签名按 SOLIDWORKS 2021+ 写；首次在实机运行时需要核对
FeatureExtrusion3 / FeatureCut4 的参数个数。
"""

from __future__ import annotations

from pathlib import Path

from ..model import Derived, Spec

MM = 1.0e-3  # SOLIDWORKS API 一律用米


class BackendUnavailable(RuntimeError):
    """本机没有可用的 SOLIDWORKS COM 服务。"""


def is_available() -> bool:
    try:
        import win32com.client  # noqa: PLC0415
    except ImportError:
        return False
    try:
        win32com.client.Dispatch("SldWorks.Application")
    except Exception:
        return False
    return True


# --- 参数表：给 SOLIDWORKS 全局变量用 -------------------------------------

def parameter_table(spec: Spec, d: Derived) -> list[tuple[str, float, str]]:
    """(变量名, 值 mm, 说明)。写进 SOLIDWORKS 方程管理器后模型即可参数化重建。"""
    plate, jets, grooves, hbm = spec.plate, spec.jets, spec.grooves, spec.hbm
    return [
        ("PlateWidth", float(plate["width"]), "冷板外形 X"),
        ("PlateHeight", float(plate["height"]), "冷板外形 Y"),
        ("PlateThickness", float(plate["thickness"]), "外形总厚，含钎缝"),
        ("BasePlateT", float(plate["base_plate_t"]), "换热底板厚"),
        ("BaseRemaining", float(plate["base_remaining"]), "接触面余铜，下限 1.8"),
        ("NozzlePlateT", float(plate["nozzle_plate_t"]), "喷嘴盖板厚"),
        ("JetStandoff", float(plate["jet_standoff"]), "喷距 H"),
        ("JetDia", float(jets["diameter"]), "喷嘴孔径 D"),
        ("JetPitch", float(jets["pitch"]), "孔间距 S"),
        ("SuctionDia", float(jets["suction_diameter"]), "抽吸孔径（候选）"),
        ("GrooveWidth", float(grooves["width"]), "GPU 短槽宽"),
        ("GrooveDepth", float(grooves["depth"]), "GPU 短槽深"),
        ("GroovePitch", float(grooves["pitch"]), "GPU 短槽节距"),
        ("GrooveSegLen", d.groove_segment_length, "短槽单段长，须 <= 8"),
        ("HbmChannelWidth", float(hbm["channel_width"]), "HBM 平槽宽"),
        ("HbmChannelDepth", float(hbm["channel_depth"]), "HBM 平槽深"),
        ("HbmChannelPitch", float(hbm["channel_pitch"]), "HBM 平槽节距"),
        ("RibWidth", float(spec.raw["rib"]["width"]), "隔离肋宽"),
    ]


# --- 路径 A：生成 VBA 宏 ---------------------------------------------------

def emit_vba(spec: Spec, d: Derived) -> str:
    """生成可在 SOLIDWORKS 里直接运行的建模宏。

    宏里保留 For 循环而不是把 240 条槽展开成上千行直线，这样工程师打开宏
    还能改节距和条数，而不是面对一堆魔法坐标。
    """
    plate, jets, grooves, hbm = spec.plate, spec.jets, spec.grooves, spec.hbm
    die_w, die_h = (float(v) for v in spec.raw["dies"]["size"])
    gw = float(grooves["width"])
    groove_span = (int(grooves["count_per_die"]) - 1) * float(grooves["pitch"]) + gw

    consts = [
        ("PLATE_W", float(plate["width"])),
        ("PLATE_H", float(plate["height"])),
        ("BASE_T", float(plate["base_plate_t"])),
        ("BASE_REM", float(plate["base_remaining"])),
        ("NOZZLE_T", float(plate["nozzle_plate_t"])),
        ("STANDOFF", float(plate["jet_standoff"])),
        ("JET_D", float(jets["diameter"])),
        ("JET_S", float(jets["pitch"])),
        ("SUCTION_D", float(jets["suction_diameter"])),
        ("G_W", gw),
        ("G_D", float(grooves["depth"])),
        ("G_PITCH", float(grooves["pitch"])),
        ("G_SEGLEN", d.groove_segment_length),
        ("G_LAND", float(grooves["segment_land"])),
        ("DIE_W", die_w),
        ("DIE_H", die_h),
        ("GROOVE_SPAN", groove_span),
        ("HBM_CH_W", float(hbm["channel_width"])),
        ("HBM_CH_D", float(hbm["channel_depth"])),
        ("HBM_CH_PITCH", float(hbm["channel_pitch"])),
        ("HBM_SPAN", d.hbm_channel_span),
        ("HBM_W", float(hbm["size"][0])),
        ("RIB_W", float(spec.raw["rib"]["width"])),
    ]

    lines: list[str] = [
        f"' {spec.model} · {spec.raw['meta']['title']}",
        f"' 由 coldplate/backends/solidworks.py 自动生成 · 参数源 {spec.source.name if spec.source else 'params'}",
        "' 单位：常量用 mm，调用 API 前统一乘 MM 换成米。",
        "' 状态：几何为候选，待订单 ICD 冻结。本宏未经实机验证。",
        "",
        "Option Explicit",
        "",
        "Const MM As Double = 0.001",
    ]
    for name, val in consts:
        lines.append(f"Const {name} As Double = {val:g}")

    die_args = ", ".join(
        f"{float(die['origin'][0]):g}, {float(die['origin'][1]):g}"
        for die in spec.dies
    )
    jet_args = ", ".join(
        f"{spec.jet_origin(die['id'])[0]:g}, {spec.jet_origin(die['id'])[1]:g}"
        for die in spec.dies
    )

    lines += [
        "",
        f"Const N_JET_X As Long = {int(jets['count_x'])}",
        f"Const N_JET_Y As Long = {int(jets['count_y'])}",
        f"Const N_GROOVE As Long = {int(grooves['count_per_die'])}",
        f"Const N_SEG As Long = {d.groove_segments}",
        f"Const N_HBM_CH As Long = {int(hbm['channels_per_side'])}",
        "",
        "Dim swApp As Object",
        "Dim swModel As Object",
        "Dim swSketch As Object",
        "",
        "Sub main()",
        "    Set swApp = Application.SldWorks",
        "    BuildBasePlate",
        "    BuildNozzlePlate",
        "End Sub",
        "",
        "' ---- 换热底板：余铜 + 短槽 + HBM 平槽 + 隔离肋 ----",
        "Sub BuildBasePlate()",
        "    Dim dieX(1) As Double, dieY(1) As Double",
        "    Dim i As Long, j As Long, k As Long",
        f"    LoadPairs dieX, dieY, Array({die_args})",
        "",
        "    Set swModel = swApp.NewPart",
        "    swModel.SketchManager.InsertSketch True",
        "    swModel.SketchManager.CreateCornerRectangle 0, 0, 0, PLATE_W * MM, PLATE_H * MM, 0",
        "    swModel.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, _",
        "        BASE_T * MM, 0, False, False, False, False, 0, 0, _",
        "        False, False, False, False, True, True, True, 0, 0, False",
        "",
        "    ' 所有槽画在同一张草图里，一次切除，避免 250 个特征拖垮重建",
        "    swModel.SketchManager.Insert3DSketch False",
        "    SelectTopFace",
        "    swModel.SketchManager.InsertSketch True",
        "    For i = 0 To UBound(dieX)",
        "        Dim y0 As Double",
        "        y0 = dieY(i) + (DIE_H - GROOVE_SPAN) / 2",
        "        For j = 0 To N_GROOVE - 1",
        "            Dim gy As Double",
        "            gy = y0 + j * G_PITCH",
        "            For k = 0 To N_SEG - 1",
        "                Dim gx As Double",
        "                gx = dieX(i) + k * (G_SEGLEN + G_LAND)",
        "                swModel.SketchManager.CreateCornerRectangle _",
        "                    gx * MM, gy * MM, 0, (gx + G_SEGLEN) * MM, (gy + G_W) * MM, 0",
        "            Next k",
        "        Next j",
        "    Next i",
        "    AddHbmChannelRects",
        "    swModel.FeatureManager.FeatureCut4 True, False, False, 0, 0, _",
        "        G_D * MM, 0, False, False, False, False, 0, 0, _",
        "        False, False, False, False, False, True, True, 0, 0, False, False",
        "",
        "    AddIsolationRibs",
        "    swModel.ViewZoomtofit2",
        "End Sub",
        "",
        "' HBM 两侧平槽：贯通整列，流程沿列长边",
        "Sub AddHbmChannelRects()",
        "    Dim colX(1) As Double",
        f"    colX(0) = {float(hbm['columns_x'][0]):g}: colX(1) = {float(hbm['columns_x'][-1]):g}",
        f"    Const COL_LO As Double = {float(hbm['rows_y'][0]):g}",
        f"    Const COL_HI As Double = {float(hbm['rows_y'][-1]) + float(hbm['size'][1]):g}",
        "    Dim c As Long, k As Long, x0 As Double",
        "    For c = 0 To 1",
        "        x0 = colX(c) + (HBM_W - HBM_SPAN) / 2",
        "        For k = 0 To N_HBM_CH - 1",
        "            Dim cx As Double",
        "            cx = x0 + k * HBM_CH_PITCH",
        "            swModel.SketchManager.CreateCornerRectangle _",
        "                cx * MM, COL_LO * MM, 0, (cx + HBM_CH_W) * MM, COL_HI * MM, 0",
        "        Next k",
        "    Next c",
        "End Sub",
        "",
        "' 隔离肋填满 H 间隙，从槽底连到盖板，切断 GPU 区横流",
        "Sub AddIsolationRibs()",
        "    Dim ribX(1) As Double",
    ]

    from ..geometry import _rib_x_origins
    ribs = _rib_x_origins(spec)
    lines += [
        f"    ribX(0) = {ribs[0]:g}: ribX(1) = {ribs[1]:g}",
        "    Dim r As Long",
        "    SelectTopFace",
        "    swModel.SketchManager.InsertSketch True",
        "    For r = 0 To 1",
        "        swModel.SketchManager.CreateCornerRectangle _",
        "            ribX(r) * MM, 0, 0, (ribX(r) + RIB_W) * MM, PLATE_H * MM, 0",
        "    Next r",
        "    swModel.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, _",
        "        STANDOFF * MM, 0, False, False, False, False, 0, 0, _",
        "        False, False, False, False, True, True, True, 0, 0, False",
        "End Sub",
        "",
        "' ---- 喷嘴盖板：128 个喷嘴 + 错排抽吸孔，HBM 区不开孔 ----",
        "Sub BuildNozzlePlate()",
        "    Dim jetX(1) As Double, jetY(1) As Double",
        "    Dim i As Long, j As Long, k As Long",
        f"    LoadPairs jetX, jetY, Array({jet_args})",
        "",
        "    Set swModel = swApp.NewPart",
        "    swModel.SketchManager.InsertSketch True",
        "    swModel.SketchManager.CreateCornerRectangle 0, 0, 0, PLATE_W * MM, PLATE_H * MM, 0",
        "    swModel.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, _",
        "        NOZZLE_T * MM, 0, False, False, False, False, 0, 0, _",
        "        False, False, False, False, True, True, True, 0, 0, False",
        "",
        "    SelectTopFace",
        "    swModel.SketchManager.InsertSketch True",
        "    For i = 0 To UBound(jetX)",
        "        For j = 0 To N_JET_X - 1",
        "            For k = 0 To N_JET_Y - 1",
        "                swModel.SketchManager.CreateCircleByRadius _",
        "                    (jetX(i) + j * JET_S) * MM, (jetY(i) + k * JET_S) * MM, 0, JET_D / 2 * MM",
        "            Next k",
        "        Next j",
        "        For j = 0 To N_JET_X - 2",
        "            For k = 0 To N_JET_Y - 2",
        "                swModel.SketchManager.CreateCircleByRadius _",
        "                    (jetX(i) + (j + 0.5) * JET_S) * MM, _",
        "                    (jetY(i) + (k + 0.5) * JET_S) * MM, 0, SUCTION_D / 2 * MM",
        "            Next k",
        "        Next j",
        "    Next i",
        "    ' 通孔：ThroughAll",
        "    swModel.FeatureManager.FeatureCut4 True, False, False, 1, 0, _",
        "        NOZZLE_T * MM, 0, False, False, False, False, 0, 0, _",
        "        False, False, False, False, False, True, True, 0, 0, False, False",
        "    swModel.ViewZoomtofit2",
        "End Sub",
        "",
        "Sub SelectTopFace()",
        "    swModel.Extension.SelectByRay 0.001, BASE_T * MM * 2, 0.001, _",
        "        0, -1, 0, 0.0005, 2, False, 0, 0",
        "End Sub",
        "",
        "Sub LoadPairs(xs() As Double, ys() As Double, flat As Variant)",
        "    Dim n As Long, i As Long",
        "    n = (UBound(flat) + 1) \\ 2",
        "    For i = 0 To n - 1",
        "        xs(i) = flat(i * 2)",
        "        ys(i) = flat(i * 2 + 1)",
        "    Next i",
        "End Sub",
        "",
    ]
    return "\n".join(lines) + "\n"


# --- 路径 B：实时 COM ------------------------------------------------------

def drive(spec: Spec, d: Derived, step_path: Path, out_dir: Path) -> list[Path]:
    """导入中性 STEP，写入参数表，存成 SLDPRT。

    先导 STEP 再挂参数表，是为了让实机第一次跑就能出一个可打开的原生文件；
    要完全参数化的原生特征树，用 emit_vba() 那条路径。
    """
    if not is_available():
        raise BackendUnavailable(
            "未检测到 SOLIDWORKS COM 服务（SldWorks.Application）。\n"
            "本机没装 SOLIDWORKS，请改用 emit_vba() 产出宏，拿到实机上运行。"
        )
    import win32com.client  # noqa: PLC0415

    out_dir.mkdir(parents=True, exist_ok=True)
    sw = win32com.client.Dispatch("SldWorks.Application")
    sw.Visible = True

    errors, warnings = 0, 0
    model = sw.OpenDoc6(str(step_path.resolve()), 1, 0, "", errors, warnings)
    if model is None:
        raise BackendUnavailable(f"SOLIDWORKS 无法打开 {step_path}")

    eq = model.GetEquationMgr()
    for name, value, note in parameter_table(spec, d):
        eq.Add3(-1, f'"{name}" = {value:g}', True, 0)
        del note  # 说明只用于 emit_vba 与文档，方程里不带注释

    target = out_dir / f"{spec.model}.SLDPRT"
    model.SaveAs3(str(target.resolve()), 0, 2)
    return [target]


def write_macro(spec: Spec, d: Derived, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{spec.model}_build.swp.bas"
    path.write_text(emit_vba(spec, d), encoding="utf-8")
    return [path]

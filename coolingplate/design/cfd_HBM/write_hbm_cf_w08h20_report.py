# -*- coding: utf-8 -*-
"""Write the counterflow iter-200 result report. Does not touch the co-flow reports."""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figs" / "cf_i200"
OUT = ROOT / "HBM_cf_w08h20_ICEM_Fluent_结果报告_i200.html"

TIN = 313.15
T_WALL = 333.89475
T_MAX = 335.81461
T_MIN = 329.31686
T_CU = 329.73845
T_OUT_LO_M = 317.70174
T_OUT_HI_M = 317.22398
T_OUT_LO_A = 315.99503
T_OUT_HI_A = 315.005
T_OUT_M = 317.48471
T_OUT_A = 315.50002
V_LO = 0.29761876
V_HI = 0.29761885
P_LO = 378.01107
P_HI = 379.76601
P_NET = 379.01389
MDOT_LO = 0.0014174272
MDOT_HI = 0.0018899035
MDOT_OUT_LO = 0.0018899036
MDOT_OUT_HI = 0.001417428
MDOT_NET = -9.0213689e-10
CP = 4179.0
AREA = 0.000484
P_W = 205000.0 * AREA
Q_ENERGY = (
    MDOT_OUT_LO * CP * (T_OUT_LO_M - TIN)
    + MDOT_OUT_HI * CP * (T_OUT_HI_M - TIN)
)
ENERGY_RATIO = Q_ENERGY / P_W
DT_WALL = T_WALL - TIN
R_TIM = DT_WALL / P_W

CSS = """
body{font-family:Segoe UI,Microsoft YaHei,sans-serif;max-width:1080px;margin:2rem auto;line-height:1.55;padding:0 1.2rem;color:#1a1a1a}
h1{font-size:1.7rem;line-height:1.3}
h2{margin-top:2rem;border-bottom:1px solid #ddd;padding-bottom:.3rem}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:14px}
th,td{border:1px solid #ccc;padding:.4rem .55rem;text-align:left;vertical-align:top}
th{background:#f4f4f4}
figure{margin:1.2rem 0}
img{max-width:100%;height:auto;background:#fff}
figcaption{font-size:13px;color:#444;margin-top:.45rem}
.note{background:#f7f4ea;border-left:4px solid #b08900;padding:.6rem .8rem;margin:1rem 0}
code{font-family:Consolas,monospace}
"""

CAPTIONS = [
    ("wall_heat_heatflux.png",
     "图 5-1　TIM 底 wall_heat，z=−2.08 mm，总表面热流密度。这是施加的边界，色标挤在 205000 W/m² 附近。画面右侧是高 Y。"),
    ("wall_tim_cu_heatflux.png",
     "图 5-2　TIM–铜界面区 wall_tim_cu 本身的总表面热流密度。负号是面法向约定，量级在 2.05×10⁵ W/m² 附近。这一张显示的是界面区，不是在 z=−2.00 mm 上切的平面。"),
    ("wall_heat_temperature.png",
     "图 5-3　TIM 底温度。四颗堆叠。右侧高 Y。偶数槽从高 Y 进、向低 Y 流；奇数槽从低 Y 进、向高 Y 流。相邻槽流向相反，所以同一端不会整列都是冷端或热端。"),
    ("wall_heat_center_temperature.png",
     "图 5-4　同一底面，第二颗堆叠 Y=13–24 mm。色标是这一小块自己的范围。"),
    ("zm1992_temperature.png",
     "图 5-5　铜侧第一层，z=−1.992 mm，全长。TIM–铜界面在 z=−2.00 mm，这一刀在界面上方 8 μm 的第一层铜里，没有切在界面上。"),
    ("zm1992_center_temperature.png",
     "图 5-6　同一铜层，第二颗堆叠 Y=13–24 mm。"),
    ("zm1000_temperature.png",
     "图 5-7　底铜中面，z=−1 mm。"),
    ("zm008_temperature.png",
     "图 5-8　槽底以下 8 μm，z=−0.008 mm。仍在铜里，没有压在 z=0 的铜–水交界面上。"),
    ("z1000_temperature.png",
     "图 5-9　槽高中面 z=1 mm 的温度。槽沿列向（网格 Y，画面向右为高 Y）。偶数槽在右侧进水，奇数槽在左侧进水。"),
    ("z1000_velocity.png",
     "图 5-10　同一中面的速度。色标是这一张自己的范围，和温度色标不是同一套。"),
    ("z1000_center_temperature.png",
     "图 5-11　槽高中面，第二颗堆叠 Y=13–24 mm，温度。"),
    ("z1000_center_velocity.png",
     "图 5-12　槽高中面，第二颗堆叠，速度。"),
    ("z4000_temperature.png",
     "图 5-13　z=4 mm。加热列上方这一层是铜。两个汇流腔里（低 Y 的 Y=−7–−4 mm，高 Y 的 Y=54–57 mm）是流体。不能把这一刀写成整层都是铜。"),
    ("x550_temperature.png",
     "图 5-14　偶数槽中心 x=5.5 mm 的竖切面，温度。画面右侧是低 Y。这条槽从高 Y 流向低 Y，在低 Y 端向上转入汇流腔。"),
    ("x550_velocity.png",
     "图 5-15　同一偶数槽竖切面的速度。画面右侧是低 Y。"),
    ("x550_velocity_vector.png",
     "图 5-16　同一竖切面的速度矢量，叠在速度云图上。箭头等长，长度不表示快慢；颜色是速度。流动指向画面右侧（低 Y），并在右端沿 Z 向上进入汇流腔。"),
    ("x550_center_temperature.png",
     "图 5-17　x=5.5 mm，第二颗堆叠 Y=13–24 mm，温度。画面右侧仍是这一段里较低的 Y。"),
    ("x550_center_velocity.png",
     "图 5-18　x=5.5 mm，第二颗堆叠，速度。"),
    ("x550_center_velocity_vector.png",
     "图 5-19　x=5.5 mm，第二颗堆叠，速度矢量。箭头等长，指向较低的 Y。"),
    ("x630_temperature.png",
     "图 5-20　肋中心 x=6.3 mm，在第 3、第 4 条槽之间的铜肋里。"),
    ("y185_temperature.png",
     "图 5-21　Y=18.5 mm，第二颗堆叠中部的横断面，温度。七个槽芯，肋从底铜连到槽顶。"),
    ("y185_velocity.png",
     "图 5-22　同一横断面的速度。"),
    ("inlet_hi_temperature.png",
     "图 5-23　偶数槽进口，y=51.5 mm 的水平进口面，温度。四条偶数槽从这里进水。"),
    ("inlet_hi_velocity.png",
     "图 5-24　偶数槽进口速度。面积加权 0.29762 m/s。"),
    ("inlet_lo_temperature.png",
     "图 5-25　奇数槽进口，y=−1.5 mm 的水平进口面，温度。三条奇数槽从这里进水。"),
    ("inlet_lo_velocity.png",
     "图 5-26　奇数槽进口速度。面积加权 0.29762 m/s。"),
    ("outlet_lo_temperature.png",
     "图 5-27　低 Y 汇流腔顶面出口 outlet_lo，z=6 mm。收集四条偶数槽。"),
    ("outlet_lo_velocity.png",
     "图 5-28　outlet_lo 速度。"),
    ("outlet_hi_temperature.png",
     "图 5-29　高 Y 汇流腔顶面出口 outlet_hi，z=6 mm。收集三条奇数槽。"),
    ("outlet_hi_velocity.png",
     "图 5-30　outlet_hi 速度。"),
    ("zm008_heatflux.png",
     "图 5-31　z=−0.008 mm 切面的热流密度。这一刀在槽底以下的铜里。"),
    ("z2004_heatflux.png",
     "图 5-32　槽顶界面上方 z=2.004 mm 的热流密度。界面在 z=2 mm，这一刀没有压在界面上。"),
]


def figure(name, caption):
    raw = (FIG / name).read_bytes()
    img = '<img src="data:image/png;base64,%s" alt="%s">' % (
        base64.b64encode(raw).decode("ascii"), name)
    return "<figure>%s<figcaption>%s</figcaption></figure>" % (img, caption)


def result_html(present):
    parts = []
    parts.append("<h1>HBM 交错流 0.80 mm × 2.00 mm<br>单侧 7 条 · Fluent 结果报告</h1>")
    parts.append(
        "<p><b>文档编号：</b> AIDC-B300-CFD-HBM-CF-W08H20-RES-200<br>"
        "<b>日期：</b> 2026-09-28<br>"
        "<b>场：</b> <code>fluent/hbm_cf_w08h20_i200.cas.h5</code> / <code>.dat.h5</code>，iter 200。"
        "网格 8,112,000 HEXA（流体 1,313,960，铜 6,582,040，TIM 216,000）。"
        "层流，能量，共轭。单精度，<code>3d -t4</code>，无 GPU。"
        "这是交错流场，不是早先同向槽的 iter 200。</p>"
    )
    parts.append(
        '<p class="note">第 200 步连续性残差 5.5151×10⁻⁴，没有降到 10⁻⁴。'
        "x/y/z 速度残差 1.04×10⁻⁷ / 1.15×10⁻⁷ / 2.28×10⁻⁷，能量残差 6.10×10⁻⁸。"
        "收敛检查是关掉的，求解按 200 步停止，不是残差收敛。"
        "下面的温度和压降是这一步的场，不作为已经关闭的设计结论。"
        "用两个出口的质量加权温度算出的带走热量约 %.1f W，施加功率 %.2f W，比值 %.3f，能量没有闭合。</p>"
        % (Q_ENERGY, P_W, ENERGY_RATIO)
    )
    parts.append("<h2>1.　边界与求解</h2>")
    parts.append("""<table>
<tr><th>项</th><th>iter 200</th></tr>
<tr><td>几何</td><td>单侧一列，槽沿列向（网格 Y）。槽 0.80 mm × 2.00 mm，肋 0.80 mm，7 条。偶数槽（4 条）在 y=51.5 mm 水平进入，向低 Y 流，在低 Y 端沿 Z 转入汇流腔，腔顶 z=6 mm 为 outlet_lo。奇数槽（3 条）在 y=−1.5 mm 水平进入，向高 Y 流，在高 Y 端沿 Z 转入汇流腔，腔顶为 outlet_hi。槽的流向端在域边界上封死。相邻进口槽在 z=2–3 mm 是铜，不和汇流腔短路。</td></tr>
<tr><td>网格</td><td><code>mesh/hbm_cf_w08h20.msh</code>。8,112,000 HEXA，节点 8,370,474。x 向比 1.1779，y 向比 1.2000，z 向在槽底是 16 μm 铜贴 8 μm 流体。由 <code>mesh/build_hbm_counterflow_hex.py</code> 分块写出，不是在 ICEM 界面里手工切的。</td></tr>
<tr><td>热流</td><td><code>wall_heat</code> 205000 W/m²。面积 0.000484 m²，四颗 11 mm × 11 mm。功率 %.2f W。堆叠间隙和绝热边界是 <code>wall_adiabat</code>。</td></tr>
<tr><td>流量</td><td>偶数进口 inlet_hi %.6e kg/s，奇数进口 inlet_lo %.6e kg/s，合计仍是 0.20 L/min。出口流出 outlet_lo %.6e kg/s（四条偶数槽），outlet_hi %.6e kg/s（三条奇数槽）。净差 %.3e kg/s。</td></tr>
<tr><td>进口 / 出口</td><td>进口 313.15 K。出口表压 0。进口面积加权静压：奇数 %.2f Pa，偶数 %.2f Pa，两进口合计 %.2f Pa。</td></tr>
<tr><td>材料</td><td>水 ρ=992.2 kg/m³，cp=4179 J/(kg·K)，k=0.631 W/(m·K)，μ=6.53×10⁻⁴ Pa·s。铜 k=390。TIM k=8.818342。</td></tr>
<tr><td>残差</td><td>200 步：连续性 5.5151×10⁻⁴，x/y/z 速度 1.036×10⁻⁷ / 1.151×10⁻⁷ / 2.280×10⁻⁷，能量 6.105×10⁻⁸。连续性未到 10⁻⁴。</td></tr>
</table>""" % (P_W, MDOT_HI, MDOT_LO, MDOT_OUT_LO, MDOT_OUT_HI, MDOT_NET, P_LO, P_HI, P_NET))

    parts.append("<h2>2.　温度</h2>")
    parts.append(
        "<p>TIM 底 <code>wall_heat</code> 面积加权 <b>%.5f K</b>，相对进口升高 %.3f K。"
        "面值 %.5f–%.5f K。铜–水界面面积加权 %.5f K。"
        "出口质量加权：低 Y 腔 %.5f K（四条偶数槽），高 Y 腔 %.5f K（三条奇数槽），"
        "两边合成 %.5f K，相对进口只升高 %.3f K。"
        "出口面积加权合成 %.5f K。</p>"
        % (T_WALL, DT_WALL, T_MIN, T_MAX, T_CU,
           T_OUT_LO_M, T_OUT_HI_M, T_OUT_M, T_OUT_M - TIN, T_OUT_A)
    )
    parts.append("""<table>
<tr><th>面</th><th>iter 200</th></tr>
<tr><td>TIM 底 wall_heat</td><td>面积加权 %.5f K；面值 %.5f–%.5f K</td></tr>
<tr><td>铜侧第一层切面 z=−1.992 mm</td><td>界面在 z=−2.00 mm。这一刀在第一层铜单元内部，离界面 8 μm</td></tr>
<tr><td>铜–水 wall_cu_fluid</td><td>面积加权 %.5f K</td></tr>
<tr><td>outlet_lo（偶数，4 条）</td><td>质量加权 %.5f K；面积加权 %.5f K；流出 %.6e kg/s</td></tr>
<tr><td>outlet_hi（奇数，3 条）</td><td>质量加权 %.5f K；面积加权 %.5f K；流出 %.6e kg/s</td></tr>
<tr><td>进口速度</td><td>inlet_lo %.8f m/s；inlet_hi %.8f m/s</td></tr>
</table>""" % (
        T_WALL, T_MIN, T_MAX, T_CU,
        T_OUT_LO_M, T_OUT_LO_A, MDOT_OUT_LO,
        T_OUT_HI_M, T_OUT_HI_A, MDOT_OUT_HI,
        V_LO, V_HI))
    for name in ("wall_heat_temperature.png", "wall_heat_center_temperature.png"):
        cap = dict(CAPTIONS)[name]
        if name in present:
            parts.append(figure(name, cap))

    parts.append("<h2>3.　热阻与能量</h2>")
    parts.append(
        "<p>R(T_TIM−T_in) = (%.5f − 313.15) / %.2f = <b>%.5f K/W</b>。"
        "除数是这一侧四颗堆叠的 %.2f W，不是两颗 GPU 的封装功率，不能和 0.03 K/W 的封装目标比。"
        "铜–水界面同样口径是 %.5f K/W。</p>"
        % (T_WALL, P_W, R_TIM, P_W, (T_CU - TIN) / P_W)
    )
    parts.append(
        "<p>两个出口按各自质量加权温度计算，ṁ cp ΔT = %.2f W，施加功率 %.2f W，比值 <b>%.3f</b>。"
        "质量不平衡 %.3e kg/s，很小。能量比值离开 1，和连续性 5.5151×10⁻⁴ 放在一起，不把能量写成已经闭合。"
        "启动过程里两个压力出口都出现过回流；第 200 步没有再测回流面积，不把出口温度解释成已经不受回流影响。</p>"
        % (Q_ENERGY, P_W, ENERGY_RATIO, MDOT_NET)
    )

    parts.append("<h2>4.　速度与压降</h2>")
    parts.append(
        "<p>两条进口的面积加权速度都是 0.29762 m/s。Dh = 1.14286 mm，"
        "Re_Dh = ρ U Dh / μ ≈ 517，小于 2000，层流。"
        "奇数进口静压 %.2f Pa，偶数进口静压 %.2f Pa。"
        "这一页不把进口静压写成一维直槽摩擦已经被证实。交错流的流程里有水平进口、槽内转向和 Z 向汇流，和直槽摩擦不是同一段压降。</p>"
        % (P_LO, P_HI)
    )

    parts.append("<h2>5.　云图（iter 200）</h2>")
    parts.append(
        "<p>每张图一个变量。色标是这一张切面、这一个变量自己的范围。"
        "壁面用面值。切面用节点值、光滑着色。"
        "Z 法向截面把 +Y 放在右侧。没有在 TIM–铜界面 z=−2.00 mm 上切平面；"
        "铜侧用 z=−1.992 mm。热流密度是总表面热流，色标用普通小数，不用科学计数法。"
        "X 法向的速度矢量叠在该面速度云图上，箭头等长，颜色才是快慢。</p>"
    )
    for name, caption in CAPTIONS:
        if name in ("wall_heat_temperature.png", "wall_heat_center_temperature.png"):
            continue
        if name in present:
            parts.append(figure(name, caption))
        else:
            parts.append("<p>缺图 <code>%s</code>。%s</p>" % (name, caption))

    parts.append("<h2>6.　网格</h2>")
    parts.append("""<table>
<tr><th>项</th><th>值</th></tr>
<tr><td>单元</td><td>8,112,000 HEXA。流体 1,313,960，铜 6,582,040，TIM 216,000。节点 8,370,474</td></tr>
<tr><td>范围</td><td>x 0–11 mm；y −7–57 mm；z −2.08–6.00 mm</td></tr>
<tr><td>流体近壁</td><td>槽内首层 8 μm，增长比不超过 1.2</td></tr>
<tr><td>固体</td><td>界面首层 16 μm。TIM 厚 80 μm，均分 6 层。z 向比在槽底为 2.0（16 μm 铜 / 8 μm 流体）</td></tr>
<tr><td>加热</td><td>TIM 只铺在四颗堆叠下：列坐标 0–11、13–24、26–37、39–50 mm</td></tr>
<tr><td>汇流</td><td>偶数槽流体沿 y 伸到低 Y 汇流腔下方，和上升段共用 z=2 mm 的面。奇数槽同样伸到高 Y 汇流腔下方</td></tr>
</table>""")
    parts.append(
        "<p>同向槽的 iter 200 留在原来的结果报告里，不把那一组数写进这一页。</p>"
    )
    return "<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'><title>%s</title><style>%s</style></head><body>%s</body></html>" % (
        "HBM_cf_w08h20_ICEM_Fluent_结果报告_i200", CSS, "".join(parts))


def main():
    present = {path.name for path in FIG.glob("*.png")}
    html = result_html(present)
    OUT.write_text(html, encoding="utf-8")
    print("wrote", OUT.name, "figures", len(present), "bytes", OUT.stat().st_size)
    print("energy_W", round(Q_ENERGY, 3), "ratio", round(ENERGY_RATIO, 4), "R", round(R_TIM, 5))


if __name__ == "__main__":
    main()

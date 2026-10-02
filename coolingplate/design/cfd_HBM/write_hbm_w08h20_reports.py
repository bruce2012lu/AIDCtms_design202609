# -*- coding: utf-8 -*-
"""Write the HBM 2 mm iter-200 result report and the 1D/CFD comparison."""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figs" / "i200"

TIN = 313.15
T_WALL = 333.48854
T_MAX = 336.96255
T_MIN = 325.27155
T_CU = 328.76468
T_OUT_A = 323.75007
T_OUT_M = 320.90033
V_IN = 0.29761836
AREA = 0.000484
MDOT = 0.0033073257
CP = 4179.0
P_W = 205000.0 * AREA
DP = 409.11261
DT_M = T_OUT_M - TIN
DT_A = T_OUT_A - TIN
DT_WALL = T_WALL - TIN
Q_ENERGY = MDOT * CP * DT_M
ENERGY_RATIO = Q_ENERGY / P_W

# 1D, same boundary: 7 x 0.80 mm x 2.00 mm, 0.20 L/min, q''=205000, Lh=44 mm, Lfric=50 mm
V_1D = 0.29761904761904756
RE_1D = 516.8192851413153
NU_1D = 7.202075488457743
H_1D = 3976.445929064731
ETA_1D = 0.9673444642937176
DTCONV = 14.812061165160136
DTF_1D = 7.178750897343861
WALL_1D = 21.990812062504
DP_1D = 60.919391128749986


def img(name):
    raw = (FIG / name).read_bytes()
    return '<img src="data:image/png;base64,%s" alt="%s">' % (
        base64.b64encode(raw).decode("ascii"), name)


def figure(name, caption):
    return "<figure>%s<figcaption>%s</figcaption></figure>" % (img(name), caption)


def rel(cfd, one):
    return (cfd - one) / one


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


def result_html():
    parts = []
    parts.append("<h1>HBM 封闭槽 0.80 mm × 2.00 mm<br>单侧 7 条 · Fluent 结果报告</h1>")
    parts.append("<p><b>文档编号：</b> AIDC-B300-CFD-HBM-W08H20-RES-200<br>"
                 "<b>日期：</b> 2026-09-28<br>"
                 "<b>场：</b> <code>fluent/hbm_w08h20_i200.cas.h5</code> / <code>.dat.h5</code>，iter 200。"
                 "网格 4,677,600 HEXA（流体 1,121,120，铜 3,340,480，TIM 216,000）。"
                 "层流，能量，共轭。单精度，<code>3d -t4</code>，无 GPU。</p>")
    parts.append(
        '<p class="note">第 200 步连续性残差 2.6060×10⁻⁴，没有降到 10⁻⁴。'
        "三个速度残差约 10⁻⁸，能量残差 6.04×10⁻⁸。"
        "收敛检查是关掉的，所以求解按 200 步停止，不是残差收敛。"
        "下面的温度和压降是这一步的场，不作为已经关闭的设计结论。</p>"
    )
    parts.append("<h2>1.　边界与求解</h2>")
    parts.append("""<table>
<tr><th>项</th><th>iter 200</th></tr>
<tr><td>几何</td><td>单侧一列。槽 0.80 mm × 2.00 mm，肋 0.80 mm，7 条，两岸各 0.30 mm，列宽 11 mm，列长 50 mm。两端各延长 10 Dh = 11.429 mm。槽顶封死，肋从槽底接到上铜板。上铜板 4.0 mm，底铜 2.0 mm，TIM 0.080 mm。外顶面 z = 6.0 mm。加热段没有通长水缝，两端的分流腔、汇流腔没有画进这套网格。</td></tr>
<tr><td>网格</td><td><code>mesh/hbm_w08h20.msh</code>。4,677,600 HEXA。流体壁面首层 8 μm、增长不超过 1.2；铜界面首层 16 μm。TIM 6 层。</td></tr>
<tr><td>热流</td><td><code>wall_heat</code> 205000 W/m²。面积 0.000484 m²，等于四颗 11 mm × 11 mm。功率 99.22 W。堆叠之间的 2 mm 间隙和两端延长段是 <code>wall_adiabat</code>。</td></tr>
<tr><td>流量</td><td>进口质量流 3.3073257×10⁻³ kg/s（0.20 L/min，40 °C 水）。出口 −3.3073257×10⁻³ kg/s。净差 1.13×10⁻¹¹ kg/s。</td></tr>
<tr><td>进口 / 出口</td><td>进口 313.15 K，均匀质量流。出口表压 0。进口面积加权静压 409.11 Pa。</td></tr>
<tr><td>材料</td><td>水 ρ=992.2 kg/m³，cp=4179 J/(kg·K)，k=0.631 W/(m·K)，μ=6.53×10⁻⁴ Pa·s。铜 k=390。TIM k=8.818342。</td></tr>
<tr><td>残差</td><td>200 步：连续性 2.6060×10⁻⁴，x/y/z 速度 7.34×10⁻⁸ / 1.10×10⁻⁸ / 4.54×10⁻⁸，能量 6.04×10⁻⁸。连续性未到 10⁻⁴。</td></tr>
</table>""")

    parts.append("<h2>2.　温度</h2>")
    parts.append(
        "<p>TIM 底 <code>wall_heat</code> 面积加权 <b>333.48854 K</b>（60.34 °C），"
        "相对进口升高 20.34 K。面值 %s–%s K。"
        "铜–水界面面积加权 328.76 K。出口质量加权 320.90 K，面积加权 323.75 K。</p>"
        % (("%.5f" % T_MIN), ("%.5f" % T_MAX))
    )
    parts.append("""<table>
<tr><th>面</th><th>iter 200</th></tr>
<tr><td>TIM 底 wall_heat</td><td>面积加权 333.48854 K；面值 325.27155–336.96255 K</td></tr>
<tr><td>铜侧第一层切面 z=−1.992 mm</td><td>界面在 z=−2.00 mm。这一刀在第一层铜单元内部，离界面 8 μm。云图色标约 318.54–335.09 K</td></tr>
<tr><td>铜–水 wall_cu_fluid</td><td>面积加权 328.76468 K</td></tr>
<tr><td>出口</td><td>面积加权 323.75007 K；质量加权 320.90033 K</td></tr>
<tr><td>进口速度</td><td>面积加权 0.29761836 m/s</td></tr>
</table>""")
    parts.append(figure(
        "wall_heat_temperature.png",
        "图 2-1　TIM 底面 wall_heat，四颗堆叠。色标是该面面值 325.27–336.96 K。"
        "画面右侧是高 Y、进口端，温度低；左侧是低 Y、出口端，温度高。"
        "四块之间的空白是未加热间隙，槽本身是通的。"))
    parts.append(figure(
        "wall_heat_center_temperature.png",
        "图 2-2　同一底面，第二颗堆叠 Y=13–24 mm。色标仍是这一小块自己的面值。"))

    parts.append("<h2>3.　热阻</h2>")
    r_tim = DT_WALL / P_W
    r_cu = (T_CU - TIN) / P_W
    parts.append(
        "<p>R(T_TIM−T_in) = (333.48854 − 313.15) / 99.22 = <b>%.5f K/W</b>。"
        "除数是这一侧四颗堆叠的 99.22 W，不是两颗 GPU 的封装功率，不能和 0.03 K/W 的封装目标比。"
        "铜–水界面同样口径是 %.5f K/W。CFD 的 TIM 底已经含 TIM、铜和对流。"
        "q''/(T_TIM−T_in) = %.3e W/(m²·K)，这是足迹平均，不是湿面局部对流系数。</p>"
        % (r_tim, r_cu, 205000.0 / DT_WALL)
    )
    parts.append(
        "<p>质量加权能量：ṁ cp ΔT = %.3f W，施加功率 99.22 W，比值 <b>%.4f</b>。"
        "面积加权出口温升 %.3f K，比质量加权 %.3f K 高，慢速热区占的面积大。"
        "能量看质量加权。比值偏离 1，和连续性还没有到 10⁻⁴ 放在一起看，不把能量写成已经闭合。</p>"
        % (Q_ENERGY, ENERGY_RATIO, DT_A, DT_M)
    )

    parts.append("<h2>4.　速度与 Re</h2>")
    parts.append(
        "<p>进口面积加权速度 0.297618 m/s。Dh = 1.14286 mm，Re_Dh = ρ U Dh / μ = %.1f。"
        "小于 2000，层流。槽中切面速度色标上沿约 0.57 m/s，是截面里的最大值，不是进口平均速度。"
        "0.80 m/s 的速度上限没有被这个平均速度碰到。一维全发展摩擦只算 50 mm 直槽，约 61 Pa；"
        "CFD 进口静压 409 Pa，多出来的是两端延长段、入口发展和肋前的流动。这页不把 409 Pa 写成一维摩擦已经被证实。</p>"
        % RE_1D
    )

    parts.append("<h2>5.　云图（iter 200）</h2>")
    parts.append("<p>每张图一个变量。色标是这一张切面、这一个变量自己的范围，没有锁定 313–337 K。"
                 "壁面用面值。切面用节点值、光滑着色。图题是 Fluent 画在画面上的。"
                 "Z 法向截面把 +Y 放在右侧。没有切在 TIM–铜界面 z=−2.00 mm 上。"
                 "铜侧用的是 z=−1.992 mm，在界面上方 8 μm 的第一层铜里。"
                 "X 法向的速度矢量叠在该面速度云图上，箭头等长，颜色才是快慢。</p>")
    captions = [
        ("zm1992_temperature.png",
         "铜侧第一层，z=−1.992 mm，全长。界面在 z=−2.00 mm，这一刀在界面上方 8 μm。色标约 318.54–335.09 K，和 TIM 底面的 325.27–336.96 K 不是同一段。"),
        ("zm1992_center_temperature.png",
         "同一铜层，第二颗堆叠 Y=13–24 mm。"),
        ("zm1000_temperature.png",
         "底铜中面，z=−1 mm。"),
        ("zm008_temperature.png",
         "铜–水槽底以下 8 μm，z=−0.008 mm。仍在铜里，没有压在 z=0 的交界面上。"),
        ("z1000_temperature.png",
         "槽高中面，z=1 mm，温度。七条槽沿 Y 贯穿。右侧高 Y 是进口，水温接近 313.15 K；左侧出口端槽内水温升高。肋是两侧的热色条。"),
        ("z1000_velocity.png",
         "同一中面的速度。色标约 0–0.567 m/s，和上一张温度色标不是同一套。速度高的是槽芯。"),
        ("z1000_center_temperature.png",
         "槽高中面，第二颗堆叠 Y=13–24 mm，温度。"),
        ("z1000_center_velocity.png",
         "槽高中面，第二颗堆叠，速度。"),
        ("z4000_temperature.png",
         "上铜板中面，z=4 mm。槽顶在 z=2 mm，这里整层是铜，加热段没有开腔。"),
        ("x550_temperature.png",
         "中间槽中心，x=5.5 mm，沿流向的竖切面，温度。中间冷带是 2 mm 高的水，上下是铜。肋把底铜和上铜板接在一起，中间没有 2 mm 水缝。"),
        ("x550_velocity.png",
         "同一竖切面的速度。流动集中在槽高里。"),
        ("x550_velocity_vector.png",
         "同一竖切面的速度矢量，叠在速度云图上。箭头等长，长度不表示快慢；颜色是速度。左边色标是云图，右边是矢量对象自己的范围。箭头指向低 Y，也就是出口。"),
        ("x550_center_temperature.png",
         "x=5.5 mm，第二颗堆叠 Y=13–24 mm，温度。"),
        ("x550_center_velocity.png",
         "x=5.5 mm，第二颗堆叠，速度。"),
        ("x550_center_velocity_vector.png",
         "x=5.5 mm，第二颗堆叠，速度矢量。箭头等长。"),
        ("x630_temperature.png",
         "肋中心，x=6.3 mm。这一刀在肋的固体里，槽顶仍然接到上铜板。"),
        ("y185_temperature.png",
         "Y=18.5 mm，第二颗堆叠中部的横断面，温度。七个蓝色槽芯，肋从底铜连到上铜板。"),
        ("y185_velocity.png",
         "同一横断面的速度。七个槽芯更快，色标上沿约 0.56 m/s。"),
        ("inlet_temperature.png",
         "进口面，Y=61.43 mm，温度。七个槽口都在进口温度附近。"),
        ("inlet_velocity.png",
         "进口面速度。面积加权 0.29762 m/s，七个槽口均匀。图题贴在色标旁。"),
        ("outlet_temperature.png",
         "出口面，Y=−11.43 mm，温度。"),
        ("outlet_velocity.png",
         "出口面速度。"),
    ]
    for name, caption in captions:
        parts.append(figure(name, caption))

    parts.append("<h2>6.　网格</h2>")
    parts.append("""<table>
<tr><th>项</th><th>值</th></tr>
<tr><td>单元</td><td>4,677,600 HEXA。流体 1,121,120，铜 3,340,480，TIM 216,000</td></tr>
<tr><td>范围</td><td>x 0–11 mm；y −11.429–61.429 mm；z −2.08–6.00 mm</td></tr>
<tr><td>流体近壁</td><td>首层 8 μm，增长比不超过 1.2。按槽道剪切，DP-A 的 y+ 约 0.46，DP-B 约 0.50</td></tr>
<tr><td>固体</td><td>界面首层 16 μm。TIM 厚 80 μm，均分 6 层</td></tr>
<tr><td>加热</td><td>TIM 只铺在四颗堆叠下：列坐标 0–11、13–24、26–37、39–50 mm</td></tr>
</table>""")
    parts.append("<p>网格由 <code>mesh/build_hbm_cht_hex.py</code> 按分块边分布写出，不是在 ICEM 界面里手工切的。"
                 "这页的剖面都是 Fluent 自己画的。网格对象在这种切面上不画出网格线，所以第 6 节用单元数和近壁尺寸，不再附一张空的网格对象。</p>")
    parts.append("<p>只收录 iter 200，场 <code>hbm_w08h20_i200</code>。TIM 底 333.48854 K。"
                 "进口静压 409.11 Pa。进口速度 0.297618 m/s。质量加权出口温升 7.750 K，能量比 %.4f。"
                 "连续性残差 2.6060×10⁻⁴，未到 10⁻⁴。</p>" % ENERGY_RATIO)
    return "<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">" \
           "<title>HBM 0.80x2.00 七槽 结果报告 iter 200</title><style>%s</style></head><body>\n%s\n</body></html>" % (
               CSS, "\n".join(parts))


def cmp_html():
    def pct(x):
        return "%+.2f%%" % (100.0 * x)

    vrel = rel(V_IN, V_1D)
    tfrel = rel(DT_M, DTF_1D)
    wrel = rel(DT_WALL, WALL_1D)
    prel = rel(DP, DP_1D)
    parts = []
    parts.append("<h1>HBM 0.80×2.00 mm 七槽 · 一维与 CFD 契合性分析</h1>")
    parts.append("<p><b>文档编号：</b> AIDC-B300-CFD-HBM-W08H20-CMP-001<br>"
                 "<b>日期：</b> 2026-09-28<br>"
                 "<b>性质：</b> 对照记录。CFD 是单侧 7 条封闭槽，iter 200，4,677,600 HEXA。"
                 "连续性残差 2.6060×10⁻⁴，未到 10⁻⁴。温度和压降因此标为限制，不写成已经由 CFD 证明的一维。</p>")
    parts.append("<p>相对差 = (CFD − 1D) / 1D。边界量对得上，标为契合。"
                 "场量定义相近、但残差未到判据，标为限制。路径不同，标为不可比。</p>")
    parts.append("<h2>1. 口径</h2>")
    parts.append("""<table>
<tr><th>项</th><th>一维</th><th>写入 Fluent 的值</th></tr>
<tr><td>槽</td><td>0.80 mm × 2.00 mm，肋 0.80 mm，单侧 7 条。Dh=1.14286 mm</td><td>同一几何。上铜板 4.0 mm，槽顶封死。两端分流腔、汇流腔不在网格里</td></tr>
<tr><td>流量</td><td>单侧 0.20 L/min，ṁ=3.30733×10⁻³ kg/s</td><td>进口 3.3073257×10⁻³ kg/s，出口大小相同</td></tr>
<tr><td>热流</td><td>205000 W/m² × 四颗 11×11 mm = 99.22 W。加热长度取 44 mm</td><td>wall_heat 面积 0.000484 m²，205000 W/m²</td></tr>
<tr><td>进口温度</td><td>313.15 K</td><td>313.15 K</td></tr>
<tr><td>对流</td><td>Hausen 型 Nu=max(4, 1.86 Gz<sup>1/3</sup>)，Gz=Dh/L·Re·Pr，L=44 mm。盖板和槽底都算冷却面，两侧肋用肋效率。壁温升=对流温差+全长流体温升</td><td>共轭场，没有单独的努塞尔数</td></tr>
<tr><td>摩擦</td><td>Shah &amp; London，fRe=16.377，只算 50 mm 全发展直槽</td><td>进口到出口的静压，含 11.4 mm 延长段和入口发展</td></tr>
</table>""")
    parts.append("<p>一维在这个边界上：U=0.29762 m/s，Re=516.8，Nu=7.20，h=3976 W/(m²·K)，肋效率 0.967，"
                 "对流温差 14.81 K，流体温升 7.179 K，出口端壁温升 21.99 K，直槽压降 60.9 Pa。</p>")
    parts.append("<h2>2. 对照</h2>")
    parts.append("""<table>
<tr><th>项目</th><th>1D / 设定</th><th>CFD iter 200</th><th>相对差</th><th>判断</th></tr>
<tr><td>进口温度</td><td>313.15 K</td><td>313.15 K</td><td>0</td><td>契合</td></tr>
<tr><td>单侧 ṁ</td><td>3.30733×10⁻³ kg/s</td><td>进口 3.3073257×10⁻³，出口 −3.3073257×10⁻³，净差 1.13×10⁻¹¹ kg/s</td><td>进口约 0</td><td>契合。质量守恒</td></tr>
<tr><td>热流面积</td><td>0.000484 m²，205000 W/m²</td><td>wall_heat 面积 0.000484 m²</td><td>0</td><td>契合</td></tr>
<tr><td>进口速度</td><td>0.297619 m/s</td><td>面积加权 0.297618 m/s</td><td>%s</td><td>契合</td></tr>
<tr><td>Re_Dh</td><td>516.8</td><td>用进口速度得到同一 Re，516.8</td><td>约 0</td><td>契合。限制：Re&lt;2000，层流，不用 Martin</td></tr>
<tr><td>流体温升</td><td>7.179 K，出口 bulk 320.33 K</td><td>质量加权出口 320.900 K，温升 7.750 K。面积加权出口 323.750 K</td><td>质量加权 %s</td><td>限制。连续性未到 10⁻⁴。ṁ cp ΔT / P = %.4f。面积加权偏高，不拿来闭能量</td></tr>
<tr><td>TIM 底温升</td><td>出口端壁温升 21.99 K（对流温差加全长流体温升）</td><td>面积加权 20.34 K（333.489 K）。面最大 23.81 K，面最小 12.12 K</td><td>%s</td><td>限制。一维是出口端槽壁，CFD 是四块足迹的平均，而且场未残差收敛。最大面值比一维出口端高约 1.8 K</td></tr>
<tr><td>静压</td><td>50 mm 全发展直槽 60.9 Pa</td><td>进口 409.11 Pa，出口 0</td><td>%s</td><td>不可比。CFD 含延长段和入口发展，不是那条 50 mm 摩擦公式</td></tr>
</table>""" % (pct(vrel), pct(tfrel), ENERGY_RATIO, pct(wrel), pct(prel)))
    parts.append("<h2>3. 差从哪里来</h2>")
    parts.append("<p>进口速度和面积、流量对齐，差在 0.001% 以内。这是边界，不是对传热模型的证明。</p>")
    parts.append("<p>质量加权温升比一维高 0.57 K（%s）。ṁ cp ΔT = %.2f W，施加功率 99.22 W，比值 %.4f。"
                 "连续性仍是 2.61×10⁻⁴。在残差降到 10⁻⁴ 之前，不把这 8%% 写成模型偏差。</p>"
                 % (pct(tfrel), Q_ENERGY, ENERGY_RATIO))
    parts.append("<p>TIM 底面积加权温升 20.34 K，比一维出口端壁温升 21.99 K 低 %.2f K。"
                 "一维把整段流体温升都加在对流温差上，对应的是热的那一端；CFD 的面积加权把进口端较冷的堆叠也算进去。"
                 "面最大值 336.96 K，相对进口 23.81 K，比一维出口端高约 1.8 K。TIM 本身 80 μm、k=8.82，"
                 "在 205000 W/m² 下大约还有 1.9 K 的导热温差，一维壁温没有单独扣这一层的算法，两边口径不完全相同。</p>"
                 % (WALL_1D - DT_WALL))
    parts.append("<p>压降 CFD 比 50 mm 全发展摩擦高 %.0f Pa（%s）。"
                 "0.5 ρ U² 大约 44 Pa，两端延长段用同一 f 再加约 28 Pa，仍然到不了 409 Pa。"
                 "多出来的是层流发展段和进口、出口的局部流动。一维没有这些项。这是路径不同，不是把 61 Pa 改写成 409 Pa。</p>"
                 % (DP - DP_1D, pct(prel)))
    parts.append("<h2>4. 不用的数</h2>")
    parts.append("<p>不用 3.5 mm 槽那次 iter 34 的 200 Pa 和 329.15 K，也不用开口 2 mm 水缝、8×0.60 mm 那次 400 步的结果。"
                 "那两次几何已经换掉。DP-B（单侧 0.24 L/min）没有做这次 CFD。两端的分流腔、汇流腔还没有尺寸，也不在这个场里。</p>")
    return "<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">" \
           "<title>HBM 0.80x2.00 1D与CFD契合性</title><style>%s</style></head><body>\n%s\n</body></html>" % (
               CSS, "\n".join(parts))


def main():
    result = ROOT / "HBM_w08h20_ICEM_Fluent_结果报告_i200.html"
    cmp_ = ROOT / "HBM_w08h20_1D_CFD契合性分析报告.html"
    result.write_text(result_html(), encoding="utf-8")
    cmp_.write_text(cmp_html(), encoding="utf-8")
    print(result.name, result.stat().st_size)
    print(cmp_.name, cmp_.stat().st_size)
    print("energy", round(Q_ENERGY, 3), "ratio", round(ENERGY_RATIO, 4))
    print("dTwall", round(DT_WALL, 3), "dTm", round(DT_M, 3))


if __name__ == "__main__":
    main()

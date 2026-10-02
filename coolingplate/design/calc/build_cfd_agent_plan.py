# -*- coding: utf-8 -*-
"""生成 CFD-AI Agent 能力评估与工作计划 HTML。

数值唯一来源：model.py（与 B300 设计报告同一套 GEO / DP-A）。
用法: python build_cfd_agent_plan.py
"""
import os

import model as M
from rhtml import h2, h3, h4, p, lead, note, ul, ol, table, cards, fig, formula

# ------------------------------------------------------------
# 本机探测结果（由作者在 2026-09-20 实测写入；生成器不现场扫盘）
# ------------------------------------------------------------
PROBE = dict(
    date="2026-09-20",
    os="Windows 10/11 22631",
    cpu="Intel Core i9-14900KF",
    cores=24,
    threads=32,
    ram_gb=128,
    python_sys=r"C:\veighna_studio\python.exe",
    python_ver="3.13.8",
    ansys_found=False,
    ansys_paths=[],
    awp_root=None,
    fluent_exe=None,
    icem_exe=None,
    wb_exe=None,
    license=None,
    pyfluent=False,
    ansys_mapdl=False,
    pythonnet=False,
    gmsh=False,
    cadquery=False,
    build123d_cad_venv=True,
    cad_venv=r"coolingplate\cad\.venv",
    step_out=[
        r"cad\out\CP-B300-JM-01_assembly.step",
        r"cad\out\CP-B300-JM-01_JM01-100_base_plate.step",
        r"cad\out\CP-B300-JM-01_JM01-200_nozzle_plate.step",
        r"cad\out\CP-B300-JM-01_JM01-400_seal_frame.step",
    ],
    journal_in_repo=False,
)

A = M.solve("DP-A")
B = M.solve("DP-B")
G = M.GEO
FL = M.WATER40

DOC_NO = "AIDC-B300-CFD-AI-001"
VER = "v1.0"
DATE = "2026-09-20"
MODEL = "CP-B300-JM-01"

# 单元胞派生量（与 §9 同一流量拆分）
M_JET = M.mass_flow(FL, A["Qg"]) / M.N_JET          # kg/s
Q_JET_LPM = A["Qg"] / M.N_JET                       # L/min
Q_JET_M3S = Q_JET_LPM / 60000.0
RE_CAL = 3000.0
V_CAL = RE_CAL * FL.mu / (FL.rho * G["D_jet"] * 1e-3)
Q_CAL_M3S = V_CAL * M.A_JET_1
Q_CAL_LPM = Q_CAL_M3S * 60000.0
M_CAL = FL.rho * Q_CAL_M3S
Q_GPU_CAL = Q_CAL_LPM * M.N_JET                     # 等价整板 GPU 流量

OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    f"CFD-AI_Agent_能力评估与工作计划_{VER}_20260920.html")

CSS = """
:root{
  --navy:#0b2748;--blue:#1769e0;--teal:#008b7a;--ink:#182536;
  --muted:#5d6b80;--line:#d7e0ec;--bg:#eef3f8;--soft:#f7fafd;
  --warn:#a65b00;--red:#b42318;--good:#1f7a4d;--cu:#b97a45;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:70px}
body{margin:0;background:var(--bg);color:var(--ink);
  font:14.5px/1.72 "Microsoft YaHei","PingFang SC","Segoe UI",Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
.page{max-width:1240px;margin:auto;background:#fff;
  box-shadow:0 8px 34px #102a4c1f}

header{padding:52px 62px 36px;background:linear-gradient(145deg,#0b2748,#123a68);
  color:#fff}
header .kicker{font-size:12px;letter-spacing:.16em;color:#93b2d6;
  text-transform:uppercase}
header h1{font-size:31px;line-height:1.28;margin:12px 0 12px;font-weight:700}
header .sub{font-size:15.5px;color:#d7e6f5;max-width:960px;line-height:1.75}
.meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:22px}
.pill{border:1px solid #ffffff4d;border-radius:14px;padding:4px 11px;
  font-size:12px;background:#ffffff12}
.pill.hot{background:#b4231833;border-color:#ff9f9a80;color:#ffd9d6}
.pill.ok2{background:#008b7a33;border-color:#7fd8cb80;color:#d3f5ef}
.pill.warn{background:#a65b0033;border-color:#f0c36e80;color:#ffe7b8}
.docbar{display:grid;grid-template-columns:repeat(4,1fr);gap:0;
  margin-top:26px;border-top:1px solid #ffffff2e;padding-top:16px}
.docbar div{font-size:12px;color:#9db6d4}
.docbar div b{display:block;font-size:14px;color:#fff;margin-top:3px;
  font-weight:600}

nav{padding:11px 62px;background:var(--soft);border-bottom:1px solid var(--line);
  position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;gap:2px 4px}
nav a{color:#17518f;text-decoration:none;font-size:12.5px;padding:3px 8px;
  border-radius:5px;white-space:nowrap}
nav a:hover{background:#e3edf9;color:var(--blue)}

main{padding:26px 62px 60px}
section{margin-bottom:8px}

h2{font-size:23px;color:var(--navy);border-bottom:2.5px solid var(--navy);
  padding-bottom:8px;margin:44px 0 16px;font-weight:700}
h2:first-of-type{margin-top:12px}
h3{font-size:17.5px;color:#14507f;margin:28px 0 10px;font-weight:600;
  padding-left:11px;border-left:4px solid var(--teal)}
h4{font-size:15px;color:#1b3d66;margin:18px 0 7px;font-weight:600}
p{margin:9px 0}

.lead{border-left:5px solid var(--blue);background:#eff6ff;padding:15px 19px;
  border-radius:8px;margin:14px 0 18px}
.note{border:1px solid #e3ca8d;background:#fffcf2;padding:13px 17px;
  border-radius:8px;margin:14px 0}
.note.risk{border-color:#eab4b0;background:#fff6f5}
.note.ok{border-color:#a8dcca;background:#f2fbf7}
ul.tight,ol.tight{margin:10px 0 14px 1.4em;padding:0}
ul.tight li,ol.tight li{margin:6px 0}
code{background:#eef2f7;padding:1px 5px;border-radius:4px;
  font-family:Consolas,"Courier New",monospace;font-size:12.5px;
  color:#1f3a5f}

.grid{display:grid;gap:11px;margin:16px 0}
.g4{grid-template-columns:repeat(4,1fr)}
.g3{grid-template-columns:repeat(3,1fr)}
.g2{grid-template-columns:repeat(2,1fr)}
.card{border:1px solid var(--line);border-top:4px solid var(--teal);
  border-radius:8px;padding:13px 14px;background:var(--soft);
  font-size:12.5px;color:var(--muted)}
.card b{display:block;font-size:22px;color:var(--navy);line-height:1.2;
  margin-bottom:4px}
.card.blue{border-top-color:var(--blue)}
.card.warn{border-top-color:var(--warn)}
.card.red{border-top-color:var(--red)}
.card.ok{border-top-color:var(--good)}

table{width:100%;border-collapse:collapse;margin:14px 0 20px;font-size:13px}
th,td{border:1px solid var(--line);padding:8px 10px;vertical-align:top;
  text-align:left;line-height:1.6}
th{background:var(--navy);color:#fff;font-weight:600;font-size:12.5px}
tbody tr:nth-child(even) td{background:#fafcfe}
tr.grp td{background:#e8eef6 !important;font-weight:700;color:var(--navy);
  font-size:12.5px;letter-spacing:.04em}
td strong{color:var(--navy)}

.tag{display:inline-block;padding:1px 7px;border-radius:4px;font-size:11px;
  background:#e6f6f2;color:var(--teal);font-weight:700;white-space:nowrap}
.tag.tagw{background:#fff3d6;color:var(--warn)}
.tag.tagr{background:#fde8e6;color:var(--red)}
.tag.tagb{background:#e7f0fb;color:var(--blue)}
.good{color:var(--good);font-weight:700}
.bad{color:var(--red);font-weight:700}
.warn2{color:var(--warn);font-weight:700}

.formula{background:#f7fafd;border:1px solid var(--line);border-left:4px solid
  var(--blue);border-radius:7px;padding:12px 16px;margin:13px 0}
.formula code{background:none;padding:0;font-size:14px;color:#123a68;
  font-weight:600;display:block;line-height:1.85}
.formula .fres{display:block;margin-top:7px;color:var(--teal);
  font-weight:700;font-size:14px}
.formula .fnote{display:block;margin-top:6px;color:var(--muted);
  font-size:12.5px;line-height:1.65}

figure{margin:18px 0 22px;border:1px solid var(--line);border-radius:10px;
  padding:14px 16px 10px;background:#fff}
figure.svgbox{background:#fcfdff}
svg.svgfig{display:block;width:100%;height:auto;margin:14px 0 0}
figure svg.svgfig{margin:0}
figcaption{margin-top:10px;font-size:12.5px;color:var(--muted);
  line-height:1.65}
figcaption strong{color:var(--navy)}
figcaption .cap{display:block;margin-top:3px}

footer{padding:24px 62px;background:var(--navy);color:#c9d8e8;font-size:12.5px;
  line-height:1.8}
footer b{color:#fff}

@media(max-width:1000px){
  header,nav,main,footer{padding-left:24px;padding-right:24px}
  .g4,.g3,.g2{grid-template-columns:1fr}
  .docbar{grid-template-columns:1fr 1fr}
  table{font-size:12px}
}
@media print{
  body{background:#fff;font-size:10.5pt}
  .page{box-shadow:none;max-width:none}
  nav{display:none}
  header{padding:24px 0}
  main{padding:0}
  h2{page-break-after:avoid;margin-top:22px}
  h3,h4{page-break-after:avoid}
  table,figure,.card,.note,.lead,.formula{page-break-inside:avoid}
  tr{page-break-inside:avoid}
  @page{size:A4;margin:13mm}
}
"""

NAVITEMS = [
    ("exec", "0 结论"), ("scope", "1 范围"), ("probe", "2 环境探测"),
    ("cap", "3 能力矩阵"), ("modes", "4 交互模式"), ("arch", "5 架构"),
    ("ground", "6 本项目锚点"), ("case0", "7 首案规格"),
    ("plan", "8 分阶段计划"), ("risk", "9 风险与开放项"),
    ("gng", "10 闸门"), ("next", "11 下一步"), ("appx", "附录"),
]


# ============================================================
# SVG
# ============================================================
def svg_arch():
    return """<svg class="svgfig" viewBox="0 0 1100 420" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-label="CFD-AI Agent 交互架构">
  <rect x="8" y="8" width="1084" height="404" rx="8" fill="#f7fafd" stroke="#d7e0ec"/>
  <text x="28" y="36" font-size="14" font-weight="700" fill="#0b2748"
        font-family="Microsoft YaHei,sans-serif">图 5-1　CFD-AI Agent 与 ICEM / Fluent 的合法交互面</text>
  <text x="28" y="56" font-size="11" fill="#5d6b80"
        font-family="Microsoft YaHei,sans-serif">原则：Agent 读写文件与脚本，不假装能点 ICEM 交互式 blocking。</text>

  <rect x="28" y="78" width="200" height="118" rx="7" fill="#0b2748"/>
  <text x="128" y="112" text-anchor="middle" fill="#fff" font-size="13" font-weight="700"
        font-family="Microsoft YaHei,sans-serif">大模型 Agent</text>
  <text x="128" y="136" text-anchor="middle" fill="#d7e6f5" font-size="11"
        font-family="Microsoft YaHei,sans-serif">写脚本 · 读日志</text>
  <text x="128" y="156" text-anchor="middle" fill="#93b2d6" font-size="10.5"
        font-family="Microsoft YaHei,sans-serif">不持有许可证</text>
  <text x="128" y="176" text-anchor="middle" fill="#93b2d6" font-size="10.5"
        font-family="Microsoft YaHei,sans-serif">不替代网格工程师</text>

  <rect x="268" y="78" width="210" height="52" rx="6" fill="#eff6ff" stroke="#1769e0"/>
  <text x="373" y="100" text-anchor="middle" fill="#14507f" font-size="12" font-weight="700"
        font-family="Microsoft YaHei,sans-serif">Python / build123d</text>
  <text x="373" y="118" text-anchor="middle" fill="#5d6b80" font-size="10.5"
        font-family="Microsoft YaHei,sans-serif">单元胞 STEP · 1D 复算</text>

  <rect x="268" y="144" width="210" height="52" rx="6" fill="#f2fbf7" stroke="#008b7a"/>
  <text x="373" y="166" text-anchor="middle" fill="#1f7a4d" font-size="12" font-weight="700"
        font-family="Microsoft YaHei,sans-serif">文本脚本作者</text>
  <text x="373" y="184" text-anchor="middle" fill="#5d6b80" font-size="10.5"
        font-family="Microsoft YaHei,sans-serif">journal / TUI / replay / pyfluent</text>

  <path d="M228 120 H268" stroke="#1769e0" stroke-width="2" fill="none"/>
  <path d="M228 156 H268" stroke="#008b7a" stroke-width="2" fill="none"/>

  <rect x="528" y="70" width="250" height="248" rx="8" fill="#fff" stroke="#d7e0ec"/>
  <text x="653" y="96" text-anchor="middle" fill="#0b2748" font-size="12.5" font-weight="700"
        font-family="Microsoft YaHei,sans-serif">交换文件（本机已有 / 待写）</text>
  <text x="548" y="124" fill="#182536" font-size="11.5" font-family="Consolas,monospace">STEP / IGES</text>
  <text x="700" y="124" fill="#1f7a4d" font-size="11" font-family="Microsoft YaHei,sans-serif">CAD 已出整板</text>
  <text x="548" y="148" fill="#182536" font-size="11.5" font-family="Consolas,monospace">.rpl  ICEM replay</text>
  <text x="700" y="148" fill="#a65b00" font-size="11" font-family="Microsoft YaHei,sans-serif">仓库尚无</text>
  <text x="548" y="172" fill="#182536" font-size="11.5" font-family="Consolas,monospace">.jou  Fluent journal</text>
  <text x="700" y="172" fill="#a65b00" font-size="11" font-family="Microsoft YaHei,sans-serif">仓库尚无</text>
  <text x="548" y="196" fill="#182536" font-size="11.5" font-family="Consolas,monospace">.msh / .cas / .dat</text>
  <text x="700" y="196" fill="#b42318" font-size="11" font-family="Microsoft YaHei,sans-serif">需求解器</text>
  <text x="548" y="220" fill="#182536" font-size="11.5" font-family="Consolas,monospace">pyfluent .py</text>
  <text x="700" y="220" fill="#a65b00" font-size="11" font-family="Microsoft YaHei,sans-serif">可写，未装包</text>
  <text x="548" y="244" fill="#182536" font-size="11.5" font-family="Consolas,monospace">.wbjn Workbench</text>
  <text x="700" y="244" fill="#a65b00" font-size="11" font-family="Microsoft YaHei,sans-serif">仓库尚无</text>
  <text x="548" y="268" fill="#182536" font-size="11.5" font-family="Consolas,monospace">transcript / residual</text>
  <text x="700" y="268" fill="#5d6b80" font-size="11" font-family="Microsoft YaHei,sans-serif">跑完才有</text>
  <text x="548" y="292" fill="#182536" font-size="11.5" font-family="Consolas,monospace">PNG 截图 QA</text>
  <text x="700" y="292" fill="#5d6b80" font-size="11" font-family="Microsoft YaHei,sans-serif">可选</text>

  <rect x="818" y="70" width="254" height="118" rx="8" fill="#fff6f5" stroke="#eab4b0"/>
  <text x="945" y="98" text-anchor="middle" fill="#b42318" font-size="12.5" font-weight="700"
        font-family="Microsoft YaHei,sans-serif">ANSYS 运行时（本机）</text>
  <text x="945" y="122" text-anchor="middle" fill="#b42318" font-size="13" font-weight="700"
        font-family="Microsoft YaHei,sans-serif">未安装</text>
  <text x="945" y="146" text-anchor="middle" fill="#5d6b80" font-size="11"
        font-family="Microsoft YaHei,sans-serif">ICEM / Fluent / WB 均未找到</text>
  <text x="945" y="168" text-anchor="middle" fill="#5d6b80" font-size="11"
        font-family="Microsoft YaHei,sans-serif">无 AWP_ROOT* · 无 license.dat</text>

  <rect x="818" y="204" width="254" height="114" rx="8" fill="#f2fbf7" stroke="#a8dcca"/>
  <text x="945" y="232" text-anchor="middle" fill="#1f7a4d" font-size="12.5" font-weight="700"
        font-family="Microsoft YaHei,sans-serif">本机已具备</text>
  <text x="945" y="256" text-anchor="middle" fill="#182536" font-size="11"
        font-family="Microsoft YaHei,sans-serif">i9-14900KF · 24C/32T · 128 GB</text>
  <text x="945" y="276" text-anchor="middle" fill="#182536" font-size="11"
        font-family="Microsoft YaHei,sans-serif">build123d CAD 链 + 整板 STEP</text>
  <text x="945" y="296" text-anchor="middle" fill="#182536" font-size="11"
        font-family="Microsoft YaHei,sans-serif">1D 模型与设计报告 v2.0</text>

  <path d="M478 104 H528" stroke="#1769e0" stroke-width="2" fill="none"/>
  <path d="M478 170 H528" stroke="#008b7a" stroke-width="2" fill="none"/>
  <path d="M778 194 H818" stroke="#b42318" stroke-width="2" stroke-dasharray="5 4" fill="none"/>

  <text x="28" y="390" fill="#5d6b80" font-size="11.5"
        font-family="Microsoft YaHei,sans-serif">虚线 = 本机断点：脚本可以写，求解器跑不起来。实线 = 今天就能做。</text>
</svg>"""


def svg_coupon():
    d = G["D_jet"]
    h = G["H_jet"]
    s = G["S_jet"]
    ch_h = G["ch_h"]
    base = G["base_cu"]
    # 剖面：左侧几何，右侧网格提示
    return f"""<svg class="svgfig" viewBox="0 0 1100 380" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-label="单元胞首案几何">
  <rect x="8" y="8" width="1084" height="364" rx="8" fill="#fcfdff" stroke="#d7e0ec"/>
  <text x="28" y="34" font-size="14" font-weight="700" fill="#0b2748"
        font-family="Microsoft YaHei,sans-serif">图 7-1　推荐首案 UC-01：单孔周期单元胞（不是 95×75 mm 整板）</text>

  <!-- 流体域 -->
  <rect x="80" y="70" width="420" height="48" rx="2" fill="#e7f0fb" stroke="#1769e0"/>
  <text x="290" y="100" text-anchor="middle" fill="#14507f" font-size="12"
        font-family="Microsoft YaHei,sans-serif">短静压箱（盖板侧）　入口质量流 ṁ₁</text>

  <rect x="258" y="118" width="64" height="36" fill="#90cdf4" stroke="#1769e0"/>
  <text x="290" y="141" text-anchor="middle" fill="#0b2748" font-size="11"
        font-family="Microsoft YaHei,sans-serif">⌀{d:.2f}</text>

  <rect x="80" y="154" width="420" height="70" fill="#bee3f8" stroke="#1769e0"/>
  <text x="290" y="184" text-anchor="middle" fill="#14507f" font-size="12"
        font-family="Microsoft YaHei,sans-serif">射流间隙 H = {h:.1f} mm　　H/D = {M.HD:.1f}</text>
  <text x="290" y="206" text-anchor="middle" fill="#5d6b80" font-size="11"
        font-family="Microsoft YaHei,sans-serif">周期边界 @ ±S/2　　S = {s:.1f} mm　　S/D = {M.SD:.1f}</text>

  <rect x="80" y="224" width="420" height="44" fill="#c6f6d5" stroke="#008b7a"/>
  <text x="290" y="251" text-anchor="middle" fill="#1f7a4d" font-size="12"
        font-family="Microsoft YaHei,sans-serif">短槽 {G['ch_w']:.2f}×{ch_h:.2f} mm（UC-02 共轭才建；UC-01 可先等温壁）</text>

  <rect x="80" y="268" width="420" height="36" fill="#d9a06b" stroke="#b97a45"/>
  <text x="290" y="291" text-anchor="middle" fill="#0b2748" font-size="12"
        font-family="Microsoft YaHei,sans-serif">余铜 t = {base:.1f} mm　k = {M.K_CU:.0f} W·m⁻¹K⁻¹</text>

  <!-- 尺寸箭头 -->
  <line x1="80" y1="320" x2="500" y2="320" stroke="#0b2748" stroke-width="1.2"/>
  <text x="290" y="348" text-anchor="middle" fill="#0b2748" font-size="12"
        font-family="Microsoft YaHei,sans-serif">单元胞平面 S × S = {s:.1f} × {s:.1f} mm</text>

  <!-- 右侧规格 -->
  <rect x="540" y="70" width="530" height="270" rx="7" fill="#f7fafd" stroke="#d7e0ec"/>
  <text x="560" y="98" fill="#0b2748" font-size="13" font-weight="700"
        font-family="Microsoft YaHei,sans-serif">冻结自 model.py GEO / DP-A</text>
  <text x="560" y="128" fill="#182536" font-size="12.5" font-family="Microsoft YaHei,sans-serif">工质　DI 水 40 °C　ρ={FL.rho:.1f}　μ={FL.mu:.2e}　k={FL.k:.3f}　Pr={FL.Pr:.2f}</text>
  <text x="560" y="154" fill="#182536" font-size="12.5" font-family="Microsoft YaHei,sans-serif">单孔流量　{Q_JET_LPM:.4f} L/min　= 整板 GPU {A['Qg']:.1f} L/min ÷ {M.N_JET} 孔</text>
  <text x="560" y="180" fill="#182536" font-size="12.5" font-family="Microsoft YaHei,sans-serif">ṁ₁ = {M_JET:.4e} kg/s　　Vⱼ = {A['jet']['V']:.3f} m/s　　Re_D = {A['jet']['Re']:.0f}</text>
  <text x="560" y="206" fill="#182536" font-size="12.5" font-family="Microsoft YaHei,sans-serif">相对喷嘴面积 f = {M.F_AREA:.4f}　（Martin 有效域 0.004–0.04，落在窗内）</text>
  <text x="560" y="232" fill="#b42318" font-size="12.5" font-weight="700"
        font-family="Microsoft YaHei,sans-serif">Re_D 低于 Martin 下限 2000　→ 设计点是外推，不是校验点</text>
  <text x="560" y="258" fill="#182536" font-size="12.5" font-family="Microsoft YaHei,sans-serif">V4 锚定案　Re≈{RE_CAL:.0f}　V={V_CAL:.2f} m/s　等价 GPU 流量 {Q_GPU_CAL:.2f} L/min</text>
  <text x="560" y="284" fill="#182536" font-size="12.5" font-family="Microsoft YaHei,sans-serif">驻点首层 ≤ 3 μm，y⁺ &lt; 1　网格量级 0.8–2.5 M（本机 24 核可跑）</text>
  <text x="560" y="310" fill="#14507f" font-size="12.5" font-family="Microsoft YaHei,sans-serif">禁止：用本单元胞结果直接外推整板 R_θ,c-in（设计报告 §10.3）</text>
</svg>"""


def svg_phases():
    boxes = [
        (40, "0", "环境", "#b42318", "本机红灯"),
        (210, "1", "单元胞几何", "#1769e0", "STEP + 脚本"),
        (380, "2", "网格 QA", "#1769e0", "y⁺ / 正交"),
        (550, "3", "Fluent 求解", "#008b7a", "层流+SST"),
        (720, "4", "对比 1D", "#008b7a", "h / ΔP"),
        (890, "5", "扩阵", "#a65b00", "8×8 后置"),
    ]
    parts = [
        '<svg class="svgfig" viewBox="0 0 1100 200" xmlns="http://www.w3.org/2000/svg"',
        ' role="img" aria-label="分阶段闸门">',
        '<rect x="8" y="8" width="1084" height="184" rx="8" fill="#f7fafd" stroke="#d7e0ec"/>',
        '<text x="28" y="34" font-size="14" font-weight="700" fill="#0b2748"',
        ' font-family="Microsoft YaHei,sans-serif">图 8-1　六阶段闸门：前一阶段不关闭，后一阶段不得开工</text>',
    ]
    for i, (x, n, t, col, sub) in enumerate(boxes):
        parts.append(
            f'<rect x="{x}" y="58" width="150" height="86" rx="8" fill="#fff" stroke="{col}" stroke-width="2"/>')
        parts.append(
            f'<circle cx="{x+28}" cy="86" r="14" fill="{col}"/>')
        parts.append(
            f'<text x="{x+28}" y="91" text-anchor="middle" fill="#fff" font-size="13" font-weight="700"'
            f' font-family="Arial,sans-serif">{n}</text>')
        parts.append(
            f'<text x="{x+52}" y="84" fill="#0b2748" font-size="13" font-weight="700"'
            f' font-family="Microsoft YaHei,sans-serif">{t}</text>')
        parts.append(
            f'<text x="{x+52}" y="108" fill="#5d6b80" font-size="11"'
            f' font-family="Microsoft YaHei,sans-serif">{sub}</text>')
        if i < len(boxes) - 1:
            parts.append(
                f'<path d="M{x+150} 101 H{boxes[i+1][0]}" stroke="#d7e0ec" stroke-width="2"/>')
    parts.append(
        '<text x="28" y="174" fill="#5d6b80" font-size="11.5" font-family="Microsoft YaHei,sans-serif">'
        "阶段 0 在本机为 NO-GO（无 ANSYS）。阶段 1 的 STEP/脚本仍可先行，但不能假装已经在算 CFD。"
        "</text></svg>")
    return "".join(parts)


# ============================================================
# 章节
# ============================================================
def ch0():
    s = ['<section id="exec">']
    s.append(h2("0.", "结论（先读这一页）", "exec"))
    s.append(lead(
        "对「大模型能不能交互 ANSYS ICEM / Fluent」的诚实答案是："
        "<strong>能写脚本、能读文件、不能点 GUI、本机现在也跑不了求解器</strong>。"
        "本机探测未找到 Fluent / ICEM / Workbench / AWP_ROOT* / 许可证；"
        "仓库里也没有现成 journal、replay 或 pyfluent 脚本。"
        "Agent 今天就能做的是：用已有 <code>build123d</code> 链生成"
        f"<strong>单孔单元胞</strong>（D={G['D_jet']:.2f}、H={G['H_jet']:.1f}、"
        f"S={G['S_jet']:.1f} mm），并起草 ICEM replay / Fluent journal / pyfluent。"
        "装上带许可证的 ANSYS 之后，才能批处理网格与求解。"
        f"<strong>不要</strong>把 95×75 mm、{M.N_JET} 孔共轭全模"
        "（报告估计 3 000–8 000 万单元）当作第一案。"))
    s.append(cards([
        ("未找到", "本机 ANSYS / ICEM / Fluent / WB", "red"),
        (f"{A['R_lo']:.4f}–{A['R_hi']:.4f}",
         "§9 一维 R<sub>θ,c-in</sub> °C/W（目标 0.028）", "warn"),
        (f"{A['jet']['Re']:.0f}",
         "设计点 Re<sub>D</sub>（Martin 下限 2000）", "red"),
        ("单元胞", "推荐第一案，禁止整板起步", "ok"),
    ]))
    s.append(p(
        "设计报告 v2.0 已把三维仿真写成<strong>需求规格书</strong>（§10），"
        "工具刻意不指定。本文件补的是：在选定 ICEM+Fluent 路线之后，"
        "<strong>这个 Agent 能承担哪一段、必须由人承担哪一段、第一案怎么开</strong>。"))
    s.append(note(
        "<strong>与报告 §10.3 的硬约束对齐：</strong>"
        "「禁止只算 1 个单元胞外推整板」。单元胞只用来"
        "（1）证明网格/模型能复现 Martin（V4，Re≈3000）；"
        f"（2）给出设计点 Re<sub>D</sub>={A['jet']['Re']:.0f} 的"
        "局部 h 与孔口 ΔP 包络。"
        "整板流量一致性、歧管压降、两 die 温差仍是后续阶段的问题。",
        "risk"))
    s.append("</section>")
    return "".join(s)


def ch1():
    s = ['<section id="scope">']
    s.append(h2("1.", "范围、读者与非目标", "scope"))
    s.append(h3("1.1　本文回答什么"))
    s.append(ol([
        "当前大模型（本 Agent）面对 ICEM / Fluent 的真实能力边界；",
        "在本仓库、本机、本冷板项目上，哪些事今天就能做；",
        "装上 ANSYS 之后，自动化能推进到哪一步；",
        "第一案（simple geometry + CFD）的冻结规格与闸门。",
    ]))
    s.append(h3("1.2　本文不回答什么"))
    s.append(ul([
        "不替代设计报告 v2.0 的 §10 需求规格（Q1–Q8、C01–C12、V1–V5 仍然有效）；",
        "不承诺本周交出整板共轭云图；",
        "不评估 Star-CCM+ / FloTHERM / Icepak / OpenFOAM 的选型（工具仍待项目拍板）；",
        "不提供可绕过许可证或破解求解器的任何路径。",
    ]))
    s.append(h3("1.3　项目上下文（只列与 CFD 决策有关的）"))
    s.append(table(
        ["项", "状态", "对 CFD-AI 的含义"],
        [
            ["一维热力",
             f"已闭合。DP-A R = {A['R_lo']:.4f}–{A['R_hi']:.4f} °C/W，"
             f"目标 {A['target']:.3f}",
             "CFD 的对照带已经有了，不是从零猜 h"],
            ["Martin 有效域",
             f"Re<sub>D</sub>={A['jet']['Re']:.0f} &lt; 2000，关联式外推",
             "第一案必须带 Re≈3000 锚定（报告 V4）"],
            ["几何冻结候选",
             f"CP-B300-JM-01，D/H/S = {G['D_jet']:.2f}/{G['H_jet']:.1f}/{G['S_jet']:.1f} mm",
             "单元胞尺寸不得另起一套"],
            ["CAD",
             "build123d 已出整板 STEP（无静压箱/水嘴，报告已声明）",
             "整板 STEP 不能直接当第一案流体域"],
            ["3D CFD",
             "需求已写，工具待定，尚未开算",
             "本计划是开工文件，不是仿真报告"],
            ["TTV",
             "未做",
             "CFD 关闭后仍要试验确认（V5）"],
        ]))
    s.append("</section>")
    return "".join(s)


def ch2():
    s = ['<section id="probe">']
    s.append(h2("2.", "本机与仓库探测（2026-09-20）", "probe"))
    s.append(lead(
        "阶段 0 的结论先行写出：<strong>求解器侧为红灯，几何与一维侧为绿灯</strong>。"
        "下列条目均为本机实测，不是产品宣传页上的「支持 ANSYS」。"))
    s.append(h3("2.1　硬件"))
    s.append(table(
        ["项", "实测"],
        [
            ["CPU", f"{PROBE['cpu']}　{PROBE['cores']} 核 / {PROBE['threads']} 线程"],
            ["内存", f"{PROBE['ram_gb']} GB"],
            ["操作系统", PROBE["os"]],
            ["对单元胞（≤3 M 单元）",
             '<span class="good">够用</span>：稳态层流/SST 可在工作站完成'],
            ["对整板共轭（30–80 M）",
             '<span class="bad">不够当过夜生产机</span>：'
             "即便装上 Fluent，也需要 HPC 或至少多节点分区；"
             "本机最多适合半 die 试探，不适合 C01–C12 矩阵"],
        ]))
    s.append(h3("2.2　ANSYS 安装与许可证"))
    s.append(table(
        ["探测项", "结果"],
        [
            ["典型目录 C:\\Program Files\\ANSYS Inc 等",
             '<span class="bad">不存在</span>'],
            ["环境变量 AWP_ROOT*", '<span class="bad">未设置</span>'],
            ["PATH 中的 fluent / icemcfd / wb / runwb2",
             '<span class="bad">which/Get-Command 均无</span>'],
            ["注册表 Uninstall 中 ANSYS/Fluent/ICEM",
             '<span class="bad">无匹配项</span>'],
            ["license.dat / FlexNet 痕迹（浅扫）",
             '<span class="bad">未发现</span>'],
            ["结论",
             '<strong class="bad">本机不能 checkout ICEM 或 Fluent</strong>。'
             "阶段 3–4 的执行被阻塞，阶段 1 的脚本与几何不受阻。"],
        ]))
    s.append(h3("2.3　Python 与仓库资产"))
    s.append(table(
        ["资产", "位置 / 版本", "可用性"],
        [
            ["系统 Python",
             f"{PROBE['python_sys']}　{PROBE['python_ver']}",
             "numpy / matplotlib 有；无 CAD、无 ANSYS 绑定"],
            ["pyfluent / ansys-fluent-core", "未安装",
             '<span class="tag tagr">缺</span>'],
            ["ansys-mapdl / pythonnet", "未安装",
             '<span class="tag tagr">缺</span>'],
            ["gmsh / cadquery / pyvista（系统环境）", "未安装",
             '<span class="tag tagr">缺</span>'],
            ["build123d + OCP",
             f"仅在 {PROBE['cad_venv']}",
             '<span class="tag">有</span> 整板 STEP 已生成'],
            ["一维模型", "design/calc/model.py",
             '<span class="tag">有</span> 本文件数值同源'],
            ["设计报告 §10",
             "NVIDIA_B300_…v2.0_20260914.html",
             '<span class="tag">有</span> CFD 需求规格书'],
            ["Fluent journal / ICEM replay / Scheme / wbjn",
             "coolingplate 下 0 个",
             '<span class="tag tagw">待写</span>'],
            ["整板 STEP",
             "<br>".join(f"<code>{p}</code>" for p in PROBE["step_out"]),
             "有，但不含静压箱/水嘴，且尺度不适合第一案"],
        ]))
    s.append(note(
        "探测方法：环境变量 <code>AWP_ROOT*</code>、"
        "<code>Get-Command</code>/<code>where</code>、"
        "常见安装根、Uninstall 注册表、浅层 license.dat 搜索、"
        "<code>importlib.util.find_spec</code>。"
        "未做全盘 <code>fluent.exe</code> 穷举（耗时长，且典型安装已被覆盖）。"
        "若 ANSYS 装在非标准盘符的深层目录，阶段 0 复查时应由人提供路径。",
        "ok"))
    s.append("</section>")
    return "".join(s)


def ch3():
    s = ['<section id="cap">']
    s.append(h2("3.", "能力矩阵（非市场话术）", "cap"))
    s.append(p(
        "三列必须分开看。<strong>今天</strong> = 无 ANSYS 二进制；"
        "<strong>若已安装</strong> = 本机或远程有带许可的 ICEM/Fluent；"
        "<strong>做不好</strong> = 即使有求解器，Agent 也不应被当成主责。"))

    s.append(h3("3.1　今天能做（无 ANSYS）"))
    s.append(table(
        ["能力", "成熟度", "本项目上的具体产物", "限度"],
        [
            ["参数化几何（Python/CAD）",
             '<span class="tag">高</span>',
             f"已有整板 build123d；可加写单孔单元胞 STEP"
             f"（S={G['S_jet']:.1f} mm 周期盒）",
             "静压箱/水嘴仍按报告刻意不建"],
            ["一维热力 / 水力复算",
             '<span class="tag">高</span>',
             f"R 区间、Re、V、孔口 ΔP、h 乐观/保守，全部来自 model.py",
             "歧管 3–5 kPa 仍是估值（AS-7）"],
            ["设计/计划类 HTML 报告",
             '<span class="tag">高</span>',
             "本文件与 v2.0 设计报告同一套 CSS/数值源",
             "不是仿真报告"],
            ["Fluent journal / TUI 起草",
             '<span class="tag tagb">中</span>',
             "可写 meshing/solve/report 的文本骨架（附录）",
             "未在本机验证；版本方言要对照安装年版本"],
            ["ICEM replay（.rpl）起草",
             '<span class="tag tagw">中低</span>',
             "简单砖块/O-grid 单元胞可以写草稿",
             "复杂 topology 的 replay 极脆，几乎一定要人先录一条"],
            ["pyfluent 脚本起草",
             '<span class="tag tagb">中</span>',
             "可按官方 API 写 launch / TUI / 后处理草稿",
             "包未装；API 随 Fluent 版本漂移"],
            ["Workbench journal（.wbjn）起草",
             '<span class="tag tagw">中低</span>',
             "可写项目树、参数更新的骨架",
             "WB 宏对版本和组件布局敏感"],
            ["结果文件解析器（预写）",
             '<span class="tag tagb">中</span>',
             "可先写 residual / surface-report / CSV 解析",
             "没有 .out/.dat 就测不了"],
        ]))

    s.append(h3("3.2　若 ANSYS 已安装且许可证可用"))
    s.append(table(
        ["能力", "推荐接口", "Agent 能自动到哪", "仍须人确认"],
        [
            ["ICEM 批处理网格",
             "icemcfd -batch -script xxx.rpl",
             "在 replay 已由人录制/审过的前提下重放、改尺寸参数",
             "阻塞质量、关联面、周期匹配"],
            ["Fluent Meshing 水密",
             "fluent 3d -meshing -tN -i xxx.jou",
             "水密单元胞/短槽 coupon 的表面网格 + poly-hexcore",
             "泄漏面、命名选择、y⁺ 是否达标"],
            ["Fluent 求解",
             "fluent 3d -tN -g -i xxx.jou　或 pyfluent",
             "层流/SST 稳态、残差与监测量、自动存 cas/dat",
             "发散时的 URF/网格局部修复"],
            ["Workbench 项目",
             "runwb2 -B -F proj.wbpj -R journal.wbjn",
             "参数化扫 D/H/S 或流量的批处理外壳",
             "工程树是否指向正确网格/材料"],
            ["后处理提取",
             "TUI report / pyfluent / 写文件",
             "ΔP、面平均 h、T_wall,max、残差曲线、质量不平衡",
             "驻点是否对、交叉流是否被周期边界歪曲"],
            ["截图 QA",
             "Fluent 硬拷贝或外部截屏",
             "残差图、网格切面、壁温图归档",
             "图是否真的回答了 Q1–Q5"],
        ]))

    s.append(h3("3.3　做不好或不应交给 Agent 主责"))
    s.append(table(
        ["事项", "原因", "正确分工"],
        [
            ["在 ICEM GUI 里交互式点选 blocking",
             "需要空间拓扑直觉；坐标点击无法从聊天稳定复现",
             "人录一条黄金 replay，Agent 只改参数重放"],
            ["复杂歧管 / 128 孔的关联与周期",
             "一点错面就全盘作废，日志也不友好",
             "第一案避开；半 die 再上"],
            ["许可证 checkout / 浮动许可排队",
             "Agent 不能创造许可，也不应抢占他人 token",
             "人提供 ANSLIC_ADMIN / 许可服务器"],
            ["千万级网格的质量排雷",
             "负体积、扭曲、周期缝需要目视 + 经验",
             "Agent 报指标，人决定加密/重切"],
            ["整板 30–80 M 共轭过夜无 HPC",
             "本机 24 核/128 GB 不是这量级的生产环境",
             "单元胞闭合后再谈分区与队列"],
            ["把 GUI 当 API 来「看图说话」驱鼠",
             "脆、慢、不可重复，评审无法复现",
             "只把截图当 QA 附件，不以它为控制面"],
            ["替代 TTV / 官方 power map",
             "报告已写：无实测不能关 V5，无热图只能用假设分布",
             "CFD 给区间，试验给真值"],
        ]))
    s.append(note(
        "一句话：<strong>Agent 是脚本与簿记员，不是网格主任工程师，"
        "更不是许可证服务器。</strong>"
        "把第一案做成可批处理的单元胞，能力才会从「能写」变成「能跑」。",
        "ok"))
    s.append("</section>")
    return "".join(s)


def ch4():
    s = ['<section id="modes">']
    s.append(h2("4.", "交互模式与推荐优先级", "modes"))
    s.append(p(
        "与 ICEM/Fluent「交互」只有下列合法面。优先级按"
        "<em>可重复、可评审、对 GUI 依赖低</em>排序。"))
    s.append(table(
        ["优先级", "模式", "载体", "何时用", "本机状态"],
        [
            ["P0", "文件 I/O",
             "STEP / IGES → MSH / CAS / DAT / CSV",
             "永远是主通道。几何、网格、解、报表都走文件。",
             '<span class="tag">STEP 已有整板</span>'],
            ["P1", "Fluent journal + TUI",
             "<code>.jou</code> 文本，<code>-i</code> 批跑",
             "求解与后处理的默认控制面；版本相对稳定。",
             '<span class="tag tagw">可写未跑</span>'],
            ["P1", "pyfluent",
             "Python API 包一层 TUI/Scheme",
             "要和 model.py 同进程对比 1D、做 DOE 时优先。",
             '<span class="tag tagr">包未装</span>'],
            ["P2", "ICEM replay",
             "<code>.rpl</code> + <code>-batch</code>",
             "结构化六面体/O-grid 单元胞。先人后机。",
             '<span class="tag tagr">无 ICEM</span>'],
            ["P2", "Fluent Meshing 水密",
             "meshing-mode journal",
             "不想维护 ICEM blocking 时的替代，适合 coupon。",
             '<span class="tag tagr">无 Fluent</span>'],
            ["P3", "Workbench journal",
             "<code>.wbjn</code> / <code>.wbpj</code>",
             "要把网格-求解-参数表绑成工程时再用，不是第一案必需。",
             '<span class="tag tagr">无 WB</span>'],
            ["P4", "截图 QA",
             "PNG / 硬拷贝",
             "给人看，不给程序当闭环。",
             "可选"],
        ]))
    s.append(h3("4.1　明确不采用的模式"))
    s.append(ul([
        "远程桌面驱鼠操作 ICEM（不可重复，无法进 Git）；",
        "把整板装配 STEP 直接丢进 Fluent Meshing 当第一案"
        "（缺流体腔、缺水嘴、特征尺度差 200 倍）；",
        "未经验证就调用「一键自动 blocking」然后当黄金网格。",
    ]))
    s.append(h3("4.2　推荐控制栈（第一案）"))
    s.append(ol([
        "build123d 生成单元胞 STEP（流体，可选固体）；",
        "Fluent Meshing 水密 journal <strong>或</strong> 人录 ICEM replay；",
        "Fluent 3d journal：层流基线 + SST 包络；",
        "TUI surface report 写出 CSV；",
        "Python 读 CSV，与 model.py 的乐观/保守带比较。",
    ]))
    s.append("</section>")
    return "".join(s)


def ch5():
    s = ['<section id="arch">']
    s.append(h2("5.", "目标架构", "arch"))
    s.append(fig(
        svg_arch(),
        "图 5-1",
        "Agent 只站在文件和脚本这一侧",
        "本机断点在求解器安装与许可证，不在一维模型或 CAD 链。"))
    s.append(h3("5.1　建议的目录（尚未创建，待阶段 1 开工）"))
    s.append(table(
        ["路径", "内容"],
        [
            ["coolingplate/cfd/geom/", "单元胞 STEP / 命名面清单"],
            ["coolingplate/cfd/icem/", "replay、blocking 模板、质量报告"],
            ["coolingplate/cfd/fluent/", "journal、pyfluent、材料、监视定义"],
            ["coolingplate/cfd/cases/UC-01/", "cas/dat、残差、CSV、截图"],
            ["coolingplate/cfd/compare/", "与 model.py 对比表"],
        ]))
    s.append(p(
        "目录现在<strong>不预先建空壳</strong>，避免仓库里出现一批无法运行的伪工程。"
        "阶段 0 绿灯后再建。"))
    s.append("</section>")
    return "".join(s)


def ch6():
    s = ['<section id="ground">']
    s.append(h2("6.", "必须锚在本项目上的数字", "ground"))
    s.append(lead(
        "下面所有数来自 <code>design/calc/model.py</code> 的 "
        f"<code>solve('DP-A')</code>，与设计报告 v2.0 §9 一致。"
        "CFD 计划若另编一套 D/H/S 或流量，视为失败。"))
    s.append(h3("6.1　几何与阵列"))
    s.append(table(
        ["量", "符号", "值", "来源"],
        [
            ["板外形", "L×W×T",
             f"{G['plate_L']:.0f}×{G['plate_W']:.0f}×{G['plate_T']:.1f} mm",
             "GEO"],
            ["喷嘴直径", "D", f"{G['D_jet']:.2f} mm", "GEO"],
            ["喷距", "H", f"{G['H_jet']:.1f} mm", "GEO"],
            ["孔距", "S", f"{G['S_jet']:.1f} mm", "GEO"],
            ["无量纲", "H/D，S/D，f",
             f"{M.HD:.1f}，{M.SD:.1f}，{M.F_AREA:.4f}", "派生"],
            ["孔数", "N",
             f"{G['n_jet_per_die']} / die × {G['n_die']} die = {M.N_JET}",
             "GEO"],
            ["短槽", "w×h，p，L",
             f"{G['ch_w']:.2f}×{G['ch_h']:.2f}，{G['ch_p']:.2f}，"
             f"{G['L_flow']:.1f} mm（上限 {G['L_flow_max']:.0f}）",
             "GEO"],
            ["余铜", "t_base,cu", f"{G['base_cu']:.1f} mm", "GEO"],
        ]))
    s.append(h3("6.2　DP-A 水力 / 热力（单元胞边界条件直接用）"))
    s.append(table(
        ["量", "整板 / GPU 份额", "折到单孔"],
        [
            ["流量",
             f"2.00 L/min 总；GPU {A['Qg']:.2f} L/min（80%）",
             f"{Q_JET_LPM:.4f} L/min"],
            ["质量流",
             f"总 ṁ={M.mass_flow(FL, A['Q']):.5f} kg/s；"
             f"GPU {M.mass_flow(FL, A['Qg']):.5f} kg/s",
             f"{M_JET:.4e} kg/s"],
            ["射流速度 / Re",
             f"V={A['jet']['V']:.3f} m/s　Re<sub>D</sub>={A['jet']['Re']:.1f}",
             "与整板相同（并联均分假设）"],
            ["孔口 ΔP（K=1.8）",
             f"{A['dp']['orifice']/1000:.2f} kPa",
             "单元胞应回收到同一量级"],
            ["短槽 ΔP（cell 拓扑）",
             f"{A['dp']['channel']:.2f} Pa（几乎可忽略）",
             "若 CFD 大一个数量级，先查出口定义"],
            ["歧管估值",
             f"{A['dp']['manifold'][0]/1000:.0f}–"
             f"{A['dp']['manifold'][1]/1000:.0f} kPa（AS-7）",
             "单元胞<strong>答不了</strong>，勿装成答了"],
        ]))
    s.append(h3("6.3　一维对照带（阶段 4 的尺子）"))
    opt, con = A["opt"], A["con"]
    s.append(table(
        ["模型", "含义", "h 或 h_eff", "对流热阻", "R<sub>θ,c-in</sub>"],
        [
            ["乐观（Martin 面平均）",
             f"Nu={opt['Nu']:.2f}，外推={opt['extrapolated']}",
             f"{opt['h']:.0f} W·m⁻²K⁻¹",
             f"{opt['R']:.4f} °C/W",
             f"{A['R_lo']:.4f} °C/W（TIM2=0.004）"],
            ["保守（短槽+驻点核）",
             f"h_ch={con['h_ch']:.0f}，h_stag={con['h_stag']:.0f}",
             f"{con['h_eff']:.0f} W·m⁻²K⁻¹",
             f"{con['R']:.4f} °C/W",
             f"{A['R_hi']:.4f} °C/W（TIM2=0.008）"],
            ["目标", "DP-A 保证点", "—", "—",
             f"{A['target']:.3f} °C/W　区间跨线"],
        ]))
    s.append(formula(
        "R_θ,c-in = R_wall + R_TIM2 + R_conv",
        result=(f"墙 {M.R_WALL:.4f} + TIM2 0.004–0.008 + "
                f"对流 {opt['R']:.4f}–{con['R']:.4f} "
                f"= {A['R_lo']:.4f}–{A['R_hi']:.4f} °C/W"),
        note_="单元胞 CFD 直接可比的是局部 h 与孔口 ΔP，不是整板 R。"))
    s.append(p(
        f"热流密度（均匀假设）：die {A['q_die']:.1f} W/cm²，"
        f"HBM {A['q_hbm']:.1f} W/cm²。"
        "单元胞若做共轭，底面热流用 die 值，不要把 1100 W 摊到 3×3 mm。"))
    q_cell = A["q_die"] * (G["S_jet"] * G["S_jet"] * 1e-2)   # W, q in W/cm2 * cm2
    s.append(formula(
        f"Q_cell = q_die × S² = {A['q_die']:.2f} W/cm² × "
        f"({G['S_jet']:.1f} mm)²",
        result=f"{q_cell:.3f} W / 单元胞",
        note_="仅 UC-02 共轭加载。UC-01 流体等温壁不需要这条。"))
    s.append(h3("6.4　报告已写死、计划不得改口的约束"))
    s.append(ul([
        f"驻点首层 ≤ 3 μm，y⁺ &lt; 1；孔内径向 ≥ 12、轴向 ≥ 8；"
        f"间隙法向 ≥ 20 层（§10.4）；",
        "必须共轭才能谈整板 R；单元胞允许先流体-only 做 V4（§10.3 禁止的是"
        "「只算单元胞就外推整板 R」，不是禁止单元胞本身）；",
        f"转捩 SST 为整板基线，层流对照必做；"
        f"Re<sub>D</sub>={A['jet']['Re']:.0f} 在过渡区（§10.5）；",
        "V4：先跑 Re≈3000 证明能复现 Martin（偏差 &lt; 15%），再回到设计点；",
        "网格无关性：粗/中/细 1 : 1.5 : 2.25，相邻套 R 与 ΔP 差 &lt; 3%。",
    ]))
    s.append("</section>")
    return "".join(s)


def ch7():
    s = ['<section id="case0">']
    s.append(h2("7.", "推荐第一案规格（冻结草案）", "case0"))
    s.append(lead(
        "第一案叫 <strong>UC-01 / UC-02</strong>，不是 C01。"
        "C01 是报告 §10.7 的整板基线，属于阶段 5 之后。"
        "若有人要求「先把整板丢进 ICEM」，按本文件拒收。"))
    s.append(fig(
        svg_coupon(),
        "图 7-1",
        "单孔周期单元胞",
        "尺寸全部来自 GEO。右侧红字是本项目必须做 V4 的原因。"))

    s.append(h3("7.1　UC-01　流体-only，等温底壁（先做）"))
    s.append(table(
        ["项", "规定"],
        [
            ["目的",
             "打通几何→网格→求解→提取；用 Re≈3000 锚定 Martin（V4）；"
             f"再跑设计点 Re={A['jet']['Re']:.0f} 看外推偏差"],
            ["计算域",
             f"周期盒 {G['S_jet']:.1f}×{G['S_jet']:.1f} mm；"
             f"孔 ⌀{G['D_jet']:.2f}（盖板厚方向至少 8 层）；"
             f"间隙 {G['H_jet']:.1f} mm；孔上短静压箱 ≥ 4D；"
             "底壁可切掉固体"],
            ["边界",
             f"顶面/静压箱：质量入口 ṁ₁={M_JET:.4e} kg/s，T={A['Tin']:.0f} °C；"
             "底壁：等温（建议 50 °C，仅用于定义 h）；"
             "四侧：平移周期；孔口出流经短槽方向开压力出口，"
             "或底面开环缝出口（须在网格说明里写死一种，禁止两种混用）"],
            ["工质",
             f"{FL.name}，先常物性，再温变 μ、k（报告 §10.5）"],
            ["模型",
             "稳态、不可压；<strong>层流必跑</strong>；k-ω SST 低 Re 作包络。"
             "单元胞暂不强制 γ-Reθ（省自由度），整板再上"],
            ["网格",
             "首层 ≤ 3 μm；驻点法向 ≥ 15；孔径向 ≥ 12；"
             "总量目标 0.8–2.5 M；三套无关性"],
            ["出口定义（待人拍板）",
             '<span class="warn2">开放项 O-CFD-01</span>：'
             "纯冲击（无槽）环缝出口 vs 带 0.40 mm 短槽侧出口。"
             "建议 UC-01a 无槽、UC-01b 带槽流体"],
            ["成功判据",
             "残差连续/动量 &lt; 1e-4，能量 &lt; 1e-6；"
             "质量不平衡 &lt; 0.1%；"
             "Re=3000 时面平均 Nu 与 Martin 偏差 &lt; 15%；"
             f"设计点孔口 ΔP 与一维 {A['dp']['orifice']/1000:.2f} kPa 偏差 &lt; 30%"
             "（K 本身是假设）"],
        ]))

    s.append(h3("7.2　UC-02　共轭 coupon（UC-01 关闭后）"))
    s.append(table(
        ["项", "规定"],
        [
            ["固体",
             f"余铜 {G['base_cu']:.1f} mm + 短槽肋；k={M.K_CU:.0f}；"
             "TIM2 先不建，改为底面热流"],
            ["热源",
             f"q = {A['q_die']:.2f} W/cm² 均布在 S×S 接触面；"
             f"单胞功率 {A['q_die'] * (G['S_jet']**2 * 1e-2):.3f} W"],
            ["可比量",
             f"局部 h、ΔT_wall、孔口 ΔP；"
             f"换算 h_eff 应落在 {A['con']['h_eff']:.0f}–{A['opt']['h']:.0f}"
             " W·m⁻²K⁻¹ 一带。落在带外先查边界，再谈改设计"],
            ["仍不可比",
             "整板 R_θ,c-in、两 die 温差、128 孔流量偏差、歧管压降"],
        ]))

    s.append(h3("7.3　V4 锚定案（与 UC-01 同网格）"))
    s.append(p(
        f"只把 ṁ 放大到 Re<sub>D</sub>={RE_CAL:.0f}："
        f"V={V_CAL:.2f} m/s，ṁ={M_CAL:.4e} kg/s，"
        f"单孔 {Q_CAL_LPM:.4f} L/min，"
        f"等价整板 GPU 流量 {Q_GPU_CAL:.2f} L/min。"
        "这不是运行点，是校验点。Martin 有效域要求 "
        "2000≤Re≤1e5、0.004≤f≤0.04、2≤H/D≤12："
        f"本几何 f={M.F_AREA:.4f}、H/D={M.HD:.1f} 已在窗内，只有 Re 越界。"))

    s.append(h3("7.4　明确不做的第一案"))
    s.append(ul([
        f"95×75 mm 整板、{M.N_JET} 孔、含 HBM 槽与隔离肋；",
        "把喷嘴当多孔介质；",
        "1/4 对称（进出口沿 Y 不对称，报告已禁）；",
        "PG25、热点 2.5×、堵塞 20%（那是 C08–C10）。",
    ]))
    s.append("</section>")
    return "".join(s)


def ch8():
    s = ['<section id="plan">']
    s.append(h2("8.", "分阶段工作计划（带闸门）", "plan"))
    s.append(fig(
        svg_phases(),
        "图 8-1",
        "六阶段",
        "阶段 0 红灯不阻止写脚本，但阻止宣称「已经在做 CFD」。"))

    s.append(h3("阶段 0　环境探测"))
    s.append(table(
        ["动作", "责任", "完成定义"],
        [
            ["确认 ANSYS 版本、组件（ICEM CFD、Fluent、WB）", "人",
             "写出 AWP_ROOT 与版本号，例如 2024 R2"],
            ["确认许可证（HPC 核数、Fluent、Meshing）", "人",
             "能 checkout 的核数 ≥ 16；记下服务器名"],
            ["本机核数/内存（已测）", "Agent 已做",
             f"{PROBE['cores']}C / {PROBE['ram_gb']} GB"],
            ["安装或接入 pyfluent，版本与 Fluent 对齐", "人 + Agent",
             "<code>import ansys.fluent.core</code> 成功"],
            ["决定网格路线：ICEM hex vs Fluent Meshing 水密", "人",
             "写进 O-CFD-02"],
        ]))
    s.append(note(
        f"<strong>本机当前闸门状态：NO-GO。</strong>"
        "未找到安装与许可证。阶段 1 可继续做几何与脚本，"
        "阶段 2–4 不得宣称完成。",
        "risk"))

    s.append(h3("阶段 1　简单几何"))
    s.append(table(
        ["动作", "责任", "完成定义"],
        [
            [f"build123d 写单元胞：D={G['D_jet']:.2f}、H={G['H_jet']:.1f}、"
             f"S={G['S_jet']:.1f} mm，命名 inlet/outlet/wall/periodic",
             "Agent",
             "STEP 可被独立 OCC/CAD 打开；面名称清单入库"],
            ["可选：短槽流体（UC-01b）与共轭固体（UC-02）两套文件",
             "Agent",
             "与 GEO 槽宽/槽深一致，误差 &lt; 0.01 mm"],
            ["起草 Fluent Meshing journal 与/或 ICEM replay 草稿",
             "Agent",
             "文本进 Git；不要求本机跑通"],
            ["人审出口定义（O-CFD-01）",
             "人",
             "书面选定 UC-01a 或 01b"],
        ]))

    s.append(h3("阶段 2　网格 QA"))
    s.append(table(
        ["动作", "完成定义"],
        [
            ["首层厚度 ≤ 3 μm，驻点 y⁺ &lt; 1（用初场速度估一次，求解后再核）",
             "后处理报告里有 y⁺ 云图与最大值"],
            ["最小正交质量 &gt; 0.15（报告 §10.2）；无负体积",
             "ICEM/Fluent 质量表截图 + CSV"],
            ["孔径向 ≥ 12、轴向 ≥ 8、间隙法向 ≥ 20",
             "切面截图可数层"],
            ["粗/中/细三套，尺寸比 1 : 1.5 : 2.25",
             "三套网格量记录在案"],
        ]))

    s.append(h3("阶段 3　Fluent 求解（coupon）"))
    s.append(table(
        ["算例", "Re / 流量", "模型", "目的"],
        [
            ["UC-01-L-3000",
             f"Re={RE_CAL:.0f}，ṁ={M_CAL:.3e} kg/s",
             "层流", "V4 锚定"],
            ["UC-01-S-3000", "同上", "SST 低 Re", "模型包络"],
            ["UC-01-L-806",
             f"Re={A['jet']['Re']:.0f}，ṁ={M_JET:.3e} kg/s",
             "层流", "设计点"],
            ["UC-01-S-806", "同上", "SST 低 Re", "设计点包络"],
            ["UC-02-*", "设计点", "共轭 + 层流/SST", "阶段 3 末可选"],
        ]))
    s.append(p(
        "收敛沿用报告 §10.8：连续性/动量 &lt; 1e-4，能量 &lt; 1e-6；"
        "h 与 ΔP 连续 500 步漂移 &lt; 0.5%；能量守恒 &lt; 1%。"
        "批处理：<code>fluent 3d -t16 -g -i uc01.jou</code> 或等价 pyfluent。"))

    s.append(h3("阶段 4　提取并与一维比较"))
    s.append(table(
        ["提取量", "和谁比", "通过"],
        [
            ["面平均 Nu（等温壁，Re=3000）",
             "Martin 同 f、H/D", "&lt; 15%"],
            [f"面平均 h（Re={A['jet']['Re']:.0f}）",
             f"{A['con']['h_eff']:.0f}–{A['opt']['h']:.0f} W·m⁻²K⁻¹",
             "落在带内或给出超带原因"],
            ["孔口 ΔP",
             f"{A['dp']['orifice']/1000:.2f} kPa（K=1.8）",
             "量级一致；可反标定 K"],
            ["层流 vs SST 的 h 差",
             "报告：&gt;20% 则只给区间", "必须上报，不得只交一个数"],
            ["网格无关性", "相邻套 h、ΔP", "&lt; 3%"],
        ]))

    s.append(h3("阶段 5　放大（仅当阶段 4 关闭）"))
    s.append(ol([
        f"8×8 单 die 阵列（{G['n_jet_per_die']} 孔），仍不要两 die + HBM；",
        "半板（沿 X 中线 1/2，报告允许；禁止 1/4）；",
        "这时才谈静压箱、隔墙、Q2 流量一致性、Q4 歧管压降；",
        "C01–C12 工况矩阵仍按设计报告执行，本计划不改优先级。",
    ]))
    s.append(note(
        "阶段 5 的网格量会从百万级跳到千万级。本机 24 核可以试 8×8，"
        "半板共轭应评估是否需要 HPC。未做评估就开 C01，视为计划失败。",
        "risk"))
    s.append("</section>")
    return "".join(s)


def ch9():
    s = ['<section id="risk">']
    s.append(h2("9.", "风险、开放项、工具待定", "risk"))
    s.append(h3("9.1　本计划自有风险（在设计报告 RK-01/02 之外）"))
    s.append(table(
        ["编号", "风险", "等级", "缓解"],
        [
            ["RK-A1",
             "本机无 ANSYS，计划停在纸面",
             '<span class="bad">红</span>',
             "阶段 0 由人提供安装路径或远程求解器账号"],
            ["RK-A2",
             "ICEM replay 在未录制的复杂拓扑上不可维护",
             '<span class="warn2">橙</span>',
             "第一案用水密 Meshing；ICEM 只用于单元胞砖块"],
            ["RK-A3",
             "单元胞周期边界歪曲交叉流，h 偏高",
             '<span class="warn2">橙</span>',
             "阶段 5 用 8×8 检查边缘孔；不把 UC h 当整板 h"],
            ["RK-A4",
             "pyfluent API 与 Fluent 版本不匹配",
             "黄",
             "journal 作底线；pyfluent 作便利层"],
            ["RK-A5",
             "24 核工作站被整板网格拖死",
             '<span class="warn2">橙</span>',
             "硬闸门：阶段 4 未关不得上全模"],
            ["RK-A6",
             "把 Agent 生成的 journal 当已验证设置",
             '<span class="bad">红</span>',
             "每条 journal 必须在目标版本空跑一次"],
        ]))
    s.append(h3("9.2　开放项"))
    s.append(table(
        ["编号", "问题", "谁拍板", "卡住哪一阶段"],
        [
            ["O-CFD-01",
             "单元胞出口：环缝 vs 短槽侧出口", "热设计负责人", "阶段 1"],
            ["O-CFD-02",
             "网格路线：ICEM hex vs Fluent Meshing 水密", "仿真负责人", "阶段 0/2"],
            ["O-CFD-03",
             "ANSYS 版本与许可核数", "IT / 仿真", "阶段 0"],
            ["O-CFD-04",
             "是否允许远程/HPC 队列", "项目", "阶段 5"],
            ["O-CFD-05",
             "工具最终是否就定 ICEM+Fluent"
             "（报告 §10.2 仍写「待定」）", "项目", "阶段 0"],
            ["O-CFD-06",
             "官方 power map（设计报告 IN-T4）", "OEM",
             "不影响单元胞，挡住整板热点案"],
        ]))
    s.append(h3("9.3　工具待定（TBD）"))
    s.append(ul([
        "<strong>TBD-1 求解器品牌</strong>：本文件按用户指定的 ICEM/Fluent 做交互评估，"
        "不关闭 §10.2 的选型门。若最终改 Icepak/FloTHERM，阶段 1 几何仍可复用，"
        "journal 作废。",
        "<strong>TBD-2 网格器</strong>：ICEM 与 Fluent Meshing 二选一，见 O-CFD-02。",
        "<strong>TBD-3 远程执行</strong>：本机无求解器时，是装本地、还是 SSH 到许可服务器，未定。",
        "<strong>TBD-4 开源兜底</strong>：若长期无许可，单元胞可用 gmsh+OpenFOAM 做 V4 练习；"
        "不作为交付求解器，除非项目改口。系统 Python 目前也未装 gmsh。",
    ]))
    s.append("</section>")
    return "".join(s)


def ch10():
    s = ['<section id="gng">']
    s.append(h2("10.", "Go / No-Go 表", "gng"))
    s.append(table(
        ["闸门", "Go 条件", "本机 (2026-09-20)", "未满足时允许做什么"],
        [
            ["G0 环境",
             "找到 Fluent+网格器，许可核数 ≥ 8",
             '<span class="bad">NO-GO</span>',
             "写几何、写脚本、写本计划；禁止说「CFD 已开算」"],
            ["G1 几何",
             "单元胞 STEP 面命名齐全，尺寸=GEO",
             '<span class="warn2">未开工</span>',
             "不得进入网格"],
            ["G2 网格",
             "y⁺&lt;1，正交&gt;0.15，三套网格就位",
             "未开始",
             "不得进入设计点结论"],
            ["G3 V4",
             "Re=3000 的 Nu 对 Martin &lt;15%",
             "未开始",
             "不得采信设计点 h（外推无锚）"],
            ["G4 设计点包络",
             "层流与 SST 的 h、ΔP 均已报；"
             "h 能解释一维带宽或指出模型缺陷",
             "未开始",
             "不得改孔径/槽深"],
            ["G5 扩阵",
             "G4 关闭 + 网格量/HPC 评估书面通过",
             "未开始",
             "不得开整板 C01–C12"],
        ]))
    s.append(p(
        "与设计报告 DR3 / C-07 对齐：单元胞关闭只证明「设置可信」，"
        "不证明「产品达标」。整板 R<sub>θ,c-in</sub> 单值仍要 C01 共轭给出。"))
    s.append("</section>")
    return "".join(s)


def ch11():
    s = ['<section id="next">']
    s.append(h2("11.", "下一步（按依赖排序）", "next"))
    s.append(ol([
        "<strong>人：关闭 O-CFD-03 / G0</strong> — "
        "给出 ANSYS 安装路径与许可证，或明确改用远程机。"
        "没有这一步，阶段 2 以后都是文本。",
        "<strong>人：关闭 O-CFD-01 / O-CFD-02</strong> — "
        "单元胞出口形式、ICEM hex 还是 Fluent Meshing。",
        "<strong>Agent：阶段 1 几何</strong> — "
        f"在 CAD 链上增加单元胞构建器（D={G['D_jet']:.2f}、"
        f"H={G['H_jet']:.1f}、S={G['S_jet']:.1f} mm），导出带命名面的 STEP。",
        "<strong>Agent：起草控制脚本</strong> — "
        "Fluent journal（求解+报表）必写；ICEM replay 仅在选定 hex 后写；"
        "pyfluent 等包装上再写可执行版。",
        "<strong>人+Agent：阶段 2–4</strong> — "
        "G0 绿灯后在目标版本空跑 journal，做 V4 再做设计点。",
        "<strong>禁止抢跑</strong> — "
        f"不要把 {G['plate_L']:.0f}×{G['plate_W']:.0f} mm 整板 STEP "
        f"或 {M.N_JET} 孔共轭当作本周任务。",
    ]))
    s.append(note(
        "若 5 个工作日内 G0 仍为红，建议把阶段 1 几何与 journal 草稿先入库，"
        "同时把「求解器到位」升级为项目风险，而不是继续扩写计划文档。",
        "ok"))
    s.append("</section>")
    return "".join(s)


def appendix():
    s = ['<section id="appx">']
    s.append(h2("附录", "脚本骨架与探测记录", "appx"))
    s.append(lead(
        "下列文本是<strong>骨架</strong>，不是本机验证过的可执行工程。"
        "版本方言（TUI 关键字、Meshing 工作流名称）必须对照实际安装的 Fluent 年版改写。"
        "没有求解器之前，这些文件的价值是评审接口，不是结果。"))

    s.append(h3("A. 本机探测原始记录"))
    s.append(table(
        ["检查", "命令或位置", "结果"],
        [
            ["AWP_ROOT*", "Get-ChildItem Env:AWP_ROOT*", "无"],
            ["典型安装根",
             r"C:\Program Files\ANSYS Inc 及 (x86)、D:\、E:\ 同类路径",
             "均不存在"],
            ["可执行文件",
             "fluent / fluent.exe / icemcfd / wb.exe / runwb2 / ansysedt",
             "Get-Command 与 where 均无"],
            ["注册表 Uninstall",
             "DisplayName ~ ANSYS|Fluent|ICEM",
             "无匹配"],
            ["license.dat 浅扫",
             r"C:\ D:\ E:\ 深度 4，过滤 ANSYS/Fluent/flexlm",
             "无"],
            ["系统 Python 绑定",
             "ansys.fluent.core / pyfluent / pythonnet / gmsh / build123d",
             "全部 missing"],
            ["CAD 虚拟环境",
             PROBE["cad_venv"],
             "build123d FOUND，OCP FOUND，ansys.fluent.core missing"],
            ["仓库脚本",
             "coolingplate 下 *.jou *.rpl *.scm *.wbjn *.cas *.msh",
             "0 个；仅有整板 STEP"],
            ["硬件",
             "Win32_Processor / ComputerSystem",
             f"{PROBE['cpu']}，{PROBE['cores']}C/{PROBE['threads']}T，"
             f"{PROBE['ram_gb']:.0f} GB"],
        ]))

    s.append(h3("B. Fluent 批处理调用（安装后）"))
    s.append(p(
        "示意命令，路径用实际 <code>AWP_ROOT</code> 替换。"
        "核数不得超过许可证。"))
    s.append(formula(
        r"%AWP_ROOT%\fluent\ntbin\win64\fluent.exe 3ddp -t16 -g -i uc01_solve.jou",
        result="无 GUI 批跑 16 进程双精度",
        note_="Meshing 模式加 -meshing；Workbench 用 runwb2 -B -R。"))

    s.append(h3("C. Fluent journal 骨架（TUI，须按版本改）"))
    s.append(p(
        "只列出必须出现的控制块，不假装这是某一年份的可运行全文。"))
    s.append(ul([
        "<code>/file/read-case</code> 或从 meshing 写出的 msh；",
        "<code>/define/models/steady</code>，能量开，层流或 visc ke-sst；",
        f"<code>/define/materials</code>：水 ρ={FL.rho:.1f}，"
        f"μ={FL.mu:.3e}，k={FL.k:.3f}，cp={FL.cp:.0f}；",
        f"入口 mass-flow-inlet = {M_JET:.6e} kg/s，T={A['Tin']+273.15:.2f} K；",
        "出口 pressure-outlet 0 Pa（表压）；周期或对称按 UC 定义；",
        "监视：入口/出口压差、底壁热流或面平均 h；",
        "迭代与自动写 dat；",
        "<code>/report/surface-integrals</code> 把 ΔP、h、T 追加到 CSV。",
    ]))

    s.append(h3("D. ICEM replay 骨架（仅当 O-CFD-02 选 hex）"))
    s.append(ul([
        "导入单元胞 STEP → 建 part（INLET/OUTLET/WALL/PER_X/PER_Y）；",
        "单砖块 + 孔处 O-grid；关联边长按 D、H、S 参数化；",
        "壁面第一层 0.003 mm，增长率 1.2，驻点 ≥15 层；",
        "写出 Fluent msh；把质量表导出；",
        "<strong>黄金 replay 必须由人在 GUI 录制第一版</strong>，"
        "Agent 只改尺寸参数后重放。",
    ]))

    s.append(h3("E. pyfluent 草稿意图（包未装，不作为本机可运行代码）"))
    s.append(ul([
        "launch Fluent 与 journal 同等设置；",
        "从 CSV 或 TUI 取值后直接 <code>import model</code> 比对 "
        f"h∈[{A['con']['h_eff']:.0f},{A['opt']['h']:.0f}]、"
        f"ΔP~{A['dp']['orifice']/1000:.2f} kPa；",
        "失败应降级回纯 journal，而不是卡在 API。",
    ]))

    s.append(h3("F. 与设计报告章节对照"))
    s.append(table(
        ["设计报告", "本文件", "关系"],
        [
            ["§9 一维计算", "§6 锚点", "数字同源 model.py"],
            ["§10.1 Q1–Q8", "阶段 5", "单元胞只服务 Q1 的局部 h，不服务 Q2–Q8"],
            ["§10.3 禁止单胞外推整板", "§0 / §7", "全文遵守"],
            ["§10.4 网格", "阶段 2 / UC 规格", "首层 3 μm、y⁺ 原样继承"],
            ["§10.7 C01–C12", "阶段 5 之后", "第一案不占用 C 编号"],
            ["§10.9 V4 Martin 锚定", "UC-01-*-3000 / G3", "第一案的科学核心"],
            ["RK-01 / RK-02", "G4 / G3", "CFD 收窄区间、外推纠偏"],
        ]))

    s.append(h3("G. 复算与再生成"))
    s.append(p(
        "修改 <code>model.py</code> 的 <code>GEO</code> 或 "
        "<code>DESIGN_POINTS</code> 后："))
    s.append(ol([
        "<code>python cp_b300_1d.py</code> 复查一维；",
        "<code>python build_report.py</code> 重生设计报告；",
        "<code>python build_cfd_agent_plan.py</code> 重生本文件。",
        "三份文档的 Re、R 区间、D/H/S 必须继续一致。",
    ]))
    s.append("</section>")
    return "".join(s)


def build():
    nav = "".join(f'<a href="#{a}">{t}</a>' for a, t in NAVITEMS)
    verdict = ("求解器未安装 · 脚本可写 · 第一案必须是单元胞")
    head = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CFD-AI Agent 能力评估与工作计划 {VER} · {DATE}</title>
<meta name="description" content="面向 ANSYS ICEM/Fluent 的大模型能力边界、
本机探测、B300 单元胞第一案规格与分阶段闸门计划">
<style>{CSS}</style>
</head>
<body>
<div class="page">
<header>
  <div class="kicker">CFD-AI Agent Capability Assessment · ICEM / Fluent</div>
  <h1>CFD-AI Agent 能力评估<br>与 ICEM / Fluent 工作计划</h1>
  <div class="sub">
    针对 {MODEL}（NVIDIA B300 微通道 + 冲击换热冷板）。
    一维已给出 R<sub>θ,c-in</sub>
    <strong>{A['R_lo']:.4f}–{A['R_hi']:.4f} °C/W</strong>
    （目标 {A['target']:.3f}），
    Re<sub>D</sub>≈<strong>{A['jet']['Re']:.0f}</strong> 落在 Martin 窗外。
    本文评估大模型与 ICEM/Fluent 的真实交互面，并冻结
    <strong>单孔单元胞</strong>为第一案——不是 95×75 mm 整板。
  </div>
  <div class="meta">
    <span class="pill">文档 {DOC_NO}</span>
    <span class="pill">版本 {VER}</span>
    <span class="pill">{DATE}</span>
    <span class="pill hot">本机无 ANSYS</span>
    <span class="pill warn">G0 = NO-GO</span>
    <span class="pill ok2">1D + CAD 链可用</span>
    <span class="pill">第一案 UC-01 单元胞</span>
  </div>
  <div class="docbar">
    <div>本机求解器<b>未找到 ICEM / Fluent / WB</b></div>
    <div>工作站<b>{PROBE['cores']} 核 · {PROBE['ram_gb']:.0f} GB</b></div>
    <div>设计点 Re<sub>D</sub>
        <b>{A['jet']['Re']:.0f}（Martin 下限 2000）</b></div>
    <div>一维热阻带<b>{A['R_lo']:.4f} – {A['R_hi']:.4f} °C/W</b></div>
  </div>
</header>
<nav>{nav}</nav>
<main>
<p class="lead">{verdict}。数值与
<code>NVIDIA_B300_微通道冲击换热冷板设计报告_v2.0_20260914.html</code>
§9 / §10 同源。</p>
"""
    body = "".join([
        ch0(), ch1(), ch2(), ch3(), ch4(), ch5(),
        ch6(), ch7(), ch8(), ch9(), ch10(), ch11(), appendix(),
    ])
    foot = f"""
</main>
<footer>
  <b>{DOC_NO} · CFD-AI Agent 能力评估与工作计划 {VER} · {DATE}</b><br>
  型号 {MODEL}　|　保证点 DP-A {A['P']:.0f} W @ {A['Q']:.1f} L/min　|　
  第一案单孔 ṁ = {M_JET:.4e} kg/s　|　
  本机 ANSYS：未安装<br>
  本文件是开工与能力边界文件，<b>不是 CFD 仿真报告，不是许可证申请书</b>。
  阶段 0 绿灯前不得宣称三维结果。<br>
  数值可复算：<code>design/calc/model.py</code>；
  本文件可再生成：<code>design/calc/build_cfd_agent_plan.py</code>。
</footer>
</div>
</body>
</html>
"""
    return head + body + foot


if __name__ == "__main__":
    html = build()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已写出: {OUT}")
    print(f"大小: {len(html)/1024:.1f} KB")
    print(f"章节数: {html.count('<section')}　表格数: {html.count('<table')}"
          f"　内嵌 SVG: {html.count('<svg')}　</svg>: {html.count('</svg>')}")
    print(f"h2: {html.count('<h2')}　</h2>: {html.count('</h2>')}")

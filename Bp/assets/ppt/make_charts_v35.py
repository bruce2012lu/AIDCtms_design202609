# -*- coding: utf-8 -*-
"""
算力冷却商业调研报告 v3.5 演示版 —— 新增图表（c31–c36）

复用 make_charts.py 的字体、色系、图注四段式与画布工具，不修改该文件、
不重绘 c01–c30（旧 PNG 全部保留）。

所有数值与表述严格取自：
  《算力冷却商业调研报告_v3.5_20260906.html》第 3A、8、9 章
  《算力冷却系统新业务BP_v2.2_20260906.html》
  《算力冷却_验证与决策包_v1.0_20260905.html》
不得自行增改，不得恢复任何已删除的伪精确点值。

运行： python make_charts_v35.py
只重渲染一张： python -c "import make_charts_v35 as m; m.c31()"
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from make_charts import (NAVY, BLUE, TEAL, RED, AMBER, GREY,
                         _finish, _plain, _canvas, _box, _arrow)

PURPLE = "#6941c6"
PURPLE_BG = "#f7f3ff"
FWS_BG = "#eef4ff"
TCS_BG = "#eef9f3"
CTRL_BG = "#fff6e0"
TX = "#33415a"


def _rbox(ax, x, y, w, h, fc, ec, lw=1.2, r=0.012):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                       fc=fc, ec=ec, lw=lw, zorder=3)
    ax.add_patch(p)
    return p


def _item(ax, x, y, w, h, text, fc="#ffffff", ec="#175cd3", fs=8.4, tc=TX, bold=False):
    _rbox(ax, x, y, w, h, fc, ec, lw=1.0, r=0.008)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", zorder=4,
            linespacing=1.35)


# ============================================================
# c31 CDU 系统架构（报告图 3A-1 SVG 结构重绘）
# ============================================================
def c31():
    """按报告图 3A-1 SVG 四栏结构用 matplotlib 重绘为 300 dpi PNG。"""
    W, H = 12.60, 5.05
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.012, 0.22, 0.976, 0.76])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 97.2, "L2L 液冷 CDU 系统框图：一次侧 FWS ／ CDU 本体 ／ 二次侧 TCS ／ 控制层",
            ha="center", va="top", fontsize=12.2, color=NAVY, fontweight="bold")

    # ---- 一次侧 FWS ----
    _rbox(ax, 0.6, 6, 18.6, 82, FWS_BG, BLUE, lw=1.3)
    ax.text(9.9, 84.5, "一次侧 FWS", ha="center", fontsize=11.2, color=BLUE,
            fontweight="bold", zorder=5)
    ax.text(9.9, 79.6, "设施侧冷却水\n供液温度按 ASHRAE W 等级",
            ha="center", va="top", fontsize=7.6, color=GREY, linespacing=1.35, zorder=5)
    fws = ["冷却塔 / 干冷器 / 冷水机组", "一次侧循环泵 + 调节阀",
           "水处理 / 补水 / 软化", "FWS 流量 / 温度传感"]
    for i, t in enumerate(fws):
        _item(ax, 1.7, 58 - i * 14.2, 16.4, 11.2, t, ec=BLUE, fs=8.2)

    # ---- CDU 本体 ----
    _rbox(ax, 21.6, 6, 38.2, 82, PURPLE_BG, PURPLE, lw=1.6)
    ax.text(40.7, 84.5, "CDU 本体", ha="center", fontsize=11.2, color=PURPLE,
            fontweight="bold", zorder=5)
    ax.text(40.7, 79.8, "系统设计 + 应用控制自留　·　硬件与制造外协",
            ha="center", fontsize=7.8, color=PURPLE, zorder=5)
    left = ["板式换热器 PHE", "双泵 N+1（屏蔽/磁力）+ VFD", "工质处理（脱气 / 补液）"]
    right = ["缓冲箱 / 膨胀箱", "电磁阀 / 止回阀 / 过滤", "温 / 压 / 流 / 漏液传感"]
    for i, (a, b) in enumerate(zip(left, right)):
        y = 61.5 - i * 13.4
        _item(ax, 23.0, y, 17.4, 11.0, a, ec=PURPLE, fs=8.0)
        _item(ax, 41.2, y, 17.4, 11.0, b, ec=PURPLE, fs=8.0)
    _item(ax, 23.0, 18.6, 35.6, 9.6,
          "PLC 控制器 + HMI + 远程 IO（应用控制自留，BSW 授权外协）",
          fc=NAVY, ec=NAVY, fs=8.0, tc="#ffffff", bold=True)
    _item(ax, 23.0, 8.2, 35.6, 8.6,
          "Modbus / SNMP / Redfish / MQTT / OPC UA 对外接口",
          fc=BLUE, ec=BLUE, fs=8.0, tc="#ffffff", bold=True)

    # ---- 二次侧 TCS ----
    _rbox(ax, 62.2, 6, 18.8, 82, TCS_BG, TEAL, lw=1.3)
    ax.text(71.6, 84.5, "二次侧 TCS", ha="center", fontsize=11.2, color=TEAL,
            fontweight="bold", zorder=5)
    ax.text(71.6, 79.6, "工质按 OEM coolant 规范\nDI 水 / PG25 等",
            ha="center", va="top", fontsize=7.6, color=GREY, linespacing=1.35, zorder=5)
    tcs = ["机柜 Manifold + UQD", "服务器节点入口 QD",
           "芯片级冷板（GPU/CPU/HBM）", "回流 Manifold + 漏液托盘"]
    for i, t in enumerate(tcs):
        _item(ax, 63.4, 58 - i * 14.2, 16.4, 11.2, t, ec=TEAL, fs=8.2)

    # ---- 控制 / 上位 ----
    _rbox(ax, 83.4, 42, 16.0, 46, CTRL_BG, AMBER, lw=1.3)
    ax.text(91.4, 84.0, "DCIM / BMS / 上位", ha="center", fontsize=10.0,
            color=AMBER, fontweight="bold", zorder=5)
    for i, t in enumerate(["远程监控", "故障预测（PdM）",
                           "能效优化（效果待实测）", "BMS 联锁停机"]):
        ax.text(91.4, 74.5 - i * 7.6, t, ha="center", fontsize=8.4, color=TX, zorder=5)

    # 连接示意
    ax.annotate("", xy=(21.5, 64), xytext=(19.4, 64),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6), zorder=6)
    ax.annotate("", xy=(62.1, 64), xytext=(59.9, 64),
                arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=1.6), zorder=6)
    ax.annotate("", xy=(83.3, 58), xytext=(59.0, 16),
                arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=1.3,
                                linestyle=(0, (4, 2))), zorder=6)

    ax.text(50, 1.6,
            "蓝色＝一次侧（设施水）　·　紫色＝CDU 本体　·　绿色＝二次侧（IT 侧）　·　橙色＝上位监控接口",
            ha="center", fontsize=8.4, color=GREY)

    note = (
        "单位：无（系统框图，不含量值）。\n"
        "口径：一次侧为设施水 FWS，二次侧为 IT 侧 TCS；两回路在板换处物理隔离，不得拼接（例：华为液冷门回路与计算柜 D2C 回路）。"
        "二次侧工质按 OEM coolant 规范，不写跨厂商单一电导率阈值；一次侧温度按 ASHRAE W 等级，不映射固定 PUE。"
        "能效优化效果待实测，不给节电率。负压改变失效模式，不等于零泄漏。\n"
        "数据性质：自绘示意图，按报告图 3A-1 SVG 结构重绘；无厂商实物照片。\n"
        "来源：报告 v3.5 §3A.4 / 图 3A-1（接回 v2.8，按 v3.x 核验修正）；BP v2.2 微笑曲线口径（应用控制自留，BSW 外协）。")
    _finish(fig, ax, note, "c31_cdu_architecture.png",
            left=0.012, right=0.988, bottom=0.22, top=0.99, spines=False)


# ============================================================
# c32 七量校核流程（报告图 3A-3 SVG 结构重绘）
# ============================================================
def c32():
    fig = plt.figure(figsize=(12.40, 4.85))
    ax = fig.add_axes([0.015, 0.24, 0.970, 0.74])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 97.4, "选型七量校核：任一项为「无数据」即不能判定兼容",
            ha="center", va="top", fontsize=12.4, color=NAVY, fontweight="bold")

    items = [
        ("① IT 功率", "P_IT（TDP / peak）"),
        ("② 液体热负荷 / HCR", "按 OEM/BOM，不跨 OEM 套用"),
        ("③ 温度工质", "TCS/FWS 供回液 + W 等级"),
        ("④ 工质与材料", "DI / PG25 / EG50 + wetted list"),
        ("⑤ Q–ΔP 曲线", "流量可加，支路压降不可加"),
        ("⑥ ATD 逼近温差", "决定有效冷量"),
        ("⑦ 冗余与故障态", "单泵失效 / 滤网脏堵"),
    ]
    n = len(items)
    w, gap = 12.6, 1.15
    x0 = (100 - (n * w + (n - 1) * gap)) / 2
    for i, (h, s) in enumerate(items):
        x = x0 + i * (w + gap)
        _rbox(ax, x, 62, w, 26, FWS_BG, BLUE, lw=1.2)
        ax.text(x + w / 2, 80.6, h, ha="center", fontsize=8.6, color=BLUE,
                fontweight="bold", zorder=5)
        ax.text(x + w / 2, 71.6, s, ha="center", va="center", fontsize=7.5,
                color=TX, linespacing=1.35, zorder=5)
        ax.plot([x + w / 2, x + w / 2], [62, 54.5], color=BLUE, lw=1.3, zorder=2)

    _rbox(ax, 3.2, 36.5, 93.6, 18.0, PURPLE_BG, PURPLE, lw=1.3)
    ax.text(50, 49.4, "L_design = Σ(P_IT × HCR × peak_factor) × (1 + 工程余量)",
            ha="center", fontsize=10.2, color=NAVY, fontweight="bold", zorder=5)
    ax.text(50, 42.2, "N_installed = ceil(L_design / C_effective) + N_redundant",
            ha="center", fontsize=10.0, color=PURPLE, zorder=5)

    ax.plot([50, 50], [36.5, 29.8], color=PURPLE, lw=1.4, zorder=2)
    _rbox(ax, 8.0, 8.5, 84.0, 21.0, CTRL_BG, AMBER, lw=1.3)
    ax.text(50, 23.6, "C_effective 目前四档全为无数据（§9.2）",
            ha="center", fontsize=11.0, color=RED, fontweight="bold", zorder=5)
    ax.text(50, 15.6,
            "任何「200 / 300 / 450 kW 覆盖 X 柜」的承诺当前不成立\n"
            "由 M5 客户书面平台包 + M9 样机矩阵关闭　·　泵 N+1 ≠ 系统 N+1 CDU 容量",
            ha="center", va="center", fontsize=8.6, color=TX, linespacing=1.45, zorder=5)

    note = (
        "单位：kW（功率 / 液体负荷）；无量纲（HCR、peak_factor）。\n"
        "口径：七个量必须同时校核。最常见误用：①用铭牌冷量代替有效冷量；②把不同回路流量或压降相加；③用同代际其他 OEM 的 HCR 或流量推算本平台。"
        "GB300 按 OEM/BOM 给液体带热比例，不给统一 HCR；N1380 量热保证无数据，HCR 保留条件；"
        "Dell 504 kW 是供电/母排生态能力；Supermicro 250 kW 是方案移热能力，不是固定 IT 铭牌。\n"
        "数据性质：流程图为自绘；C_effective 四档为无数据裁决。算法示例（不构成覆盖承诺）：Lenovo GB300 "
        "L_design(1 柜) = 135 × 0.90 × (155/135) = 139.5 kW（peak），TDP 口径 121.5 kW。\n"
        "来源：报告 v3.5 §3A.2 / §3A.5 / 图 3A-3；Lenovo GB300 Product Guide Table 27（一级）；§9.2 有效能力矩阵。")
    _finish(fig, ax, note, "c32_seven_checks.png",
            left=0.015, right=0.985, bottom=0.24, top=0.99, spines=False)


# ============================================================
# c33 配置形态与容量阶梯（删 ASP；额定工况示例）
# ============================================================
def c33():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.40, 4.95),
                                   gridspec_kw={"width_ratios": [1.12, 0.88]})

    # ---- 左：形态 ----
    forms = [
        (TEAL, "In-Rack\n机内 4–10U", "约 15–300 kW", "失效域：单柜",
         "阶段一主推\n50–150 kW"),
        (BLUE, "Side-Car\n机柜外挂", "约 50–200 kW", "失效域：1–2 柜",
         "阶段一主推\n存量改造"),
        (NAVY, "In-Row / Row\n行间 / 落地", "约 200 kW–1.35 MW", "失效域：2–10 柜",
         "阶段二\n按项目 qualification"),
        (GREY, "机房级 Hall\nOCP Deschutes", "1–2.5 MW", "失效域：整 Pod",
         "不主推\n避免与 Vertiv 正面竞争"),
    ]
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 100)
    ax1.axis("off")
    ax1.set_title("配置形态：阶段一先做失效域小的形态", fontsize=11.4,
                  color=NAVY, pad=8, loc="left")
    for i, (c, name, cap, fail, rec) in enumerate(forms):
        x = 2 + i * 24.4
        _rbox(ax1, x, 18, 22.8, 72, "#f8fafc", c, lw=1.4)
        _rbox(ax1, x, 72, 22.8, 18, c, c, lw=0)
        ax1.text(x + 11.4, 81, name, ha="center", va="center", fontsize=9.0,
                 color="#ffffff", fontweight="bold", linespacing=1.35, zorder=5)
        ax1.text(x + 11.4, 62, cap, ha="center", fontsize=10.4, color=c,
                 fontweight="bold", zorder=5)
        ax1.text(x + 11.4, 50, fail, ha="center", fontsize=8.4, color=TX, zorder=5)
        ax1.text(x + 11.4, 32, rec, ha="center", fontsize=8.6, color=c,
                 fontweight="bold", linespacing=1.45, zorder=5)
    ax1.text(50, 8.5, "公开产品容量区间为厂商规格（二级），不是本公司额定值　·　ASP 列已删除（无数据）",
             ha="center", fontsize=8.2, color=GREY)

    # ---- 右：额定工况示例 ----
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.axis("off")
    ax2.set_title("额定冷量不是常数：两个一手示例", fontsize=11.4,
                  color=NAVY, pad=8, loc="left")

    _rbox(ax2, 3, 54, 94, 38, FWS_BG, BLUE, lw=1.3)
    ax2.text(50, 86.5, "Vertiv XDU450", ha="center", fontsize=11.2, color=BLUE,
             fontweight="bold", zorder=5)
    ax2.text(50, 72.5,
             "名义 453 kW　建立在 4℃ ATD 等指定工况\n"
             "改变温度 / 流量 / 压降 / 工质后有效冷量即变化",
             ha="center", va="center", fontsize=8.8, color=TX, linespacing=1.55, zorder=5)

    _rbox(ax2, 3, 10, 94, 38, TCS_BG, TEAL, lw=1.3)
    ax2.text(50, 42.5, "OCP Project Deschutes", ha="center", fontsize=11.2,
             color=TEAL, fontweight="bold", zorder=5)
    ax2.text(50, 28.5,
             "2 MW　对应 3℃ ATD、500 GPM、80–90 psi\n"
             "N+1 无密封泵　·　开放规范，不是认证",
             ha="center", va="center", fontsize=8.8, color=TX, linespacing=1.55, zorder=5)

    note = (
        "单位：kW / MW（公开产品容量区间）；℃（ATD）；GPM / psi（Deschutes 规范工况）。\n"
        "口径：形态容量为公开产品区间，不是本公司 100/200/300/450 kW 的额定值或覆盖承诺。"
        "本公司阶段一主推 In-Rack 50–150 kW 与 Side-Car 100–200 kW；阶段二进入 Row / In-Row 200–500 kW；"
        "阶段三不主推机房级。v2.8「ASP 区间」「覆盖几柜」两列不接回。W-class 只定义供液温度上限，不映射 PUE。\n"
        "数据性质：Vertiv XDU450 为原厂数据表（一级）；OCP Deschutes 为开放规范（二级）；形态区间为厂商规格综合（二级/三级）。"
        "本公司四档有效能力矩阵每一格仍为无数据。\n"
        "来源：Vertiv XDU450 datasheet；OCP Specification Deschutes 2025-09-05；报告 v3.5 §3A.4.2 / §3A.5.1 / §3A.7.1；BP v2.2 阶段划分。")
    _finish(fig, [ax1, ax2], note, "c33_cdu_forms_ladder.png",
            left=0.02, right=0.985, bottom=0.30, top=0.92, wspace=0.10, spines=False)


# ============================================================
# c34 冷板工艺与路线（阶段三；禁止 PCB 冷板误用）
# ============================================================
def c34():
    fig = plt.figure(figsize=(12.40, 5.05))
    ax = fig.add_axes([0.015, 0.26, 0.970, 0.72])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 97.6, "芯片级 / 微通道冷板：阶段三才进入　·　工艺只做定性对比",
            ha="center", va="top", fontsize=12.2, color=NAVY, fontweight="bold")

    # 术语纪律条
    _rbox(ax, 2, 82.5, 96, 11.5, "#fff7f6", RED, lw=1.2)
    ax.text(50, 88.2,
            "术语纪律：「PCB 冷板」仅在流道真正集成于印制电路板时使用；本公司阶段三做的是芯片级 / 微通道冷板托盘，不称 PCB 冷板",
            ha="center", va="center", fontsize=9.0, color=RED, fontweight="bold", zorder=5)

    seals = [
        (BLUE, "CNC + 真空钎焊", "产品化 · 阶段三起步",
         "CNC 铣槽 + 盖板真空钎焊\n中端 GPU / 小批量定制\n相对成本中、工艺难度低"),
        (TEAL, "真空钎焊 / 蚀刻叠焊", "产品化 · 阶段三主推",
         "多片铜箔蚀刻 + 真空钎焊\n高功率 GPU / HBM 一体\n耐压约 5–10 MPa（通行量级）"),
        (PURPLE, "扩散焊", "产品化后期 · 高端",
         "原子级键合\n耐压约 10–20 MPa（通行量级）\n相对成本高、不可拆"),
    ]
    for i, (c, name, tag, body) in enumerate(seals):
        x = 2 + i * 32.4
        _rbox(ax, x, 42, 30.8, 37.5, "#f8fafc", c, lw=1.4)
        _rbox(ax, x, 68.2, 30.8, 11.3, c, c, lw=0)
        ax.text(x + 15.4, 73.8, name, ha="center", fontsize=11.0, color="#ffffff",
                fontweight="bold", zorder=5)
        ax.text(x + 15.4, 64.6, tag, ha="center", fontsize=8.4, color=c,
                fontweight="bold", zorder=5)
        ax.text(x + 15.4, 53.4, body, ha="center", va="center", fontsize=8.6,
                color=TX, linespacing=1.55, zorder=5)

    # 三层成熟度
    layers = [
        (BLUE, "产品化", "刨削 / 蚀刻叠焊 / CNC 钎焊 / 铝挤"),
        (AMBER, "验证", "3D 打印 · VC 复合 · 喷射冲击 · 两相冷板"),
        (GREY, "研究", "封装内嵌 / 硅内嵌微流道 · CVD 金刚石基底"),
    ]
    for i, (c, name, body) in enumerate(layers):
        x = 2 + i * 32.4
        _rbox(ax, x, 8, 30.8, 29.5, "#ffffff", c, lw=1.2)
        ax.text(x + 15.4, 31.4, name, ha="center", fontsize=10.5, color=c,
                fontweight="bold", zorder=5)
        ax.text(x + 15.4, 20.2, body, ha="center", va="center", fontsize=8.4,
                color=TX, linespacing=1.50, zorder=5)

    note = (
        "单位：MPa（密封工艺典型耐压，工程手册 / 供应商资料量级）；℃/W、kPa 的热阻与压降目标均为本公司内部目标，本图不展开点值。\n"
        "口径：只做结构 / 工艺难度 / 成熟度分层的定性对比。v2.8 原表的热阻、压降、热流密度、量产良率、量产时点五列已删除，不接回。"
        "验证层不得写入客户承诺；研究层不得给量产时点、良率、寿命或专利壁垒点值。"
        "本图冷板不与 PCB 集成。水质按 OEM coolant 规范，不写跨厂商单一阈值。\n"
        "数据性质：工艺分层与供应商名为公开信息综合（二级）；耐压为通行量级，具体件以供应商书面值与本公司测试为准；"
        "阶段三内部目标须热阻标定台验证。\n"
        "来源：报告 v3.5 §3A.3 / §3A.9.1 / §3A.9.3 / 图 3A-2；§9.1 产品定义（冷板托盘留在阶段三）。")
    _finish(fig, ax, note, "c34_coldplate_routes.png",
            left=0.015, right=0.985, bottom=0.26, top=0.99, spines=False)


# ============================================================
# c35 标准分层与 qualification（五分法；无统一认证）
# ============================================================
def c35():
    fig = plt.figure(figsize=(12.40, 5.00))
    ax = fig.add_axes([0.012, 0.24, 0.976, 0.74])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 97.6, "标准五分法：已发布 ≠ 认证　·　不存在公开统一 NVIDIA / 华为 CDU 认证",
            ha="center", va="top", fontsize=12.0, color=NAVY, fontweight="bold")

    layers = [
        (NAVY, 2, 78, 18.4, "正式标准\n已实施", "YD/T 6049-2024\nYD/T 6358-2025"),
        (BLUE, 21.6, 78, 18.4, "正式标准\n待实施", "GB/T 48023-2026\n2027-02-01 实施"),
        (TEAL, 41.2, 78, 18.4, "开放规范", "OCP coolant v1.3\nOCP UQD / Deschutes"),
        (AMBER, 60.8, 78, 18.4, "厂商规格", "NVIDIA MGX / NVL72\n华为 Atlas 接口"),
        (GREY, 80.4, 78, 18.4, "草案 / 内部目标", "2025-1993T-YD\n内部 MTBF / 负压"),
    ]
    for c, x, y, w, name, ex in layers:
        _rbox(ax, x, 52, w, 38, "#f8fafc", c, lw=1.4)
        _rbox(ax, x, 75.6, w, 14.4, c, c, lw=0)
        ax.text(x + w / 2, 82.8, name, ha="center", va="center", fontsize=9.0,
                color="#ffffff", fontweight="bold", linespacing=1.30, zorder=5)
        ax.text(x + w / 2, 62.6, ex, ha="center", va="center", fontsize=8.2,
                color=TX, linespacing=1.50, zorder=5)

    ax.text(50, 47.6, "以上五行「是否等于产品认证」全部为否　·　标准给合同提供技术依据，不是准入凭证",
            ha="center", fontsize=9.2, color=RED, fontweight="bold")

    # 九步链（压缩）
    steps = ["平台/BOM\n冻结", "TCS/FWS\nQ–ΔP 对齐", "材料·压力\n泄漏·遥测",
             "DVT/PVT\n或 PoC", "FAT", "安装联调", "SAT/ISAT", "最终验收", "项目BOM\n/ 订单"]
    n = len(steps)
    sw, sg = 9.4, 1.15
    sx0 = (100 - (n * sw + (n - 1) * sg)) / 2
    for i, s in enumerate(steps):
        x = sx0 + i * (sw + sg)
        col = BLUE if i < 4 else (TEAL if i < 7 else NAVY)
        _rbox(ax, x, 22.5, sw, 19.5, col, col, lw=0)
        ax.text(x + sw / 2, 32.2, s, ha="center", va="center", fontsize=7.4,
                color="#ffffff", fontweight="bold", linespacing=1.30, zorder=5)
        if i < n - 1:
            ax.annotate("", xy=(x + sw + sg - 0.15, 32.2),
                        xytext=(x + sw + 0.15, 32.2),
                        arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.2,
                                        mutation_scale=10), zorder=5)

    _rbox(ax, 3, 4.5, 94, 15.5, "#fff7f6", RED, lw=1.2)
    ax.text(50, 12.2,
            "NPN 是伙伴计划，NVIDIA-Certified Systems 面向整机；华为有公司级供应商体系，未公开 Atlas CDU 完整名录\n"
            "准入是逐项目九步 qualification 的固定成本，不可摊薄为一次投入；不得写「已获大厂认证」",
            ha="center", va="center", fontsize=8.6, color=RED, linespacing=1.45, zorder=5)

    note = (
        "单位：无（属性分层与流程）。\n"
        "口径：五分法把正式标准、待实施、开放规范、厂商规格、草案/内部目标分开；草案参数不可当现行要求。"
        "OCP / ODCC 是规范符合性，不是认证。W-class 不是 PUE；水质按 OEM coolant；负压≠零泄漏；MTBF 仅为内部目标。\n"
        "数据性质：标准状态为官方条目（一级）；「不存在公开统一 CDU 认证」为截至 2026-08-22 的公开证据裁决。\n"
        "来源：报告 v3.5 §8.1 / §8.1.1 / §8.3；YD/T 6049-2024、YD/T 6358-2025、GB/T 48023-2026、OCP coolant v1.3；"
        "NVIDIA Partner Network / NVIDIA-Certified Systems；华为采购供应商 FAQ。")
    _finish(fig, ax, note, "c35_standards_qualification.png",
            left=0.012, right=0.988, bottom=0.24, top=0.99, spines=False)


# ============================================================
# c36 软件栈：应用控制自留 / BSW 外协
# ============================================================
def c36():
    fig = plt.figure(figsize=(12.40, 4.90))
    ax = fig.add_axes([0.015, 0.24, 0.970, 0.74])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 97.4, "控制系统是 CDU 的大脑：应用控制自留，基础软件授权外协",
            ha="center", va="top", fontsize=12.2, color=NAVY, fontweight="bold")

    layers = [
        (NAVY, 68, "③ 上位监控 / DCIM 对接",
         "可视化 · 时序库 · 报警引擎 · 能效模型",
         "应用与数据资产自留", "基础框架外协并托管"),
        (BLUE, 40, "② 数据 / 网络层（Gateway）",
         "边缘网关 · 工业交换 · 协议转换 · TLS 上行",
         "数据模型与缓存策略自留", "协议栈授权外协"),
        (TEAL, 12, "① 工业控制层（Edge）",
         "PLC + HMI + 远程 IO　·　控制逻辑（梯形图 / ST）",
         "控制逻辑自研", "PLC 硬件与 BSW 外购 / 授权"),
    ]
    for c, y, name, comp, keep, out in layers:
        _rbox(ax, 2, y, 96, 24.5, "#f8fafc", c, lw=1.4)
        _rbox(ax, 2, y, 3.2, 24.5, c, c, lw=0)
        ax.text(8.2, y + 17.6, name, ha="left", fontsize=11.0, color=c,
                fontweight="bold", zorder=5)
        ax.text(8.2, y + 10.4, comp, ha="left", fontsize=8.8, color=TX, zorder=5)
        _rbox(ax, 52, y + 3.4, 21.6, 8.6, "#eaf1fd", BLUE, lw=1.0)
        ax.text(62.8, y + 7.7, keep, ha="center", va="center", fontsize=8.2,
                color=BLUE, fontweight="bold", zorder=5)
        _rbox(ax, 75.2, y + 3.4, 20.8, 8.6, "#f2f4f7", GREY, lw=1.0)
        ax.text(85.6, y + 7.7, out, ha="center", va="center", fontsize=8.2,
                color=GREY, fontweight="bold", zorder=5)

    ax.text(50, 6.4,
            "保障：源码托管 · 版本冻结 · step-in rights　·　v2.8「上位 SaaS 全自研」已收窄　·　无统一 CDU 认证，Redfish / OpenBMC 按项目对齐",
            ha="center", fontsize=8.6, color=NAVY)

    note = (
        "单位：无（职责分层）。\n"
        "口径：按 BP v2.2 微笑曲线，自留需求定义、系统架构、应用控制策略、报警与故障态逻辑、数据模型与能效算法；"
        "PLC 硬件、BSW、协议栈、时序数据库与 Web 框架授权外协。"
        "OCP Cooling Environments / UQD 为开放规范；NVIDIA MGX 与华为 Atlas 为厂商规格，不存在公开统一 CDU 认证。\n"
        "数据性质：分工为 BP 口径与报告工程接回，不是收入或毛利预测；能效寻优效果须现场 A/B 实测，不给节电率。\n"
        "来源：报告 v3.5 §3A.8 / §3A.8.1 / §3A.8.3；BP v2.2 微笑曲线与软件 / IP 边界。")
    _finish(fig, ax, note, "c36_software_stack.png",
            left=0.015, right=0.985, bottom=0.24, top=0.99, spines=False)


def build():
    c31()
    c32()
    c33()
    c34()
    c35()
    c36()
    print("done: c31 / c32 / c33 / c34 / c35 / c36")


if __name__ == "__main__":
    build()

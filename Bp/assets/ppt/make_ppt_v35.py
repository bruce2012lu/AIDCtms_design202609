# -*- coding: utf-8 -*-
"""
算力冷却商业调研报告 v3.5 演示版 —— PPTX 生成脚本

复用 make_ppt.py 的全部版式工具与既有页面函数，复用 make_ppt_v33.py 已对齐
BP v2.2 / 决策包的商业页，不修改那两份文件、不覆盖 v3.3 演示稿。

相对 v3.3 演示版的改动：
  · 封面 / 页脚 / 封底：版本改为 v3.5 Integrated / 20260906，证据基线 v3.5
  · 一页结论：结论 2 指向第 3A 章七量校核
  · 工程篇新增 6 页（c31–c36）：CDU 架构、七量校核、形态阶梯、冷板工艺、
    标准五分法、软件栈；平台矩阵改写为七量
  · 市场页（含第 15 页三分母嵌套饼图）与商业页数字原样保留
数据来源：《算力冷却商业调研报告_v3.5_20260906.html》
        《算力冷却系统新业务BP_v2.2_20260906.html》
        《算力冷却_验证与决策包_v1.0_20260905.html》

运行： python make_charts_v33.py && python make_charts_v35.py && python make_ppt_v35.py
"""
import os

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

import make_ppt as M
import make_ppt_v33 as V33
from make_ppt import (NAVY, BLUE, TEAL, RED, AMBER, GREY, DARKTX, WHITE, LINE,
                      BGBLUE, BGTEAL, BGRED, BGAMBER, BGGREY, FONT,
                      SW, SH, ML, CW, BODY_Y, BODY_H,
                      tb, para, rect, hline, new_slide, takeaway,
                      chart_slide, make_table)

M.VERSION = "v3.5 Integrated"
M.CUTOFF = "数据截止 2026-09-05"
M.OUT_PPTX = os.path.join(M.BP_DIR, "算力冷却商业调研报告_v3.5_演示版_20260906.pptx")

prs = M.prs
BLANK = M.BLANK
_page = M._page


# =====================================================================
# 1 封面（v3.5）
# =====================================================================
def slide_cover():
    _page[0] += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, SW, SH, NAVY, None)
    rect(s, 0, 0, 0.22, SH, BLUE, None)
    rect(s, 0, SH - 0.10, SW, 0.10, TEAL, None)

    _, tf = tb(s, 1.0, 0.85, 11.0, 0.34)
    para(tf, "Commercial Research Report · 演示版 / 20260906", 12,
         RGBColor(0x8F, 0xB4, 0xE8), bold=True, first=True)

    _, tf = tb(s, 1.0, 1.30, 11.4, 1.15)
    para(tf, "算力冷却商业调研报告", 44, WHITE, bold=True, first=True, line=1.05)

    _, tf = tb(s, 1.0, 2.50, 11.4, 0.80)
    para(tf, "高密 AI 基础设施液冷：需求、算力基建投资、液冷占比、工程边界、竞争、准入、", 15.5,
         RGBColor(0xC9, 0xD8, 0xFF), first=True, line=1.35)
    para(tf, "项目池与验证期权　·　v3.5 接回第 3A 章工程深度，商业口径对齐 BP v2.2 / 决策包", 15.5,
         RGBColor(0xC9, 0xD8, 0xFF), line=1.35)

    hline(s, 1.0, 3.52, 11.3, RGBColor(0x2A, 0x47, 0x66), 1.2)

    kpis = [
        ("接近 30 → 约 70 亿美元",
         "Dell'Oro 全球液冷设备制造商收入\n2025 机构估计 → 2029 机构预测；TAM 主锚（未变）"),
        ("10.36% ／ 684.75–715.00 元/kW",
         "曙光数创冷板液冷毛利率；两个运营商采购样本\n折算的单位容量包价上限（决策包口径）"),
        ("第 3A 章工程深度已接回",
         "CDU 架构 / 七量校核 / 冷板工艺 / 标准五分法\nSAM 24m 仍为无数据，不是 0"),
    ]
    for i, (big, sub) in enumerate(kpis):
        x = 1.0 + i * 3.83
        rect(s, x, 3.75, 3.55, 1.30, RGBColor(0x10, 0x2A, 0x4C), None)
        _, tf = tb(s, x + 0.18, 3.90, 3.24, 0.42)
        para(tf, big, 13.5 if i == 1 else 16,
             RGBColor(0x7E, 0xC8, 0xBE) if i == 2 else WHITE, bold=True, first=True)
        _, tf = tb(s, x + 0.18, 4.36, 3.22, 0.62)
        para(tf, sub, 9, RGBColor(0x9F, 0xB3, 0xCC), first=True, line=1.35)

    meta = [("版本", "v3.5 Integrated"), ("数据截止日", "2026-09-05"),
            ("演示日期", "2026-09-06"),
            ("市场序列口径", "2026-08-22（未变）"),
            ("配套 BP", "v2.2_20260906"),
            ("配套决策包", "验证与决策包 v1.0_20260905")]
    for i, (k, v) in enumerate(meta):
        x = 1.0 + (i % 3) * 3.83
        y = 5.25 + (i // 3) * 0.42
        _, tf = tb(s, x, y, 3.70, 0.36)
        p = tf.paragraphs[0]
        p.line_spacing = 1.2
        r = p.add_run(); r.text = k + "："
        r.font.size = Pt(10); r.font.color.rgb = RGBColor(0x6E, 0x86, 0xA6)
        r.font.name = FONT
        r = p.add_run(); r.text = v
        r.font.size = Pt(10); r.font.bold = True; r.font.color.rgb = WHITE
        r.font.name = FONT

    rect(s, 1.0, 6.28, 4.05, 0.42, RGBColor(0x5B, 0x14, 0x0E), None)
    _, tf = tb(s, 1.16, 6.37, 3.85, 0.28)
    para(tf, "机密 · 仅供董事会与核心团队讨论", 11, RGBColor(0xFF, 0xC9, 0xC4),
         bold=True, first=True)
    _, tf = tb(s, 5.35, 6.30, 7.0, 0.60)
    para(tf, "本报告不构成证券投资建议、产品认证或采购承诺。总体结论 valid_until 2026-11-30；投资与占比章节 2027-02-28；",
         9, RGBColor(0x8F, 0xA4, 0xBE), first=True, line=1.35)
    para(tf, "价格与现金实证 2026-12-31；责任结构 2027-03-31。本演示稿不修改任何既有报告、BP 与 v3.3 演示稿。",
         9, RGBColor(0x8F, 0xA4, 0xBE), line=1.35)


# =====================================================================
# 2 一页结论（v3.5：结论 2 指向 3A）
# =====================================================================
def slide_conclusions():
    s = new_slide("结论先行",
                  "需求方向成立；工程壁垒在平台级适配，商业缺口已转化为可行域与生存条件")
    y = takeaway(s, BODY_Y, [
        "当前证据只支持「受客户、工程、责任与现金门禁约束的小规模验证期权」，不支持按行业 CAGR 批准量产扩张。",
        "「已明确验证路径」不等于「已验证」：研究充分性裁决仍为 SUFFICIENT WITH LIMITATIONS，SAM/SOM 仍为无数据。",
    ], NAVY, BGBLUE)

    items = [
        ("1", "需求方向强，口径不可相加", "设备、整机、宽产业是不同分母，任何两项不得相加",
         "0.92 / 2027-01-31", BLUE),
        ("2", "工程壁垒是平台级适配",
         "铭牌冷量不能证明兼容；须同时校核 IT 功率、HCR、温度工质、Q–ΔP、ATD、冗余（第 3A 章）",
         "0.94 / 2026-11-30", BLUE),
        ("3", "增长不保证高毛利；毛利集中在海外与服务侧",
         "三家一手年报：英维克境外 52.64% vs 境内 23.83%；申菱方案服务 31.63% vs 设备 21.46%；曙光服务 51.02% vs 冷板 10.36%",
         "披露事实 0.93；方向可迁移性 0.70", TEAL),
        ("4", "公开招标不能验证单位经济，但已能约束价格可行域",
         "两个包价样本折算收敛在 684.75–715.00 元/kW（差 4.4%），可作 300–500 kW 档价格上限边界，不是价格预测",
         "0.96；折算值 0.85 / 2026-12-31", TEAL),
        ("5", "液冷在算力投资中价值占比极低，且高度依赖分母", "占总投资长期不到 1%，占设施侧约 1%–6%，占 DCPI 约 5%–11%",
         "相对量级 0.80；任一点值 0.35 / 2027-02-28", AMBER),
        ("6", "最优策略是验证期权，且取证必须先于样机支出",
         "四项前置证据 < 5 万元、6–8 周，保护 245 万元样机与 NRE 支出，保护比 49:1",
         "0.88 / 2026-12-31", RED),
    ]
    cw = (CW - 0.30) / 2
    ch = 1.42
    for i, (num, head, body, conf, col) in enumerate(items):
        x = ML + (i % 2) * (cw + 0.30)
        yy = y + 0.16 + (i // 2) * (ch + 0.18)
        rect(s, x, yy, cw, ch, RGBColor(0xFA, 0xFC, 0xFF), LINE, 0.75)
        rect(s, x, yy, 0.055, ch, col, None)
        _, tf = tb(s, x + 0.20, yy + 0.11, 0.34, 0.30)
        para(tf, num, 15, col, bold=True, first=True)
        _, tf = tb(s, x + 0.58, yy + 0.09, cw - 0.78, 0.62)
        para(tf, head, 11.8, NAVY, bold=True, first=True, line=1.18)
        _, tf = tb(s, x + 0.58, yy + 0.62, cw - 0.78, 0.50)
        para(tf, body, 9.2, DARKTX, first=True, line=1.26)
        _, tf = tb(s, x + 0.58, yy + 1.13, cw - 0.78, 0.24)
        para(tf, "置信度 / valid_until：" + conf, 8.8, col, bold=True, first=True)


# =====================================================================
# 平台矩阵（v3.5：五项 → 七量；保留已修正表述）
# =====================================================================
def slide_platform_matrix_v35():
    s = new_slide("工程篇（四）",
                  "平台工程基线：铭牌冷量不能证明兼容，七个量必须同时校核")
    y = takeaway(s, BODY_Y, [
        "只记录同一版本、同一回路可比较的数据；公开未披露即写「无数据」，不得用其他 OEM 参数替代。",
        "选型须同时校核：IT 功率 · 液体热负荷/HCR · 温度工质 · 流量 · Q–ΔP · ATD · 冗余与故障态。",
    ], NAVY, BGBLUE)

    rows = [
        ["平台 / 版本", "IT 功率", "液体负荷 / HCR", "TCS 温度 / 工质", "工程裁决"],
        [("Lenovo GB300 NVL72\n2026-08-13 update", NAVY, True), "135 kW TDP\n155 kW peak",
         "约 90%；121.5–139.5 kW\n为本报告推导", "供液 25–45℃；DI water\n或 PG25；回液无数据",
         "当前最完整的一柜曲线；\n项目须确认曲线对应工质"],
        [("Lenovo N1380 / SC750 V4", NAVY, True), "54 kW / enclosure\n三套 162 kW DC",
         ("量热保证无数据；公开架构\n称接近全水冷", RED), "供液 27/32/40/45℃；\n处理洁净水；回液无数据",
         "流量可加，支路压降不可\n相加；HCR 保留条件"],
        [("Huawei Atlas 900 A3", NAVY, True), "计算柜最大 66 kW",
         "约 70%，随配置；46.2 kW\n仅为本报告粗算", "液冷门供液 5–32℃；\n纯水或 EG50；回液无数据",
         ("液冷门回路与计算柜 D2C\n回路不得拼接", RED)],
        [("HPE GB200 NVL72 v4", NAVY, True), "132 kW / rack",
         "115 kW liquid + 17 kW air", ("公开摘要无数据", RED),
         "液体负荷可用，水力须取\nsite readiness 包"],
        [("Dell IR7000 + XE8712", NAVY, True), "特定配置最高\n264 kW / rack",
         ("HCR / 液体 kW 无数据", RED), "28/32/36/40℃；\nDell validated PG25",
         "504 kW 是供电/母排生态\n能力，非本配置液体负荷"],
    ]
    make_table(s, ML, y + 0.16, CW, [2.3, 1.6, 2.4, 2.4, 2.6], rows,
               font=8.8, hdr_font=10, row_h=0.63, hdr_h=0.34)

    yy = y + 0.16 + 0.34 + 5 * 0.63 + 0.18
    _, tf = tb(s, ML, yy, CW, 0.52)
    para(tf, "NVIDIA DGX GB200（约 120 kW/rack）、Supermicro DLC-2（方案移热能力最高 250 kW，非固定 IT 铭牌）与 NVIDIA Rubin（原厂路线称 100% 液冷，固定 rack kW 未披露）三项关键字段为无数据，不承诺任何容量档覆盖柜数。",
         9.2, GREY, first=True, line=1.3)
    para(tf, "来源：Lenovo GB300 Product Guide Table 27；N1380 Configuration Guide Tables 1–4；Atlas 900 A3 技术规格；Dell Rack-Scale DLC Guidelines pp.4–5, 18–19。报告 v3.5 表 3A.1。",
         9.2, GREY, line=1.3)


# =====================================================================
# 封底（v3.5）
# =====================================================================
def slide_back_v35():
    _page[0] += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, SW, SH, NAVY, None)
    rect(s, 0, 0, SW, 0.10, TEAL, None)
    _, tf = tb(s, 1.2, 2.35, 11.0, 0.70)
    para(tf, "算力冷却商业调研报告 · v3.5 Integrated", 28, WHITE, bold=True,
         first=True)
    _, tf = tb(s, 1.2, 3.12, 11.0, 0.40)
    para(tf, "演示版 / 20260906　·　数据截止 2026-09-05　·　配套《算力冷却系统新业务BP》v2.2_20260906",
         13, RGBColor(0xC9, 0xD8, 0xFF), first=True)
    hline(s, 1.2, 3.75, 10.9, RGBColor(0x2A, 0x47, 0x66), 1.2)
    _, tf = tb(s, 1.2, 3.98, 11.0, 1.70)
    lines = [
        "本演示稿由《算力冷却商业调研报告 v3.5》与《算力冷却_验证与决策包 v1.0》整理而成，全部数据取自该两份文件与配套 BP v2.2，",
        "未引入其中没有的数字，未恢复已删除的伪精确点值。工程页按第 3A 章接回并经 v3.x 核验修正；商业页对齐决策包倒推纪律。",
        "三级来源（GPU 基板 3.5–5.0 万美元、责任上限 10%–20%、年降 5%–8%、海外 200–240 美元/kW）已保留等级标注，不得写成行业事实。",
        "所有图表为本演示稿自绘（matplotlib + python-pptx）。图 3A-1 / 3A-3 SVG 已重绘为 300 dpi PNG。总体结论 valid_until 2026-11-30。",
    ]
    for t in lines:
        para(tf, t, 10.5, RGBColor(0x9F, 0xB3, 0xCC),
             first=(t.startswith("本演示稿由")), line=1.62)
    rect(s, 1.2, 5.86, 4.4, 0.44, RGBColor(0x5B, 0x14, 0x0E), None)
    _, tf = tb(s, 1.38, 5.96, 4.2, 0.28)
    para(tf, "机密 · 仅供董事会与核心团队讨论", 11.5, RGBColor(0xFF, 0xC9, 0xC4),
         bold=True, first=True)
    _, tf = tb(s, SW - 2.2, 5.96, 1.6, 0.28, align=PP_ALIGN.RIGHT)
    para(tf, f"{_page[0]}", 11, RGBColor(0x6E, 0x86, 0xA6), bold=True, first=True,
         align=PP_ALIGN.RIGHT)


# =====================================================================
# 组装
# =====================================================================
def build():
    slide_cover()                       # [改] 1
    slide_conclusions()                 # [改] 2

    chart_slide("阅读须知（一）", "两套独立标签体系：来源等级决定证据力，数据性质决定这个数字是什么",
                "c20_evidence_pyramid.png",
                ["全文每个数字都同时带来源等级与数据性质；机构端点、本报告桥接与本报告情景必须能被一眼区分。",
                 "「无数据」是一种裁决结果，不是遗漏 —— 报告中共有 SAM/SOM、ASP、毛利、ROIC、CDU 能力矩阵等多处保持无数据。"])

    M.slide_discipline()

    chart_slide("市场篇（一）", "需求方向没有争议：用电五年翻倍、容量需求五年增 1.7 倍，但三条曲线分母不同",
                "c01_power_capacity.png",
                ["2025 → 2030 机构端点：用电 485 → 950 TWh（IEA）；关键 IT 需求 82 → 219 GW（McKinsey）；设施供给 103 → 200 GW（JLL）。",
                 "需求 219 GW 高于供给 200 GW 不等于订单缺口：两者定义、基准、时点、占用与可交付性不同，不可相减。"])

    chart_slide("市场篇（二）", "机柜功率密度在一代内从 66 kW 跃到 264 kW —— 风冷延寿空间被物理压缩",
                "c02_rack_power.png",
                ["Dell'Oro 称「1 MW 机柜正在临近」；NVIDIA Rubin 路线称 100% 液冷，Vera Rubin 计算托盘取消风扇。",
                 "但铭牌功率不是采购依据：Supermicro 250 kW 是方案移热能力，Dell 264 kW 是特定配置最高值，504 kW 是供电/母排。"])

    chart_slide("市场篇（三）", "真正约束液冷需求的不是规划容量，而是每年实际投运的 10–28 GW",
                "c03_new_commissioned.png",
                ["JLL：2025 年 57% 项目延迟至少 3 个月，主要市场并网平均等待超过 4 年；C&W：全球大负荷平均供电周期 4.4 年。",
                 "管理动作：在建与规划 pipeline 不计入当年投运，也不计入任何 SAM；项目预算只跟随已获电、已开工、平台已冻结的批次。"],
                note="逐年投运量无任何机构发布 —— 全部为本报告由 JLL 累计端点桥接的模型值。")

    chart_slide("市场篇（四）", "AI 占存量容量约 25% → 50%，但占新增容量高达 76% —— 两个分母差一倍",
                "c04_ai_share.png",
                ["v3.1 曾把存量份额当作新增份额使用；v3.2 已在表 2.5.2 列名中标明「存量口径」，并单列 65%–82% 的新增份额序列。",
                 "这一区分直接决定自下而上模型的 IT 腿：用错分母会把液冷相关容量低估近一半。"])

    chart_slide("市场篇（五）", "算力基建总投资 2025 年约 6,500–8,050 亿美元，2030 年约 1.64–2.05 万亿美元",
                "c05_capex_layers.png",
                ["先分层再谈占比：不同机构所称的「数据中心投资」相差十倍以上，主因是层级不同而非数据冲突。",
                 "使用边界（强制）：本序列仅用于外部市场锚定与情景分析，不得换算为公司收入预算、SAM/SOM、产能规划、ASP 或毛利率。"],
                note="confidence 0.72 / valid_until 2027-02-28　·　机构只发布累计口径，全部年度序列为本报告模型")

    chart_slide("市场篇（六）", "两条独立路径交叉验证后的裁决：McKinsey 6.7 万亿基准情景已过时，改用加速情景",
                "c06_path_ab.png",
                ["路径 B 的 IT 腿自下而上低估约 36%（容量法 2,040 亿 vs IDC 实测 3,180 亿），四项原因逐条披露，不取平均掩盖。",
                 "处置：L1 以路径 B 为主锚（设施侧有 JLL、Epoch AI、Turner & Townsend 三个独立每 MW 证据），L2 以 IDC 实测为主锚。"],
                note="反向风险：加速情景依赖 AI 投资回报持续被市场接受；若 2027 年融资收紧，实际路径可能快速回落到 A-基准甚至 A-受限。")

    chart_slide("市场篇（七）", "四大厂商 CapEx 只作旁证：它证伪了基准情景，但不能除以 L3 得「份额」",
                "c14_hyperscaler_capex.png",
                ["四家使用三种不同 CapEx 定义，含办公、网络骨干、自研芯片预付等非数据中心支出，与全球 L3 口径不同。",
                 "四家之外还有 Oracle、xAI、CoreWeave、字节、阿里、腾讯与主权 AI 项目等大量投资主体，因此该表不得相加进 L3。"],
                color=AMBER, bg=BGAMBER)

    chart_slide("市场篇（八）", "液冷设备市场：2029 年约 70 亿美元合理，但整条曲线只有两个机构端点",
                "c07_lc_scenarios.png",
                ["三重合理性校验（宏观占比、容量强度、机柜强度）均通过量级检查，但都不能独立闭环 —— 只能作异常检查。",
                 "董事会外部 TAM 采用 2032 年 90–140 亿美元（本报告模型），Base 约 115 亿；不是机构预测、不是 CDU SAM/SOM、不是公司可得收入。"],
                note="invalidate_if：Dell'Oro 新版偏离 2029 年 60–80 亿美元；2027–2028 已获电投运或 AI 液冷采用显著落后；设备价格年降幅 >15% 且瓦数/配置不能抵消。")

    chart_slide("市场篇（九）", "Dell'Oro 的四个版本必须隔离：70 − 58 = 12 不是浸没与 RDHx 的规模",
                "c08_delloro_versions.png",
                ["这是本报告最关键的方法论纪律之一：三个数字分属三个发布版本、三个边界，底层逐年表与方法为付费内容，不可见。",
                 "禁止：母子精确拆分、跨版本相减、连成连续年度曲线、拼成一条占比序列。新版发布即重设端点。"],
                color=RED, bg=BGRED)

    chart_slide("市场篇（十）", "液冷占比取决于分母，同一年三个比例相差约 30 倍",
                "c09_three_denominators.png",
                ["同一个分子（液冷设备制造商收入），换三个分母：占 L3 约 0.3%–0.9%，占 L1 约 1.3%–5.6%，占 DCPI 约 5%–11%。",
                 "任何引用必须同时写出分母层级与来源版本。只写「液冷约占 10%」或「液冷不到 1%」都是误导。"],
                color=RED, bg=BGRED,
                note="相对量级 confidence 0.80；任一年份的任一点值 confidence 0.35 —— 禁止点值引用。")

    chart_slide("市场篇（十 · 续）", "30 倍差距来自分母层级：L3 ⊃ L1 ⊃ DCPI ⊃ 液冷",
                "c30_denominator_pies.png",
                ["同一分子（液冷设备制造商收入，2029 年约 70 亿美元）依次放进三个嵌套分母：占 L3 约 0.3%–0.5%、占 L1 约 1.7%–2.9%、占 DCPI 约 5%–8%。",
                 "饼① 约 81% 是 IT 设备，与液冷供应商无竞争关系；饼② DCPI 以外部分与饼③ 其他品类均无公开细分金额，宁可合并为「其他」也不编造比例。"],
                color=RED, bg=BGRED,
                note="扇区按表 2.6.5 Base 值绘制、仅示意量级；对外引用一律用区间，并同时写明分母层级与 Dell'Oro 版本。")

    chart_slide("市场篇（十一）", "同一个分子、同一年，换 Dell'Oro 的版本就从 10%–13% 变成 5%–8%",
                "c10_version_sensitivity.png",
                ["变化几乎全部来自 Dell'Oro 扩大 DCPI 边界并上调预测，不是液冷竞争地位下降。",
                 "v3.1 正文的「2029 液冷约占旧版 DCPI 631 亿美元的 10%–13%」仍然正确 —— 但只在旧版口径下正确。"],
                color=AMBER, bg=BGAMBER)

    M.slide_denominator_usage()

    chart_slide("市场篇（十三）", "设施侧「液冷投入」是设备制造商收入的 5–6 倍 —— 差额被 EPC 与安装截留",
                "c11_facility_vs_manufacturer.png",
                ["这解释了工程口径与市场口径的表面矛盾：「液冷占 AI 机房造价 15%–33%」是项目造价科目，与本报告的 1%–6% 不在同一分母。",
                 "对本业务的含义：能进入独立设备供应商可争夺池子的，只有右侧那一段。"])

    chart_slide("市场篇（十四）", "占比不是稳定参数：四项推高、四项压低、一项方向不确定",
                "c25_share_drivers.png",
                ["2030 年组①、组② 同时出现台阶，主要来自 Dell'Oro 新版 DLC「超过 80 亿美元」造成的预测版本跳点，不解释为有机改善。",
                 "其中「OEM/ODM 垂直整合」与「设施侧 EPC 吃掉价值」两项对独立供应商的杀伤最直接。"])

    # ---------------- 工程篇：保留三层路线 + 新增 3A 六页 ----------------
    chart_slide("工程篇（一）", "技术路线按成熟度三分：只有第一层已产品化，后两层不给性能点值",
                "c23_tech_routes.png",
                ["主边界是冷板式直接液冷（CDU、冷板、Manifold、UQD、工质、二次管路、控制、安装调试与流体运维）。",
                 "「PCB 冷板」仅在流道真正集成于印制电路板时使用；其余一律称芯片级 / 微通道冷板。浸没与两相不进入收入分母。"])

    chart_slide("工程篇（二）",
                "CDU 卖的是可验证系统与责任闭环：一次侧 FWS / 本体 / 二次侧 TCS / 控制层",
                "c31_cdu_architecture.png",
                ["核心职责是热量交换、流量分配、压差稳定、水质保护与漏液隔离；二次侧工质按 OEM coolant，不写单一电导率阈值。",
                 "应用控制自留、BSW 授权外协。能效优化效果待实测；负压改变失效模式，不等于零泄漏。"],
                note="按报告图 3A-1 SVG 结构重绘为 300 dpi PNG，未嵌入外链矢量。")

    chart_slide("工程篇（三）",
                "七量缺一项即不能判定兼容：200 / 300 / 450 kW 不是平台兼容承诺",
                "c32_seven_checks.png",
                ["必须同时校核 IT 功率、液体热负荷/HCR、温度工质、流量、Q–ΔP、ATD、冗余与故障态。",
                 "C_effective 四档全为无数据。Dell 504 kW 是供电/母排；Supermicro 250 kW 是方案移热；GB300 按 OEM/BOM。"],
                color=RED, bg=BGRED,
                note="v2.8「200/300/450 kW 各覆盖几柜」对照表不接回。泵 N+1 ≠ 系统 N+1 CDU 容量。")

    slide_platform_matrix_v35()         # [改] 七量

    chart_slide("工程篇（五）", "供液温度从 25℃ 升到 45℃：流量约 3 倍，压降约 8 倍",
                "c12_qdp_curve.png",
                ["这是当前公开资料中最完整的一柜 Q–ΔP 曲线，也是「铭牌冷量不能证明兼容」最直观的证据。",
                 "项目必须确认曲线对应的工质（DI water 或 PG25）；不同 OEM 的流量与压降不可互相套用，支路压降不可相加。"])

    chart_slide("工程篇（六）",
                "形态先选失效域：阶段一 In-Rack / Side-Car；额定冷量必须写清工况",
                "c33_cdu_forms_ladder.png",
                ["阶段一主推 In-Rack 50–150 kW 与 Side-Car 100–200 kW；阶段二才进入 Row / In-Row 200–500 kW。",
                 "Vertiv XDU450 名义 453 kW 建立在 4℃ ATD；OCP Deschutes 2 MW 对应 3℃ ATD、500 GPM、N+1 无密封泵。"],
                note="ASP 列已删除。W-class 只定义供液温度，不映射固定 PUE。机房级不主推。")

    chart_slide("工程篇（七）", "容量档不是兼容承诺：四档 × 四类工况的有效能力当前全部为无数据",
                "c26_cdu_matrix_na.png",
                ["这不是资料收集不足，而是尚无样机热性能与 PQ 矩阵；解锁条件是客户 RFQ 加样机实测，不是更多公开检索。",
                 "在矩阵填实之前，任何「我们的 300 kW CDU 支持某平台」的表述都不成立。"],
                color=RED, bg=BGRED)

    chart_slide("工程篇（八）",
                "冷板只做定性对比：阶段三才进入芯片级 / 微通道，禁止把托盘误称为 PCB 冷板",
                "c34_coldplate_routes.png",
                ["产品化层：CNC + 真空钎焊起步，蚀刻叠焊 / 真空钎焊主推，扩散焊为高端后期。验证层与研究层不给性能点值。",
                 "「PCB 冷板」仅在流道真正集成于印制电路板时使用；本报告阶段三做的是芯片级 / 微通道冷板托盘。"],
                color=AMBER, bg=BGAMBER,
                note="热阻、压降、量产良率与量产时点点值已撤销，不接回。")

    chart_slide("工程篇（九）",
                "不存在公开可验证的统一 CDU 认证 —— 标准五分法，准入是逐项目九步 qualification",
                "c35_standards_qualification.png",
                ["正式标准 / 待实施 / 开放规范 / 厂商规格 / 草案必须分开；五行「是否等于产品认证」全部为否。",
                 "NPN 是伙伴计划；NVIDIA-Certified Systems 面向整机；华为未公开 Atlas CDU 完整名录。"],
                color=RED, bg=BGRED,
                note="营销材料只可写具体项目、具体平台、具体版本的 qualification 状态，不得写「已获大厂认证」。")

    chart_slide("工程篇（十）",
                "软件栈按微笑曲线切开：应用控制自留，PLC 硬件与 BSW 授权外协",
                "c36_software_stack.png",
                ["自留需求定义、架构、控制策略、故障态逻辑、数据模型与能效算法；保障手段是源码托管、版本冻结与 step-in rights。",
                 "OCP / UQD 是开放规范；NVIDIA MGX 与华为 Atlas 是厂商规格。v2.8「上位 SaaS 全自研」已收窄。"],
                color=TEAL, bg=BGTEAL)

    chart_slide("格局篇（一）", "竞争已全栈化：三笔并购把液冷装进了水处理、电力与预制模块的全栈组合里",
                "c24_competition.png",
                ["壁垒已从设备转向全球服务、流体管理与责任承担；新进入者要面对的是组合方案，不是单机比价。",
                 "所有可比数字必须按四层严格分列，不以集团收入或集团毛利冒充液冷收入或毛利。"])

    chart_slide("格局篇（二）", "唯一可用的纯液冷毛利实绩：冷板 10.36%，与浸没 36.49% 相差三倍",
                "c13_margin_evidence.png",
                ["这是报告中仅有的、口径较纯的历史可比毛利证据，也是「增长不保证高毛利」的直接支撑。",
                 "复算：298,639,495.45 − 267,702,360.46 = 30,937,134.99；÷ 298,639,495.45 = 10.3594%，与年报披露自洽。"],
                color=AMBER, bg=BGAMBER,
                note="下行反证：2026 H1 冷板收入 +290.09%，同期归母净利 −7,340 万元、经营现金流 −2.42 亿元 —— 10.36% 不是行业地板。")

    chart_slide("商业篇（一）", "把资本压在微笑曲线两端：中段的器件、基础软件与制造交给受控供应商",
                "c16_smile_curve.png",
                ["自留七项价值控制点：需求权、架构权、版本权、变更权、放行权、数据权、客户权。",
                 "外协不转移最终责任：ISO 9001 外部过程控制原则与产品质量法都要求本公司保留最终放行、品牌与客户责任。"],
                color=TEAL, bg=BGTEAL)

    chart_slide("商业篇（二）", "商业三步走：2027 启动，800 / 1,200 / 1,500 万元是阶段上限而非承诺额度",
                "c18_roadmap.png",
                ["阶段 2、3 是条件期权。只有订单、贡献、回款、可靠性与现金跑道同时达标才解锁，缺一即冻结。",
                 "优先 50–200 kW。BP v2.2 在 G0 与 G1 之间新增 G0.5 前置证据门：只加严次序，不新增额度。"],
                color=TEAL, bg=BGTEAL)

    chart_slide("商业篇（三）", "行业 TAM 增长推导不出公司收入：中间横着五道项目门和六个断点",
                "c19_tam_sam_som.png",
                ["六个断点：分母、可交付、准入、价格、现金、模型。任何一个都足以让「TAM × 目标份额」失效。",
                 "SAM 24m 与 SOM 当前均为无数据 —— 不是 0，而是公开可核验的合格项目尚未闭环。"],
                color=RED, bg=BGRED)

    V33.slide_unit_economics_v33()

    chart_slide("商业篇（五）",
                "价格可行域与国内运营商采购上限不重叠；所需毛利率高于国内一手实证 4–27 个百分点",
                "c27_price_band_margin_gap.png",
                ["同边界成本下界 840 元/kW，高于国内运营商包价上限 684.75–715.00 元/kW 约 17%–23%：两者不重叠。",
                 "倒推所需 27%–37% vs 国内一手实证 10.36%–23.83%。这是「必须达到什么」，不是「将会达到什么」。"],
                color=RED, bg=BGRED,
                note="国内运营商裸设备渠道据此由「待验证机会」降级为「待排除假说」——在取得反证前，不得作为阶段一收入与毛利来源。")

    chart_slide("商业篇（六）",
                "责任敞口：最小事故即合同额 1.76–2.52 倍；责任封顶是业务前提，不是谈判技巧",
                "c28_liability_multiples.png",
                ["一次约 50 ml 冷却液损坏单块 GPU 基板 = 合同额 1.76–2.52 倍、项目毛利 17.0–24.3 倍。",
                 "行业指引转引的 10%–20% 责任上限（1.43–2.86 万元）仅覆盖单块基板成本的 4%–11%。"],
                color=RED, bg=BGRED,
                note="R1–R6 无法达成即不接单，且该判定先于报价。技术故障隔离是唯一降低敞口本身的手段（4.71 倍）。")

    chart_slide("商业篇（七）",
                "最小验证集与保护比 49:1 —— 用 < 5 万元、6–8 周决定 245 万元该不该花",
                "c29_min_evidence_gate.png",
                ["四项前置证据 M1 / M3 / M4 / M5 合计现金成本 < 5 万元、周期 6–8 周，全部取得前不得启动样机与 NRE 采购。",
                 "245 万元占阶段一 800 万元上限的 30.6%，且是阶段一唯一一笔不可回收的大额支出。复算：(115 + 130) ÷ 5 = 49.0。"],
                color=TEAL, bg=BGTEAL,
                note="G0.5 只规定支出次序，不新增额度、不放宽 G1 的任何既有判据；M3/M4/M5 本就是 G1 必需项，本门只把它们提前到花钱之前。")

    chart_slide("商业篇（八）", "资金门禁 G0–G3：证据不到位，钱就不出去",
                "c22_gates.png",
                ["每道门同时约束工程、商业、质量、责任、现金与组织六个维度，任一硬门未达即自动冻结。",
                 "现金生存条件：峰值 91 万元/MW，并行约 1 个项目，最低现金 171 万元；预付款是生存条件，不是商务优惠。"],
                color=TEAL, bg=BGTEAL)

    M.slide_counterarguments()
    M.slide_tracking()
    V33.slide_next_steps_v33()
    slide_back_v35()

    prs.save(M.OUT_PPTX)
    print("saved:", M.OUT_PPTX)
    print("slides:", len(prs.slides._sldIdLst))


if __name__ == "__main__":
    build()

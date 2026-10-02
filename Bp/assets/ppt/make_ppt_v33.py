# -*- coding: utf-8 -*-
"""
算力冷却商业调研报告 v3.3 演示版 —— PPTX 生成脚本

复用 make_ppt.py 的全部版式工具与既有页面函数（tb / para / rect / hline /
footer / new_slide / add_image / takeaway / chart_slide / make_table 及
slide_discipline / slide_denominator_usage / slide_platform_matrix /
slide_counterarguments / slide_tracking），不修改该文件、不重写既有页面。

相对 v3.2 演示版的改动：
  · 封面与封底：版本改为 v3.3 / 20260906，数据截止 2026-09-05，配套 BP v2.2
  · 一页结论：结论 3 / 4 / 6 按报告 v3.3 更新
  · 商业篇新增 3 页：价格可行域与实证毛利缺口、责任敞口倍数、最小验证集与保护比
  · 单位经济页：改写为「已转化为可行域与生存条件」
  · 结论页：下一步行动改为四项前置证据
  · 2026-09-06 页面修订（同版本、不升版本号）：第 14 页液冷占比三分母页之后新增第 15 页
    「30 倍差距来自分母层级」三分母嵌套饼图（c30），总页数 38 → 39，后续页码顺延
数据来源：《算力冷却商业调研报告_v3.3_20260906.html》《算力冷却系统新业务BP_v2.2_20260906.html》
        《算力冷却_验证与决策包_v1.0_20260905.html》。不引入三份文件中没有的数字。

运行： python make_charts.py && python make_charts_v33.py && python make_ppt_v33.py
"""
import os

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

import make_ppt as M
from make_ppt import (NAVY, BLUE, TEAL, RED, AMBER, GREY, DARKTX, WHITE, LINE,
                      BGBLUE, BGTEAL, BGRED, BGAMBER, BGGREY, FONT,
                      SW, SH, ML, CW, BODY_Y, BODY_H,
                      tb, para, rect, hline, new_slide, takeaway,
                      chart_slide, make_table)

# ---------- 版本元数据（footer 在调用时读取模块级变量，改这里即可全局生效）----------
M.VERSION = "v3.3 Evidence-led"
M.CUTOFF = "数据截止 2026-09-05"
M.OUT_PPTX = os.path.join(M.BP_DIR, "算力冷却商业调研报告_v3.3_演示版_20260906.pptx")

prs = M.prs
BLANK = M.BLANK
_page = M._page


# =====================================================================
# 1 封面（v3.3）
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
    para(tf, "项目池与验证期权　·　v3.3 补入分部毛利实证、单位容量价格上限与验证路径", 15.5,
         RGBColor(0xC9, 0xD8, 0xFF), line=1.35)

    hline(s, 1.0, 3.52, 11.3, RGBColor(0x2A, 0x47, 0x66), 1.2)

    kpis = [
        ("接近 30 → 约 70 亿美元",
         "Dell'Oro 全球液冷设备制造商收入\n2025 机构估计 → 2029 机构预测；TAM 主锚（未变）"),
        ("10.36% ／ 684.75–715.00 元/kW",
         "v3.3 新增两个可复算实证锚：曙光数创冷板液冷毛利率\n两个运营商采购样本折算的单位容量包价上限"),
        ("SAM 24m = 无数据",
         "但价格、责任、现金已转化为可行域、敞口与生存条件\n验证路径与最小证据集已明确"),
    ]
    for i, (big, sub) in enumerate(kpis):
        x = 1.0 + i * 3.83
        rect(s, x, 3.75, 3.55, 1.30, RGBColor(0x10, 0x2A, 0x4C), None)
        _, tf = tb(s, x + 0.18, 3.90, 3.24, 0.42)
        para(tf, big, 13.5 if i == 1 else 16,
             RGBColor(0x7E, 0xC8, 0xBE) if i == 2 else WHITE, bold=True, first=True)
        _, tf = tb(s, x + 0.18, 4.36, 3.22, 0.62)
        para(tf, sub, 9, RGBColor(0x9F, 0xB3, 0xCC), first=True, line=1.35)

    meta = [("版本", "v3.3 Evidence-led"), ("数据截止日", "2026-09-05"),
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
    para(tf, "价格与现金实证 2026-12-31；责任结构 2027-03-31。本演示稿不修改任何既有报告、BP 与演示稿文件。",
         9, RGBColor(0x8F, 0xA4, 0xBE), line=1.35)


# =====================================================================
# 2 一页结论（v3.3：结论 3 / 4 / 6 更新）
# =====================================================================
def slide_conclusions():
    s = new_slide("结论先行",
                  "需求方向成立；四个缺口已由决策包转化为条件、可行域、敞口与生存条件")
    y = takeaway(s, BODY_Y, [
        "当前证据只支持「受客户、工程、责任与现金门禁约束的小规模验证期权」，不支持按行业 CAGR 批准量产扩张。",
        "「已明确验证路径」不等于「已验证」：研究充分性裁决仍为 SUFFICIENT WITH LIMITATIONS，SAM/SOM 仍为无数据。",
    ], NAVY, BGBLUE)

    items = [
        ("1", "需求方向强，口径不可相加", "设备、整机、宽产业是不同分母，任何两项不得相加",
         "0.92 / 2027-01-31", BLUE),
        ("2", "工程壁垒是平台级适配", "铭牌冷量不能证明平台兼容；水力、材料、冗余与故障态共同决定可用性",
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
# 新增 · 商业篇（六）单位经济：已转化为可行域与生存条件
# =====================================================================
def slide_unit_economics_v33():
    s = new_slide("商业篇（四）",
                  "单位经济：空模型未填实，但已从「无数据」转化为可行域与生存条件")
    y = takeaway(s, BODY_Y, [
        "四个 SKU 的额定工况、ASP、贡献毛利、ROIC 与盈亏平衡仍全部为「无数据」——「无数据」不是 0，不得用二手区间填空。",
        "变化的是：现在已经知道「一旦填实，结果必须落在哪个区间才成立」。以下全部是约束条件，回答「必须达到什么」。",
    ], NAVY, BGBLUE)

    rows = [
        ["维度", "v3.2 的状态", "v3.3 转化后的约束（必须达到什么）", "解锁证据"],
        [("价格", NAVY, True), ("无数据", RED, True),
         ("同边界成本下界 840 元/kW；< 840 必然亏损，840–1,090 不可接单，1,090–1,440 容量不可达，1,440–1,730 可讨论。"
          "国内运营商包价上限 684.75–715.00 元/kW 落在「必然亏损」区间内", RED),
         "M1 四 SKU 书面报价 + M2 两个同边界分项合同价"],
        [("毛利", NAVY, True), ("无数据", RED, True),
         ("倒推所需 27%–37%，国内一手实证 10.36%–23.83%，缺口约 4–27 个百分点。"
          "「提高国内定价」无任何一手实证支持，不在选项之列", RED),
         "M1（降 BOM）；海外与服务方向的前置条件成本"],
        [("责任", NAVY, True), ("无数据", RED, True),
         ("单块 GPU 基板损坏 = 合同额 1.76–2.52 倍、项目毛利 17.0–24.3 倍；行业惯例 10%–20% 上限仅覆盖单块基板成本的 4%–11%。"
          "R1–R6 无法达成即不接单", RED),
         "M3 客户书面责任条款 + 产品责任险报价"],
        [("现金", NAVY, True), ("跑道 NA", RED, True),
         ("峰值 91 万元/MW；并行容量 1.21 MW、年吞吐 1.86 MW，为 F2 盈亏平衡 7.80 MW/年 的 23.8%。"
          "三条底线：最低现金 171 万元 / 最大并行 1 个项目 / 回款延迟容忍 11.2 周", RED),
         "M4 客户书面付款条款（30% 预付款可把 11.2 周延长到 17.1 周）"],
    ]
    make_table(s, ML, y + 0.16, CW, [0.9, 1.1, 6.4, 3.8], rows,
               font=8.8, hdr_font=10.5, row_h=0.92, hdr_h=0.34)

    yy = y + 0.16 + 0.34 + 4 * 0.92 + 0.18
    box = rect(s, ML, yy, CW, 0.62, BGRED, RGBColor(0xF6, 0xC8, 0xC5), 0.75)
    tf = box.text_frame
    tf.margin_left = Inches(0.16)
    para(tf, "隔离条款：以上均为约束边界，不是 ASP、毛利率或现金流预测，不得填入四 SKU 空模型的任何一格。",
         10.5, RED, bold=True, first=True, line=1.22)
    para(tf, "合同额 14.30 万元与项目毛利 1.48 万元采用国内运营商实证包价上限与曙光冷板实证毛利率，是可核验的外部值，不是本公司报价或毛利假设。",
         9.4, DARKTX, line=1.22)


# =====================================================================
# 结论与下一步（v3.3：下一步 = 四项前置证据）
# =====================================================================
def slide_next_steps_v33():
    s = new_slide("风险与结论（三）",
                  "下一步不是扩大研究，也不是做样机 —— 是用 < 5 万元、6–8 周拿到四项书面证据")
    y = takeaway(s, BODY_Y, [
        "本轮可批准：阶段 1 上限 800 万元内的架构、付费 PoC、供应链 / NPI、软件 / IP 与责任验证，以及四项前置取证。",
        "本轮不可批准：在四项证据齐备前启动样机物料、工装与 NRE 采购（含「先小批量试做」）；无订单扩产；无限责任项目。",
    ], NAVY, BGBLUE)

    w = (CW - 0.24) / 2
    yy = y + 0.18

    # 左：四项前置证据
    rect(s, ML, yy, w, 4.16, RGBColor(0xFA, 0xFC, 0xFF), LINE, 0.75)
    rect(s, ML, yy, w, 0.42, NAVY, None)
    _, tf = tb(s, ML + 0.16, yy + 0.09, w - 0.32, 0.26)
    para(tf, "四项前置证据（BP v2.2 §12.1 · G0.5 前置证据门）", 11.5, WHITE,
         bold=True, first=True)
    _, tf = tb(s, ML + 0.16, yy + 0.60, w - 0.32, 3.46)
    todos = [
        ("M1　四 SKU 关键件书面报价", "每类 ≥2 家，含 MOQ / 阶梯价 / 交期 / 质保 / 付款。决定 BOM 能否落到 275–450 元/kW，即单位经济是否可能为正。4–6 周 · ≈0"),
        ("M3　责任条款 + 保险报价", "客户书面责任条款草案 + 产品责任险报价（冷却液释放须明列承保）。决定最坏情景是否会毁掉公司。4–8 周 · 1–3 万元"),
        ("M4　客户书面付款条款", "预付款比例、里程碑比例、账期起算日、质保金 / 保函形式四项齐备。决定并行项目数与现金红线。2–4 周 · ≈0"),
        ("M5　客户书面平台包", "TCS/FWS 温度、Q–ΔP、工质、wetted materials、HCR、冗余与故障态。决定样机设计是否有效。4–8 周 · ≈0"),
    ]
    for i, (k, v) in enumerate(todos):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = 1.26
        p.space_after = Pt(7)
        r = p.add_run(); r.text = f"{k}\n"
        r.font.size = Pt(10.6); r.font.bold = True; r.font.color.rgb = BLUE
        r.font.name = FONT
        r = p.add_run(); r.text = v
        r.font.size = Pt(9.2); r.font.color.rgb = DARKTX; r.font.name = FONT

    # 右上：保护比
    x2 = ML + w + 0.24
    rect(s, x2, yy, w, 1.62, BGRED, RGBColor(0xF6, 0xC8, 0xC5), 0.75)
    rect(s, x2, yy, w, 0.42, RED, None)
    _, tf = tb(s, x2 + 0.16, yy + 0.09, w - 0.32, 0.26)
    para(tf, "为什么次序比速度重要：保护比 49 : 1", 11.5, WHITE, bold=True, first=True)
    _, tf = tb(s, x2 + 0.16, yy + 0.58, w - 0.32, 0.98)
    para(tf, "四项证据合计 < 5 万元、6–8 周，决定 245 万元（NRE 115 + 样机 130）该不该花。",
         10, DARKTX, first=True, line=1.32)
    para(tf, "245 万元占阶段一 800 万元上限的 30.6%，且是阶段一唯一一笔不可回收的大额支出。复算：(115 + 130) ÷ 5 = 49.0。",
         9.4, RED, line=1.32)

    # 右中：阶段一目标改写
    rect(s, x2, yy + 1.76, w, 1.28, BGTEAL, RGBColor(0xB6, 0xE4, 0xD2), 0.75)
    rect(s, x2, yy + 1.76, w, 0.42, TEAL, None)
    _, tf = tb(s, x2 + 0.16, yy + 1.85, w - 0.32, 0.26)
    para(tf, "阶段一目标改写为证据里程碑（BP v2.2 §14.2）", 11.5, WHITE,
         bold=True, first=True)
    _, tf = tb(s, x2 + 0.16, yy + 2.34, w - 0.32, 0.66)
    para(tf, "在 B2 = 1、年吞吐 1.86 MW 的现金约束下，任何「阶段一收入 X 万元」目标在数学上都要求突破 B1 / B2 现金安全底线。",
         9.4, DARKTX, first=True, line=1.30)
    para(tf, "董事会月报不再报收入达成率，改报最小验证集十项的取得状态。",
         9.4, TEAL, line=1.30)

    # 右下：保持无数据
    rect(s, x2, yy + 3.18, w, 0.98, BGGREY, LINE, 0.75)
    _, tf = tb(s, x2 + 0.16, yy + 3.28, w - 0.32, 0.80)
    para(tf, "在 PPT 中保持「无数据」的项目", 10.5, NAVY, bold=True, first=True)
    para(tf, "SAM 24m · SOM · CDU 净 ASP · 四 SKU BOM 与毛利 · 贡献毛利 / ROIC / 盈亏平衡 · CDU 有效能力矩阵。已删除且不予恢复：市场份额、部件价值占比、通用毛利率、CDU 静态 ASP、MTBF 与「零外漏」。",
         8.8, DARKTX, line=1.28)

    _, tf = tb(s, ML, yy + 4.30, CW, 0.30, align=PP_ALIGN.CENTER)
    para(tf, "最终裁决：先用 < 5 万元买清楚四个答案，再决定是否投入 245 万元 —— 而不是先做样机再找客户。",
         12, NAVY, bold=True, first=True, align=PP_ALIGN.CENTER)


# =====================================================================
# 封底（v3.3）
# =====================================================================
def slide_back_v33():
    _page[0] += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, SW, SH, NAVY, None)
    rect(s, 0, 0, SW, 0.10, TEAL, None)
    _, tf = tb(s, 1.2, 2.35, 11.0, 0.70)
    para(tf, "算力冷却商业调研报告 · v3.3 Evidence-led", 28, WHITE, bold=True,
         first=True)
    _, tf = tb(s, 1.2, 3.12, 11.0, 0.40)
    para(tf, "演示版 / 20260906　·　数据截止 2026-09-05　·　配套《算力冷却系统新业务BP》v2.2_20260906",
         13, RGBColor(0xC9, 0xD8, 0xFF), first=True)
    hline(s, 1.2, 3.75, 10.9, RGBColor(0x2A, 0x47, 0x66), 1.2)
    _, tf = tb(s, 1.2, 3.98, 11.0, 1.70)
    lines = [
        "本演示稿由《算力冷却商业调研报告 v3.3》与《算力冷却_验证与决策包 v1.0》整理而成，全部数据取自该两份文件正文，",
        "未引入其中没有的数字，未恢复已删除的伪精确点值。全部倒推结论回答「必须达到什么」，不回答「将会达到什么」。",
        "三级来源（GPU 基板 3.5–5.0 万美元、责任上限 10%–20%、年降 5%–8%、海外 200–240 美元/kW）已保留等级标注，不得写成行业事实。",
        "所有图表为本演示稿自绘（matplotlib + python-pptx），不含任何来源不明的外部图片。总体结论 valid_until 2026-11-30。",
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
# 组装（页序沿用 v3.2，标注 [新] / [改] 的为本次变更）
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
                 "但铭牌功率不是采购依据：Supermicro 250 kW 与 Dell 264 kW 分别是方案移热能力与特定配置最高值，口径不同。"])

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

    # [新 · 2026-09-06 页面修订] 第 15 页：三分母嵌套构成饼图（方案 B：独立成页，后续页码顺延）
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

    chart_slide("技术与格局篇（一）", "技术路线按成熟度三分：只有第一层已产品化，后两层不给性能点值",
                "c23_tech_routes.png",
                ["主边界是冷板式直接液冷（CDU、冷板、Manifold、UQD、工质、二次管路、控制、安装调试与流体运维）。",
                 "浸没、两相与设施侧冷源只作相邻路线比较，不进入本报告的收入分母。"])

    M.slide_platform_matrix()

    chart_slide("技术与格局篇（三）", "供液温度从 25℃ 升到 45℃：流量约 3 倍，压降约 8 倍",
                "c12_qdp_curve.png",
                ["这是当前公开资料中最完整的一柜 Q–ΔP 曲线，也是「铭牌冷量不能证明兼容」最直观的证据。",
                 "项目必须确认曲线对应的工质（DI water 或 PG25）；不同 OEM 的流量与压降不可互相套用，支路压降不可相加。"])

    chart_slide("技术与格局篇（四）", "CDU 卖的是可验证系统与责任闭环，不是铭牌 kW",
                "c17_cdu_schematic.png",
                ["有效冷量随 ATD、供回液温度、工质、泵故障态、海拔与污堵变化，必须以矩阵而非单点表述。",
                 "控制层（应用控制算法、状态机、故障降级、BMS/DCIM 接口、远程诊断）是本业务自留的高附加值环节。"])

    chart_slide("技术与格局篇（五）", "容量档不是兼容承诺：四档 × 四类工况的有效能力当前全部为无数据",
                "c26_cdu_matrix_na.png",
                ["这不是资料收集不足，而是尚无样机热性能与 PQ 矩阵；解锁条件是客户 RFQ 加样机实测，不是更多公开检索。",
                 "在矩阵填实之前，任何「我们的 300 kW CDU 支持某平台」的表述都不成立。"],
                color=RED, bg=BGRED)

    chart_slide("技术与格局篇（六）", "竞争已全栈化：三笔并购把液冷装进了水处理、电力与预制模块的全栈组合里",
                "c24_competition.png",
                ["壁垒已从设备转向全球服务、流体管理与责任承担；新进入者要面对的是组合方案，不是单机比价。",
                 "所有可比数字必须按四层严格分列，不以集团收入或集团毛利冒充液冷收入或毛利。"])

    chart_slide("技术与格局篇（七）", "唯一可用的纯液冷毛利实绩：冷板 10.36%，与浸没 36.49% 相差三倍",
                "c13_margin_evidence.png",
                ["这是报告中仅有的、口径较纯的历史可比毛利证据，也是「增长不保证高毛利」的直接支撑。",
                 "复算：298,639,495.45 − 267,702,360.46 = 30,937,134.99；÷ 298,639,495.45 = 10.3594%，与年报披露自洽。"],
                color=AMBER, bg=BGAMBER,
                note="下行反证：2026 H1 冷板收入 +290.09%，同期归母净利 −7,340 万元、经营现金流 −2.42 亿元 —— 10.36% 不是行业地板。")

    chart_slide("技术与格局篇（八）", "不存在公开可验证的统一 CDU 认证 —— 准入是逐项目的九步 qualification",
                "c21_qualification_chain.png",
                ["NPN 是伙伴计划，NVIDIA-Certified Systems 面向整机；华为有公司级供应商体系，但未公开 Atlas CDU 完整名录。",
                 "营销材料只可写具体项目、具体平台、具体版本的 qualification 状态，不得写「已获大厂认证」。"],
                color=RED, bg=BGRED)

    chart_slide("商业篇（一）", "把资本压在微笑曲线两端：中段的器件、基础软件与制造交给受控供应商",
                "c16_smile_curve.png",
                ["自留七项价值控制点：需求权、架构权、版本权、变更权、放行权、数据权、客户权。",
                 "外协不转移最终责任：ISO 9001 外部过程控制原则与产品质量法都要求本公司保留最终放行、品牌与客户责任。"],
                color=TEAL, bg=BGTEAL)

    chart_slide("商业篇（二）", "商业三步走：2027 启动，800 / 1,200 / 1,500 万元是阶段上限而非承诺额度",
                "c18_roadmap.png",
                ["阶段 2、3 是条件期权。只有订单、贡献、回款、可靠性与现金跑道同时达标才解锁，缺一即冻结。",
                 "BP v2.2 在 G0 与 G1 之间新增 G0.5 前置证据门：只加严次序，不新增额度、不放宽 G1 的任何既有判据。"],
                color=TEAL, bg=BGTEAL)

    chart_slide("商业篇（三）", "行业 TAM 增长推导不出公司收入：中间横着五道项目门和六个断点",
                "c19_tam_sam_som.png",
                ["六个断点：分母、可交付、准入、价格、现金、模型。任何一个都足以让「TAM × 目标份额」失效。",
                 "SAM 24m 与 SOM 当前均为无数据 —— 不是 0，而是公开可核验的合格项目尚未闭环。"],
                color=RED, bg=BGRED)

    slide_unit_economics_v33()          # [改]

    # ---------------- [新] 商业篇（五）（六）（七） ----------------
    chart_slide("商业篇（五）",
                "价格可行域与国内运营商采购上限不重叠；所需毛利率高于国内一手实证 4–27 个百分点",
                "c27_price_band_margin_gap.png",
                ["同边界成本下界 840 元/kW，高于国内运营商包价上限 684.75–715.00 元/kW 约 17%–23%：两者不重叠。",
                 "倒推所需 27%–37% vs 国内一手实证 10.36%–23.83%。这是「必须达到什么」，不是「将会达到什么」。"],
                color=RED, bg=BGRED,
                note="国内运营商裸设备渠道据此由「待验证机会」降级为「待排除假说」——在取得反证前，不得作为阶段一收入与毛利来源。")

    chart_slide("商业篇（六）",
                "责任敞口：最小事故即赔掉 17–24 个项目的全部毛利，而行业惯例上限赔不起一块基板",
                "c28_liability_multiples.png",
                ["一次约 50 ml 冷却液损坏单块 GPU 基板 = 合同额 1.76–2.52 倍、项目毛利 17.0–24.3 倍。",
                 "行业指引转引的 10%–20% 责任上限（1.43–2.86 万元）仅覆盖单块基板成本的 4%–11%。"],
                color=RED, bg=BGRED,
                note="因此责任封顶是业务前提而非谈判技巧：R1–R6 无法达成即不接单，且该判定先于报价。技术故障隔离是唯一降低敞口本身的手段（4.71 倍）。")

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
                 "阶段上限与外部 TAM 无关，不因市场情景上修而调整；G0.5 只规定支出次序，不新增任何额度。"],
                color=TEAL, bg=BGTEAL)

    M.slide_counterarguments()
    M.slide_tracking()
    slide_next_steps_v33()              # [改]
    slide_back_v33()                    # [改]

    prs.save(M.OUT_PPTX)
    print("saved:", M.OUT_PPTX)
    print("slides:", len(prs.slides._sldIdLst))


if __name__ == "__main__":
    build()

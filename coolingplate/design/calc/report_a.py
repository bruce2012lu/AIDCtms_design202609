# -*- coding: utf-8 -*-
"""报告章节 0–5：摘要、设计目标、芯片规格、设计输入、设计流程、性能设计。"""
import model as M
import figures as FG
import figures2 as F2
from rhtml import (h2, h3, h4, p, lead, note, ul, ol, table, cards, fig,
                   imgfig, formula, CONF)

A = M.solve("DP-A")
B = M.solve("DP-B")
AP = M.solve("DP-A", M.PG25_40)
G = M.GEO
HI, MI, LO, FR = CONF["H"], CONF["M"], CONF["L"], CONF["F"]


# ============================================================
def ch0_summary():
    s = ['<section id="exec">']
    s.append(h2("0.", "摘要与结论", "exec"))
    s.append(lead(
        "<strong>一句话：</strong>CP-B300-JM-01 的几何、工艺与接口方案是可行的，"
        "但<strong>热性能尚未被证明</strong>。用两套独立换热模型核算同一几何，"
        f"壳–进液热阻落在 <strong>{A['R_lo']:.4f} – {A['R_hi']:.4f} °C/W</strong>"
        "（DP-A）这个跨度近 2 倍的区间里：乐观端有余量，保守端越过 0.028 的目标线。"
        "因此本版把结论定为<strong>“方案通过、性能待证”</strong>，"
        "并给出明确的闭合路径（CFD → TTV → 孔径/TIM2 杠杆）。"))

    s.append(cards([
        (f"{A['P']:.0f} W", "DP-A 保证点 · Lenovo TGP", ""),
        (f"{B['P']:.0f} W", "DP-B 包络 · NVIDIA 最大 TGP", "blue"),
        (f"{A['R_lo']:.3f}–{A['R_hi']:.3f}", "壳–进液热阻实算区间 °C/W", "warn"),
        (f"{A['dp']['total'][0]/1000:.1f}–{A['dp']['total'][1]/1000:.1f}",
         "板内压降 kPa（上限 20）", "ok"),
    ], 4))

    s.append(h3("0.1　六条结论"))
    s.append(ol([
        "<strong>热源是非均匀的，冷板必须分区。</strong>B300 是双 reticle die + "
        "8 组 12-Hi HBM3E。两颗 die 各约 "
        f"{A['p_die']:.0f} W、面平均 {A['q_die']:.1f} W/cm²；单颗 HBM 约 "
        f"{A['p_hbm']:.1f} W、{A['q_hbm']:.1f} W/cm²，低一个量级且怕冲蚀。"
        "结论：GPU 区用射流 + 短槽，HBM 区<strong>不设喷嘴</strong>、限近壁流速，"
        "中间用隔离肋做真正的水力隔墙。",

        "<strong>胞热流有名义值和 5% 边界冗余，流量不加这 5%。</strong>"
        f"整板仍是 {A['p_die']:.0f}+{A['p_die']:.0f}+"
        f"{A['p_hbm']*M.GEO['n_hbm']:.0f}+{A['p_other']:.0f} = {A['P']:.0f} W。"
        f"两 die GPU 名义热 {A['p_gpu']:.0f} W 进 {M.N_JET} 个胞，"
        f"q''<sub>nominal</sub> = {A['q_cell']:.3f} W/cm²"
        f"（{A['q_cell_si']:.6f} W/m²）。"
        f"施加边界取 {A['flux_margin']:.2f} 倍："
        f"{A['q_bc']:.3f} W/cm²（{A['q_bc_si']:.6f} W/m²），"
        f"对应胞功率 {A['p_gpu_bc']:.1f} W，不是把板规格改成这个数。"
        f"单孔流量仍是 {A['mdot_hole']:.6e} kg/s"
        f"（{A['Qg']/M.N_JET:.6f} L/min）。DP-B 名义 "
        f"{B['q_cell']:.3f} W/cm²，边界 {B['q_bc']:.3f} W/cm²，"
        f"单孔 {B['mdot_hole']:.6e} kg/s。",

        "<strong>水力设计有大量余量，热设计没有。</strong>板内压降实算只有 "
        f"{A['dp']['total'][0]/1000:.1f}–{A['dp']['total'][1]/1000:.1f} kPa，"
        "离 20 kPa 上限很远；而热阻上界已经超标。"
        "<strong>这意味着正确的优化方向是“用压降换换热”</strong>，"
        "而不是继续压压降。",

        "<strong>孔径仍是压降杠杆，但 Martin 换热式不再使用。</strong>"
        f"孔径 0.50 → 0.40 mm（孔数仍为 {M.N_JET}），"
        f"Re_D 从 {M.orifice_sweep()[0]['Re']:.0f} 升到 "
        f"{M.orifice_sweep()[2]['Re']:.0f}，"
        f"孔口压降从 {M.orifice_sweep()[0]['dP']/1000:.2f} kPa 升到 "
        f"{M.orifice_sweep()[2]['dP']/1000:.2f} kPa。"
        "两侧 Re 都低于 2000，Martin 1977 不采用。",

        "<strong>射流雷诺数落在关联式有效域之外。</strong>设计点 "
        f"Re_D ≈ {A['jet']['Re']:.0f}（D=0.50 mm，{M.N_JET} 孔），"
        "Martin 阵列关联式的下限是 2000。"
        "本报告<strong>不把 Martin 外推值当作设计热阻</strong>。"
        "壳–进液用短槽模型加 R_TIM2 区间。"
        "这是必须做三维共轭 CFD 的直接技术原因。",

        "<strong>短槽是肋，不是导管。</strong>按真实“就近抽走”拓扑，槽内流速只有 "
        f"{A['ch']['V']:.3f} m/s（Re ≈ {A['ch']['Re']:.0f}），压降 "
        f"{A['dp']['channel']/1000:.3f} kPa 可忽略。它的作用是把湿润面积放大 "
        f"{M.AREA_GAIN:.2f} 倍（肋效率 {A['con']['eta']:.3f}），"
        "而不是靠通道流速换热。v1.x 把它当 0.74 m/s 的导管算，"
        "隐含了与射流互相矛盾的流动拓扑。",

        "<strong>PG25 不能沿用水的 Martin 百分比。</strong>"
        "Re<sub>D</sub> 低于 2000，Martin h 不采用。"
        f"短槽模型对流热阻从 {A['con']['R']:.4f} 变为 {AP['con']['R']:.4f} °C/W"
        f"（{(AP['con']['R']/A['con']['R']-1)*100:+.0f}%）。"
        "若项目最终用 PG25，必须单独定流量，不能沿用水的 2.0 L/min。",
    ]))

    s.append(h3("0.2　放行判据（本版状态）"))
    s.append(table(
        ["#", "判据", "目标", "本版状态", "结论"],
        [
            ["1", "壳–进液热阻 R<sub>θ,c-in</sub>",
             f"DP-A &lt; {A['target']} °C/W",
             f"{A['R_lo']:.4f} – {A['R_hi']:.4f}",
             '<span class="bad">不判定</span>（区间跨目标线）'],
            ["2", "板内压降 @ 设计流量", "≤ 18 kPa（上限 20）",
             f"{A['dp']['total'][0]/1000:.1f} – "
             f"{A['dp']['total'][1]/1000:.1f} kPa",
             '<span class="good">通过</span>（余量大）'],
            ["3", "HBM 近壁流速",
             f"≤ {G['V_cap_hbm']:.2f} m/s",
             f"{A['hbm']['V']:.3f} m/s（DP-B {B['hbm']['V']:.3f}）",
             '<span class="good">通过</span>'],
            ["4", "流体温升", "参考 &lt; 10 K",
             f"{A['dTf']:.2f} K（DP-B {B['dTf']:.2f} K）",
             '<span class="good">通过</span>'],
            ["5", "几何闭合（尺寸链）", "X/Y/厚度自洽",
             "5 项全部闭合", '<span class="good">通过</span>'],
            ["6", "承压与变形", "3 bar 下应力 &lt;&lt; 屈服",
             "余铜跨槽弯曲应力约 0.02 MPa",
             '<span class="good">通过</span>'],
            ["7", "可制造性", "12–18 个月可交货",
             "机加 + 真空钎焊，无增材出货件",
             '<span class="good">通过</span>'],
            ["8", "结温包络", "T<sub>j</sub> ≤ 90 °C（常见口径）",
             f"{A['Tj'][0]:.0f} – {A['Tj'][1]:.0f} °C",
             '<span class="bad">不判定</span>（上界顶到包络）'],
        ]))
    s.append(note(
        "<strong>本文件不是</strong>NVIDIA / Lenovo 订单 ICD，"
        "也不是 FAT 保证书。封装坐标、官方热图、单板额定流量三项未获得，"
        "第 5–9 章的几何与计算均为<strong>候选设计</strong>，"
        "用于评审与打样，不能直接写入采购合同。", "risk"))
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch1_goals():
    s = ['<section id="goals">']
    s.append(h2("1.", "设计目标", "goals"))
    s.append(lead(
        "设计目标分三层：<strong>项目目标</strong>（为什么做）、"
        "<strong>产品指标</strong>（做到什么程度）、"
        "<strong>验证判据</strong>（怎么算做到了）。"
        "每条指标都标注性质：门槛值不可谈判，目标值是设计瞄准点，"
        "拉伸值用于指导下一代。"))

    s.append(h3("1.1　项目目标"))
    s.append(ol([
        "为 NVIDIA B300（Blackwell Ultra）SXM 模块提供一款"
        "<strong>可在 12–18 个月内量产交付</strong>的单相液冷冷板，"
        "在 1100 W 保证点下满足结温包络，并对 1400 W 给出工程包络。",
        "以<strong>微通道 + 冲击射流分区杂交</strong>结构建立差异化技术资产，"
        "并与同目录专利分析报告的方案 A 权项结构对齐。",
        "工艺路线限定在<strong>机加工 + 真空钎焊</strong>，"
        "不把整板金属增材作为出货基线，以控制良率与交期风险。",
        "输出可被第三方复算的设计文档：所有数值有公式、有脚本、有来源。",
    ]))

    s.append(h3("1.2　产品指标（写入送样大纲）"))
    s.append(table(
        ["类别", "指标", "门槛值", "目标值", "拉伸值", "验证方法"],
        [
            "热",
            ["热", "壳–进液热阻 R<sub>θ,c-in</sub> @ DP-A",
             "≤ 0.032 °C/W", "<strong>&lt; 0.028 °C/W</strong>",
             "≤ 0.024 °C/W", "TTV 加热块 + 共轭 CFD"],
            ["热", "壳–进液热阻 @ DP-B（包络）", "—", "&lt; 0.025 °C/W",
             "≤ 0.022 °C/W", "仅仿真包络，不作出厂保证"],
            ["热", "两 die 中心温差", "≤ 8 K", "<strong>≤ 5 K</strong>",
             "≤ 3 K", "TTV 双加热区 + 红外"],
            ["热", "HBM 区最高壁温", "低于 GPU 驻点壁温", "同左", "—",
             "红外 / 热电偶"],
            "水力",
            ["水力", "板内压降 @ 设计流量", "≤ 20 kPa",
             "<strong>≤ 18 kPa</strong>", "≤ 12 kPa", "流阻曲线实测"],
            ["水力", "设计流量（水，40 °C）", "—",
             f"<strong>{A['Q']:.1f} L/min</strong>", "—",
             f"候选值，{FR}（由托盘分流决定）"],
            ["水力", "HBM 支路近壁流速", f"≤ {G['V_cap_hbm']:.2f} m/s",
             "≤ 0.60 m/s", "—", "CFD + 分区流量标定"],
            ["水力", "分区流量偏差 GPU : HBM", "80 : 20 ±15%",
             "<strong>±10%</strong>", "±5%", "分区流量计"],
            "机械与工艺",
            ["机械", "接触面平面度", "≤ 0.08 mm",
             "<strong>≤ 0.05 mm</strong>", "≤ 0.03 mm", "三坐标 / 平晶"],
            ["机械", "接触面粗糙度 Ra", "≤ 1.6 μm",
             "<strong>≤ 0.8 μm</strong>", "≤ 0.4 μm", "轮廓仪"],
            ["机械", "外形包络（不含快接）", "—",
             f"<strong>{G['plate_L']:.0f}×{G['plate_W']:.0f}×"
             f"{G['plate_T']:.1f} mm</strong>", "—", f"图纸 A0，{FR}"],
            ["机械", "整件质量", "≤ 600 g", "≈ 440 g", "—", "称重"],
            ["工艺", "耐压 / 密封", "1.5× 工作压力保压",
             "3 bar 保压 + 100% 氦检", "—", "氦质谱检漏"],
            ["工艺", "洁净度 / 过滤配套", "系统 ≤ 50 μm",
             f"≤ 孔径 1/10（{G['D_jet']*100:.0f} μm）", "—", "颗粒计数"],
        ], widths=["7%", "26%", "15%", "18%", "12%", "22%"]))

    s.append(h3("1.3　热阻预算的来源：为什么是 0.028"))
    s.append(p(
        "目标值不是拍出来的，是从结温倒推的。取结温包络上限与进液温度之差作为"
        "<strong>全链可用温差</strong>，减去冷板拿不到的封装内热阻，"
        "剩下的才是冷板的预算："))
    s.append(formula(
        "R<sub>θ,j-in</sub>(上限) = (T<sub>j,max</sub> − T<sub>in</sub>) / P"
        " ；　R<sub>θ,c-in</sub>(预算) = R<sub>θ,j-in</sub> − R<sub>pkg</sub>",
        None,
        "R<sub>pkg</sub> = 硅扩散 + TIM1 + 封装盖，取 "
        f"{M.R_PKG[0]}–{M.R_PKG[1]} °C/W（NVIDIA 冻结，本设计不可改）"))
    s.append(table(
        ["设计点", "P", "T<sub>in</sub>", "T<sub>j,max</sub>",
         "可用温差", "R<sub>θ,j-in</sub> 上限", "减 R<sub>pkg</sub> 后预算",
         "本报告取值"],
        [
            ["DP-A", f"{A['P']:.0f} W", "40 °C", "90 °C", "50 K",
             f"{50/A['P']:.4f}", f"{50/A['P']-M.R_PKG[1]:.4f} – "
             f"{50/A['P']-M.R_PKG[0]:.4f}",
             "<strong>&lt; 0.028</strong>"],
            ["DP-B", f"{B['P']:.0f} W", "40 °C", "90 °C", "50 K",
             f"{50/B['P']:.4f}", f"{50/B['P']-M.R_PKG[1]:.4f} – "
             f"{50/B['P']-M.R_PKG[0]:.4f}",
             "<strong>&lt; 0.025</strong>"],
            ["DP-A（最恶进液 45 °C）", f"{A['P']:.0f} W", "45 °C", "90 °C",
             "45 K", f"{45/A['P']:.4f}",
             f"{45/A['P']-M.R_PKG[1]:.4f} – {45/A['P']-M.R_PKG[0]:.4f}",
             "需复核"],
        ]))
    s.append(note(
        f"注意 DP-B 的数学事实：1400 W 下全链上限只有 {50/B['P']:.4f} °C/W，"
        f"扣掉封装内阻后冷板预算仅 {50/B['P']-M.R_PKG[1]:.4f}–"
        f"{50/B['P']-M.R_PKG[0]:.4f} °C/W。"
        "<strong>目标 0.025 已经落在这个区间的上沿</strong>，"
        "说明 1400 W + 独立冷板 + TIM2 的组合在物理上就很紧，"
        "这也是业界走向盖板一体化（MLCP，取消 TIM2）的原因。"
        "本设计因此只把 1100 W 作为保证点。", "risk"))

    s.append(h3("1.4　不在范围内"))
    s.append(F2.fig_hierarchy())
    s.append('<p class="figcap"><strong>图 1-1</strong>　系统层级与设计边界。'
             '本报告只设计最右一格。</p>')
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch2_chip():
    s = ['<section id="chip">']
    s.append(h2("2.", "GB300 / B300 芯片规格数据", "chip"))
    s.append(lead(
        "冷板要对的不是“一块 1100 W 的铜盖”，而是"
        "<strong>两颗 reticle 级计算 die + 八组 HBM3E 堆叠</strong>。"
        "本章把能查到的官方数据和必须假设的数据严格分开："
        f"{HI} 为 NVIDIA / Lenovo 官方公开原文，{MI} 为公开资料或合理工程估算，"
        f"{LO} 为本设计假设，不得写入合同。"))

    s.append(h3("2.1　B300（Blackwell Ultra）芯片级规格"))
    s.append(table(
        ["项目", "官方值", "对冷板设计的含义", "置信度"],
        [
            "硅与封装",
            ["架构 / 工艺", "Blackwell Ultra；TSMC 4NP",
             "与 B200 同代硅，功率与 HBM 容量加码", HI],
            ["晶体管数", "2080 亿（208B）", "双 reticle 才能放下", HI],
            ["计算裸片", "<strong>2 颗 reticle 级 die</strong>，"
             "NV-HBI 10 TB/s 互联，对 CUDA 仍是一颗 GPU",
             "<strong>两个主热点</strong>，各需一套独立射流阵列；"
             "中间 die-to-die 缝不应正对密集射流", HI],
            ["SM / GPC", "最多 160 SM、8 GPC（SKU 可少）",
             "热图随 SM 开启数变化，喷嘴密度应随 power map 单调增加", HI],
            ["Tensor Core", "640 个第五代；TMEM 256 KB/SM",
             "决定瞬态功率斜率，影响热惯量与失冷窗口", HI],
            "存储",
            ["HBM 容量", "288 GB HBM3E（数据手册另有 279 GB 口径）",
             "容量口径差不影响冷板几何；但 HBM 必须被冷板完整盖住", HI],
            ["HBM 带宽", "8 TB/s（Lenovo 该页写 7.7 TB/s）",
             "带宽越高 HBM 自身功耗越高，次热点不可忽略", HI],
            ["HBM 配置", "<strong>8 组 12-Hi 堆叠</strong>；"
             "16 × 512-bit 控制器（合计 8192-bit）",
             "<strong>八个次热点</strong>，决定冷板 HBM 区布置；"
             "见 §2.3 口径辨析", HI],
            "互联与形态",
            ["NVLink", "第五代，1.8 TB/s 双向（18 链 × 100 GB/s）",
             "桥与 I/O 在封装边缘，冷板开孔与压装须避开", HI],
            ["NVLink-C2C", "900 GB/s（对 Grace CPU 一致性互联）",
             "决定超级芯片拓扑，不直接影响单板冷板", HI],
            ["主机接口", "PCIe Gen6 ×16", "同上", HI],
            ["形态", "SXM 模块，数据中心液冷；无消费级 PCIe 卡",
             "必须 D2C 冷板，风冷不在范围", HI],
            "功率",
            ["最大 TGP", "<strong>configurable up to 1400 W</strong>",
             "本设计 DP-B 包络", HI],
            ["整机 SKU TGP", "<strong>1100 W</strong>（Lenovo SXM DLC）",
             "本设计 DP-A 保证点", HI],
        ], widths=["16%", "30%", "40%", "14%"]))

    s.append(h3("2.2　GB300 NVL72 机柜级规格（约束来源）"))
    s.append(table(
        ["项目", "官方值", "对冷板的含义", "置信度"],
        [
            ["配置", "72× Blackwell Ultra GPU + 36× Grace CPU，全液冷机柜",
             "18 个计算托盘，每托盘 4× B300 → 本冷板 72 块/柜", HI],
            ["超级芯片", "1× Grace + 2× B300，NVLink-C2C；"
             "1 TB 统一内存（HBM3E + LPDDR5X）",
             "Grace 用独立冷板，不与 B300 共一块铜", HI],
            ["CPU 核", "2592 个 Arm Neoverse V2", "不在本供货", HI],
            ["GPU 内存 / 带宽", "20 TB / 最高 576 TB/s（整柜）", "—", HI],
            ["快速内存", "37 TB（整柜）", "—", HI],
            ["NVLink 带宽", "130 TB/s（整柜聚合）", "—", HI],
            ["算力", "FP4 1440 PFLOPS（稀疏）/ 1080 PFLOPS（稠密）；"
             "1.44 exaFLOPS",
             "算力密度是液冷的根本驱动，不直接进冷板计算", HI],
            ["机柜热负荷", "135 kW TDP / 155 kW EDP",
             "约 90% 由液冷带走 → 单板热负荷来源", MI],
            ["机柜水力表", "进液 25–45 °C ↔ 59–177 L/min；"
             "系统压降 16–127 kPa",
             "<strong>整柜口径</strong>，不是单板保证值", MI],
            ["网络", "ConnectX-8 SuperNIC 800 Gb/s", "不在本供货", HI],
        ], widths=["16%", "30%", "40%", "14%"]))

    s.append(h3("2.3　口径辨析：HBM 堆叠是 8 组还是 12 组"))
    s.append(p(
        "NVIDIA 技术博客正文写“Eight 12-Hi stacks”，"
        "但该文末尾的更正声明写“corrected … to show the proper 12 HBM stacks "
        "instead of 8”。两处字面冲突，而这个数直接决定冷板 HBM 区的布置，"
        "必须用电气与容量两条独立线索交叉校核："))
    s.append(table(
        ["校核线索", "若为 8 组 12-Hi", "若为 12 组", "判据"],
        [
            ["总接口宽度", "HBM3E 每堆 1024-bit × 8 = "
             "<strong>8192-bit</strong>，与官方“16×512-bit 控制器"
             "（8192-bit total）”<strong>完全吻合</strong>",
             "12 × 1024 = 12288-bit，与官方 8192-bit <strong>矛盾</strong>",
             "<strong>支持 8 组</strong>"],
            ["容量闭合", "8 × 36 GB（12-Hi × 3 GB）= "
             "<strong>288 GB</strong>，闭合",
             "12 × 24 GB（12-Hi × 2 GB）= 288 GB，也能闭合",
             "两者皆可，不能判别"],
            ["同代对比", "B200 为 8 组 HBM3E，B300 沿用封装骨架、换 12-Hi 堆叠",
             "需要重新设计基板与控制器数量", "支持 8 组"],
        ]))
    s.append(note(
        "<strong>本设计判定：按 8 组 12-Hi 布置</strong>。"
        "更正声明最可能的原意是“12-Hi（12 层高）而非 8-Hi”，"
        "被写成了“12 stacks instead of 8”。电气宽度 8192-bit 是硬证据，"
        "它只能对应 8 组 HBM3E。"
        "<strong>但这是一个带风险的判定</strong>：已登记为开放项 C-02，"
        "若 OEM 封装图确认为 12 组，则 §8 的 HBM 区坐标、隔离肋长度与 "
        "HBM 支路通道数必须重画（GPU 射流区不受影响）。", "risk"))

    s.append(h3("2.4　功率两档与热包络"))
    s.append(table(
        ["参数", "DP-A（保证点）", "DP-B（包络）", "来源"],
        [
            ["芯片功率 P", f"<strong>{A['P']:.0f} W</strong>",
             f"<strong>{B['P']:.0f} W</strong>",
             "Lenovo SXM DLC TGP / NVIDIA 最大 TGP"],
            ["设计进液温度", f"{A['Tin']:.0f} °C（计算基准）",
             "25–45 °C（OEM 表）", "GB300 机柜表"],
            ["设计流量（水）", f"{A['Q']:.1f} L/min",
             f"{B['Q']:.1f} L/min", f"本设计候选，{FR}"],
            ["结温包络 T<sub>j</sub>", "83–90 °C", "同左",
             f"厂商常见口径，{MI}"],
            ["热阻目标", f"&lt; {A['target']} °C/W",
             f"&lt; {B['target']} °C/W", "§1.3 倒推"],
        ]))
    s.append(note(
        "两档<strong>不得相加，也不得混成一个数</strong>。"
        "1400 W 是可配置上限，不是本冷板的出厂保证点；"
        "把 1400 写成保证值会在 FAT 时无法交付。"
        "同样，禁止把 ASHRAE W45 的 45 °C 直接当成机柜进液保证，"
        "也禁止用厂商宣传的“单 GPU 2400 W”当基线。", "risk"))

    s.append(h3("2.5　热源分区（设计假设，须官方热图冻结）"))
    s.append(p(
        "NVIDIA 未公开 B300 封装外形与 die 坐标。以下取值按同代双 die 量级设定，"
        f"全部标 {LO}。功率拆分比例是本设计的<strong>假设</strong>，"
        "不是官方 power map。"))
    s.append(table(
        ["对象", "几何假设", f"DP-A 功率", f"DP-B 功率", "热流密度（DP-A）",
         "设计含义"],
        [
            ["单计算 die", f"{G['die_w']:.0f} × {G['die_h']:.0f} mm "
             f"（{M.A_DIE*1e4:.2f} cm²）",
             f"{A['p_die']:.0f} W（39%）", f"{B['p_die']:.0f} W",
             f"面均 {A['q_die']:.1f} W/cm²<br>热点估 "
             f"{A['q_die']*2.5:.0f} W/cm²",
             "射流阵列主目标"],
            ["NV-HBI 缝", f"{G['hbi']:.0f} mm 宽", "低", "低", "低",
             "不对缝打密集射流"],
            ["单颗 HBM 堆", f"{G['hbm_w']:.0f} × {G['hbm_h']:.0f} mm "
             f"（{M.A_HBM*1e4:.2f} cm²）",
             f"{A['p_hbm']:.1f} W（合计 18%）", f"{B['p_hbm']:.1f} W",
             f"面均 {A['q_hbm']:.1f} W/cm²",
             "只需盖住 + 均温，禁射流"],
            ["I/O 与其它", "封装边缘", f"{A['p_other']:.0f} W（4%）",
             f"{B['p_other']:.0f} W", "低", "靠铜扩热"],
            ["冷板作用面积", f"{G['plate_L']:.0f} × {G['plate_W']:.0f} mm "
             f"（{M.A_PLATE*1e4:.1f} cm²）", "—", "—",
             f"板均 {A['q_plate']:.1f} W/cm²",
             "用 footprint 平均会严重低估 die"],
        ], widths=["13%", "18%", "15%", "12%", "20%", "22%"]))
    s.append(F2.fig_energy())
    s.append('<p class="figcap"><strong>图 2-1</strong>　'
             f'能量分流校核：{A["p_die"]:.0f}+{A["p_die"]:.0f}+'
             f'{A["p_hbm"]*8:.0f}+{A["p_other"]:.0f} = {A["P"]:.0f} W。'
             '这是功率去向，不是流量去向。</p>')
    s.append(note(
        "<strong>不要用 500–600 W/cm² 当整板平均。</strong>"
        "那类数字是按 1.5–2 cm² 活性核反推的热点上限。"
        f"本设计按 die 面平均（{A['q_die']:.1f} W/cm²）加 2.5 倍热点系数"
        f"（{A['q_die']*2.5:.0f} W/cm²）校核射流区，"
        "并在 CFD 中用真实热图替换该系数。"))
    s.append(imgfig(
        "assets/src/gb200_fig1_layout_heatflux.jpg", "图 2-2",
        "多芯片非均匀热图（GB200 模组，作类比）",
        "2×GPU + CPU 的 footprint 平均只有 35–40 W/cm²，而 die 面平均高得多。"
        "B300 单封装没有 Grace，但仍是双 die + HBM 的强非均匀热源，"
        "<strong>不能用一条等宽长槽通铺</strong>。"
        "来源：arXiv:2604.10941, Fig. 1。"))
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch3_inputs():
    s = ['<section id="inputs">']
    s.append(h2("3.", "设计输入", "inputs"))
    s.append(lead(
        "设计输入是<strong>可追溯的外部约束</strong>，与设计输出严格区分。"
        "每条输入标明来源、状态和一旦变化会影响哪一章 —— "
        "这样输入变更时可以定位返工范围，而不是全文重做。"))

    s.append(h3("3.1　输入追溯矩阵"))
    s.append(table(
        ["编号", "输入项", "取值 / 内容", "来源", "状态", "影响章节"],
        [
            "热输入",
            ["IN-T1", "保证点功率", f"{A['P']:.0f} W",
             "Lenovo Press LP2357（B300 SXM DLC TGP）",
             '<span class="good">已冻结</span>', "全篇"],
            ["IN-T2", "包络功率", f"{B['P']:.0f} W",
             "NVIDIA Blackwell Ultra 博客 / 数据手册",
             '<span class="good">已冻结</span>', "§5, §9, §10"],
            ["IN-T3", "结温包络", "83–90 °C",
             "厂商常见口径", '<span class="warn2">待确认</span>',
             "§1.3, §9.7"],
            ["IN-T4", "官方 power map（两 die + HBM 分布）", "未获得",
             "NVIDIA / OEM", '<span class="bad">缺失</span>',
             "§2.5, §5.2, §10.6"],
            ["IN-T5", "封装内热阻 R<sub>pkg</sub>",
             f"{M.R_PKG[0]}–{M.R_PKG[1]} °C/W",
             "工程估算", '<span class="warn2">估算</span>', "§1.3, §9.7"],
            ["IN-T6", "TIM2 面积热阻", "0.1–0.2 °C·cm²/W",
             "OCP / Meta 公开资料", '<span class="warn2">估算</span>',
             "§9.7"],
            "水力输入",
            ["IN-H1", "机柜进液温度窗", "25–45 °C",
             "GB300 机柜表 / Lenovo Table 27",
             '<span class="good">已冻结</span>', "§9, §10.7"],
            ["IN-H2", "整柜流量", "59–177 L/min（随温度）",
             "同上", '<span class="good">已冻结</span>', "§7.1"],
            ["IN-H3", "整柜系统压降", "16–127 kPa",
             "同上", '<span class="good">已冻结</span>', "§7.1"],
            ["IN-H4", "单板额定流量与压降窗", "未获得（本设计取 "
             f"{A['Q']:.1f} L/min）", "托盘分流计算 + 订单 ICD",
             '<span class="bad">缺失</span>', "§5.5, §9"],
            ["IN-H5", "工质", "DI 水（基线）/ PG25（校核）",
             "与 GB300 总体设计一致",
             '<span class="warn2">待商务确认</span>', "§9.9"],
            ["IN-H6", "系统过滤等级", "投运 ≤ 25 μm",
             "系统侧要求", '<span class="warn2">待确认</span>',
             "§6.7, §12"],
            "机械与接口输入",
            ["IN-M1", "封装外形、螺钉位、TIM 窗、die/HBM 坐标", "未获得",
             "OEM 封装图 / SXM ICD", '<span class="bad">缺失</span>',
             "§6, §8"],
            ["IN-M2", "压装力与加载方式", "未获得（估 300–500 N）",
             "订单 ICD", '<span class="bad">缺失</span>', "§6.4"],
            ["IN-M3", "UQD 型号与水嘴方向", "跟托盘，不自创口径",
             "订单 ICD", '<span class="bad">缺失</span>', "§6.6, §7.1"],
            ["IN-M4", "托盘空间包络与相邻件", "未获得",
             "OEM", '<span class="bad">缺失</span>', "§8.2"],
            ["IN-M5", "四板并联拓扑", "并联，禁止串联",
             "GB300 总体设计", '<span class="good">已冻结</span>', "§7.1"],
            "上游文件继承",
            ["IN-R1", "《GB300 NVL72 冷却系统总体设计报告 v2.2》",
             "整柜 135/155 kW、约 90/10 液风分担、机柜水力表",
             "本仓库", '<span class="good">已冻结</span>', "§2.2, §7.1"],
            ["IN-R2", "《AI 算力芯片液冷冷板专利分析报告 v1.4》",
             "方案 A 权项结构（GPU 射流 / HBM 禁射流 / 隔离肋 / 压降窗）、"
             "工艺三分流", "同目录", '<span class="good">已冻结</span>',
             "§5.1, §6.1"],
            ["IN-R3", "《AI 算力芯片液冷冷板技术调查分析报告 v1.3》",
             "射流三区、H/D 与 S/D 窗、微通道强化综述",
             "同目录", '<span class="good">已冻结</span>', "§5.4, §9.4"],
        ], widths=["7%", "22%", "24%", "19%", "12%", "16%"]))

    s.append(h3("3.2　工质物性（计算基准）"))
    s.append(table(
        ["工质", "温度", "ρ / kg·m⁻³", "c<sub>p</sub> / J·kg⁻¹K⁻¹",
         "μ / Pa·s", "k / W·m⁻¹K⁻¹", "Pr", "用途"],
        [
            [M.WATER40.name.split()[0] + " DI", "40 °C",
             f"{M.WATER40.rho:.1f}", f"{M.WATER40.cp:.0f}",
             f"{M.WATER40.mu:.3e}", f"{M.WATER40.k:.3f}",
             f"{M.WATER40.Pr:.2f}", "<strong>设计基准</strong>"],
            ["PG25（25% 丙二醇）", "40 °C",
             f"{M.PG25_40.rho:.1f}", f"{M.PG25_40.cp:.0f}",
             f"{M.PG25_40.mu:.3e}", f"{M.PG25_40.k:.3f}",
             f"{M.PG25_40.Pr:.2f}", "校核，见 §9.9"],
        ]))
    s.append(note(
        f"PG25 的 Pr 是水的 {M.PG25_40.Pr/M.WATER40.Pr:.1f} 倍，"
        f"导热率只有水的 {M.PG25_40.k/M.WATER40.k*100:.0f}%，"
        f"动力粘度是水的 {M.PG25_40.mu/M.WATER40.mu:.2f} 倍。"
        "这三项共同决定了 §9.9 中约 29% 的换热损失 —— "
        "不是经验拍的 15%。"))

    s.append(h3("3.3　假设登记册"))
    s.append(p(
        "以下每条都是<strong>设计假设</strong>，不是事实。"
        "登记的意义是：评审时逐条质询，输入到位后逐条替换。"))
    s.append(table(
        ["编号", "假设", "取值", "若假设错误的后果", "替换条件"],
        [
            ["AS-1", "两 die 合计占 78% 功率", "各 39%",
             "射流阵列功率密度设计偏差；两 die 温差判据失效",
             "官方 power map"],
            ["AS-2", "HBM 合计占 18%", "单颗 "
             f"{A['p_hbm']:.1f} W", "HBM 支路 20% 流量分配可能不足或浪费",
             "官方 power map"],
            ["AS-3", "HBM 为 8 组", "左右各 4 颗",
             "<strong>HBM 区坐标与隔离肋须重画</strong>（见 §2.3）",
             "OEM 封装图"],
            ["AS-4", "die 尺寸 27×28 mm", f"{M.A_DIE*1e4:.2f} cm²/颗",
             "热流密度与射流阵面尺寸偏差", "OEM 封装图"],
            ["AS-5", "热点系数 2.5×", f"{A['q_die']*2.5:.0f} W/cm²",
             "局部壁温预测偏低，驻点设计不足", "官方热图 / CFD"],
            ["AS-6", "TIM2 面积热阻 0.1–0.2 °C·cm²/W",
             f"{M.R_TIM2[0]}–{M.R_TIM2[1]} °C/W",
             "<strong>直接决定 §9.11 差距闭合可行性</strong>",
             "TIM2 选型 + 实测"],
            ["AS-7", "静压箱/隔墙压降 3–5 kPa", "占板内压降主项",
             "压降预算失真（但余量大，风险低）", "CFD"],
            ["AS-8", "槽内流动拓扑为“就近抽走”", f"L<sub>f</sub> = "
             f"{G['L_flow']:.1f} mm",
             "换热与压降模型选择错误（v1.x 的问题所在）", "CFD 流线"],
        ], widths=["7%", "22%", "15%", "34%", "22%"]))
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch4_process():
    s = ['<section id="process">']
    s.append(h2("4.", "设计流程", "process"))
    s.append(lead(
        "流程的作用是<strong>把“算得对”和“做得出”分开评审</strong>，"
        "并规定什么条件下必须回头改几何。"
        "本报告 v2.0 完成到 ⑥（机械与图纸），"
        "⑤（三维仿真）只给需求规格，工具未选定；⑦（样件试验）未开始。"))
    s.append(F2.fig_process())
    s.append('<p class="figcap"><strong>图 4-1</strong>　'
             '门控设计流程与两条强制迭代回路。</p>')

    s.append(h3("4.1　阶段门与交付物"))
    s.append(table(
        ["门", "名称", "放行条件", "交付物", "本版状态"],
        [
            ["DR0", "输入冻结", "IN-* 矩阵中“缺失”项全部有责任人与计划日期",
             "输入追溯矩阵（§3.1）、假设登记册（§3.3）",
             '<span class="good">已完成</span>（含 6 项缺失，已登记）'],
            ["DR1", "方案选定", "权衡矩阵有量化权重；FTO 初筛无红灯",
             "方案决策矩阵（§5.1）、分区策略（§5.2）",
             '<span class="good">已完成</span>'],
            ["DR2", "性能基线", "热阻预算闭合；一维计算可复算；"
             "敏感性给出杠杆",
             "热阻预算（§5.3）、一维计算书（§9）、脚本 <code>calc/</code>",
             '<span class="warn2">有条件通过</span>（区间跨目标线）'],
            ["DR3", "仿真与图纸", "CFD 网格无关性达标；"
             "R 与 ΔP 落在目标内；图纸尺寸链闭合",
             "CFD 报告、2D/3D/爆炸图（§8）",
             '<span class="bad">未完成</span>（仿真未做）'],
            ["DR4", "送样放行", "首件 TTV 热阻达标；氦检通过；流阻曲线符合",
             "FAT 报告、出厂三曲线",
             '<span class="bad">未开始</span>'],
        ], widths=["7%", "12%", "28%", "28%", "25%"]))

    s.append(h3("4.2　两条强制迭代回路"))
    s.append(table(
        ["回路", "触发条件", "回到哪一步", "可调杠杆（按优先级）"],
        [
            ["R1 仿真回路",
             "CFD 得到的 R<sub>θ,c-in</sub> 超目标，或 ΔP 超 20 kPa，"
             "或分区流量偏差 &gt; ±10%",
             "回 §5 性能设计 / §9 一维计算",
             "① 孔径 0.50→0.40/0.35 mm（见 §9.10）"
             "② TIM2 升级到 ≤0.004 °C/W"
             "③ 流量 2.0→2.2/2.4 L/min"
             "④ 阵列加密到 10×10（须重算压降）"
             "⑤ 槽深 1.5→1.0 mm（减死体积，须重画厚度链）"],
            ["R2 验证回路",
             "TTV 实测与 CFD 偏差 &gt; 15%",
             "回 §5，并修正 §9 的关联式选择与经验系数",
             "① 用实测反标定 h 模型"
             "② 复核 TIM2 装配压力与厚度"
             "③ 复核喷嘴孔一致性与堵塞"],
        ], widths=["12%", "28%", "22%", "38%"]))

    s.append(h3("4.3　变更控制"))
    s.append(ul([
        "<strong>几何冻结原则：</strong>§8 的锁定坐标表是全文唯一几何来源。"
        "任何图、任何计算与该表冲突，以该表为准；修改该表必须升版本号。",
        "<strong>数值单一来源：</strong>本报告所有数值由 "
        "<code>calc/model.py</code> 计算，"
        "<code>calc/cp_b300_1d.py</code> 输出计算书，"
        "<code>calc/build_report.py</code> 生成本文件。"
        "不存在手抄数字，改参数即全文同步。",
        "<strong>输入变更影响分析：</strong>按 §3.1 的“影响章节”列定位返工范围。",
    ]))
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch5_performance():
    s = ['<section id="perf">']
    s.append(h2("5.", "性能设计", "perf"))
    s.append(lead(
        "性能设计回答三个问题：<strong>选什么结构</strong>、"
        "<strong>热阻预算怎么分</strong>、"
        "<strong>射流与流量参数取在哪个窗口</strong>。"
        "详细的公式与逐步数值在 §9，本章只给设计决策与理由。"))

    s.append(h3("5.1　方案选型：为什么是分区杂交"))
    s.append(table(
        ["评价维度", "权重", "纯铲齿微通道", "纯射流平板", "整板增材拓扑",
         "<strong>分区杂交（本方案）</strong>"],
        [
            ["双 die 热点能力", "25%", "3（沿程出口侧先超温）",
             "5（驻点 h 极高）", "4", "<strong>5</strong>（每 die 独立阵列）"],
            ["HBM 安全（冲蚀 / 偏载）", "20%", "3（流速易偏高）",
             "1（高速射流伤堆叠）", "3",
             "<strong>5</strong>（无喷嘴 + 流速帽 + 隔离肋）"],
            ["压降", "15%", "2（长槽高）", "3（孔板集中）", "4",
             "<strong>4</strong>（短槽 + 中等孔速）"],
            ["可制造性 / 交期", "20%", "5（成熟）", "3（三层对位）",
             "1（残粉、导热折损）",
             "<strong>4</strong>（机加 + 钎焊，12–18 个月）"],
            ["可靠性 / 防堵", "10%", "5", "2（孔易堵）", "2",
             "<strong>3</strong>（0.50 mm 孔 + 过滤）"],
            ["专利可占位", "10%", "1（直槽空间窄）", "2（阵列已密）", "3",
             "<strong>5</strong>（HBM 禁射流 + 流速帽 + 隔离肋 + 压降窗）"],
            ["<strong>加权得分</strong>", "100%", "3.20", "2.95", "2.85",
             "<strong>4.50</strong>"],
        ], widths=["20%", "8%", "17%", "15%", "14%", "26%"]))
    s.append(note(
        "选型结论与同目录专利分析报告 v1.4 的<strong>方案 A</strong> 一致："
        "GPU 区射流 + 短微通道，HBM 区仅低速微通道，中间隔离肋。"
        "规避要点：不能只写“分区用射流和微通道”（已被华为 WO2026103052A1 覆盖），"
        "必须把 <strong>HBM 无喷嘴、近壁流速上限、隔离肋的流动/力学双重功能、"
        "额定流量下压降窗</strong> 写成必要技术特征。", "ok"))

    s.append(h3("5.2　分区策略"))
    s.append(table(
        ["", "GPU 射流区（第一区）", "HBM 微通道区（第二区）", "隔离肋"],
        [
            ["对应热源", "2 颗计算 die", "8 组 12-Hi HBM3E", "两区之间"],
            ["热流密度（DP-A）",
             f"die 面均 {A['q_die']:.3f}；"
             f"胞名义 {A['q_cell']:.3f}；"
             f"边界 {A['q_bc']:.3f} W/cm²（×{A['flux_margin']:.2f}）",
             f"面均 {A['q_hbm']:.1f} W/cm²",
             "5% 只在 GPU 胞边界，不改 1100 W"],
            ["喷嘴", f"有，{M.N_JET} 个 ⌀{G['D_jet']:.2f} mm",
             "<strong>无</strong>（权项必要特征）", "—"],
            ["通道", f"{G['ch_w']:.2f} × {G['ch_h']:.2f} mm，"
             f"节距 {G['ch_p']:.2f}，{M.N_CH_DIE} 条/die",
             f"{G['hbm_ch_w']:.2f} × {G['hbm_ch_h']:.2f} mm，"
             f"{G['n_hbm_ch']} 条", f"实心铜，宽 {G['rib']:.1f} mm"],
            ["水力直径", f"{M.DH_CH*1e3:.3f} mm",
             f"{M.DH_HBM*1e3:.3f} mm（更大，用于降速）", "—"],
            ["流量分配（DP-A）", f"<strong>{A['Qg']:.2f} L/min（80%）</strong>",
             f"<strong>{A['hbm']['Q_lpm']:.2f} L/min（20%）</strong>", "0"],
            ["特征速度", f"孔速 {A['jet']['V']:.3f} m/s",
             f"近壁 {A['hbm']['V']:.3f} m/s（帽 {G['V_cap_hbm']:.2f}）", "—"],
            ["设计意图", "把热点边界层打断，就地抽走废液，抑制交叉流",
             "盖住、均温、低剪切、不冲蚀焊球与堆叠",
             "切断串流；压装时把载荷传到边框，减轻 HBM 偏载"],
        ], widths=["16%", "30%", "30%", "24%"]))
    s.append(p(
        "为什么 80/20 而不是按面积或按功率平分："
        "HBM 只占 18% 功率且热流低一个量级，"
        "多送水只会抬压降与冲蚀风险，对结温没有帮助；"
        "GPU 需要高 h，必须把大部分质量流量送到驻点。"
        "分配靠<strong>盖板开孔面积与隔墙</strong>实现，"
        "不用外置调节阀，样件用分区流量计标定。"))

    s.append(h3("5.3　热阻预算分配"))
    s.append(F2.fig_rnetwork())
    s.append('<p class="figcap"><strong>图 5-1</strong>　'
             '结–进液热阻网络。冷板只拥有 TIM2 以下三段。</p>')
    s.append(table(
        ["环节", "DP-A 分配 / °C/W", "占比（保守端）", "可控性", "说明"],
        [
            ["硅扩散 + TIM1 + 封装盖", f"{M.R_PKG[0]}–{M.R_PKG[1]}",
             "—（在壳温之上）", "不可控",
             "NVIDIA 封装决定；只有 MLCP 才能动"],
            ["TIM2", f"{M.R_TIM2[0]}–{M.R_TIM2[1]}",
             f"{M.R_TIM2[1]/A['R_hi']*100:.0f}%", "选型可控",
             "面积热阻 0.1–0.2 °C·cm²/W ÷ 有效面积；"
             "<strong>保守端占掉近 1/4 预算</strong>"],
            ["铜壁导热（余铜 2.0 mm）", f"{M.R_WALL:.4f}",
             f"{M.R_WALL/A['R_hi']*100:.0f}%", "几何可控",
             "一维导热，按两 die 投影面积"],
            ["对流（射流 + 短槽）",
             f"<strong>{A['con']['R']:.4f}</strong>",
             f"{A['con']['R']/A['R_hi']*100:.0f}%", "<strong>主攻</strong>",
             "Martin 因 Re&lt;2000 不采用；只保留短槽模型，216 胞并联"],
            ["<strong>合计 壳–进液</strong>",
             f"<strong>{A['R_lo']:.4f}–{A['R_hi']:.4f}</strong>", "100%",
             "—", f"目标 &lt; {A['target']}"],
        ], widths=["24%", "18%", "12%", "12%", "34%"]))
    s.append(F2.fig_rchain_bar())
    s.append('<p class="figcap"><strong>图 5-2</strong>　'
             '四种组合下的热阻堆叠与目标线。虚线为目标，'
             '保守模型两档均越线。</p>')

    s.append(h3("5.4　射流参数设计窗"))
    s.append(table(
        ["参数", "符号", "本设计取值", "文献 / 关联式窗", "是否在窗内", "理由"],
        [
            ["孔径", "D", f"{G['D_jet']:.2f} mm", "0.3–1.0 mm（可微钻）",
             '<span class="good">是</span>',
             "可微钻、堵塞风险可接受、过滤要求合理"],
            ["无量纲喷距", "H/D", f"{M.HD:.1f}", "2–6",
             '<span class="good">是</span>',
             "过近势核未展开，过远到达速度衰减"],
            ["无量纲孔距", "Sx/D · Sy/D",
             f"{M.SD_X:.1f} · {M.SD_Y:.1f}", "4–8",
             '<span class="good">是</span>',
             "过密射流互扰，过疏覆盖不足"],
            ["相对喷嘴面积", "f", f"{M.F_AREA:.5f}", "0.004–0.04（Martin）",
             '<span class="good">是</span>', "落在关联式有效域"],
            ["孔雷诺数", "Re<sub>D</sub>", f"{A['jet']['Re']:.0f}",
             "≥ 2000（Martin 有效域）",
             '<span class="bad">否，外推</span>',
             "<strong>本设计最大不确定来源</strong>，见 §9.4"],
            ["槽内流程", "L<sub>f</sub>", f"{G['L_flow']:.1f} mm"
             f"（上限 {G['L_flow_max']:.0f}）", "越短越抑交叉流",
             '<span class="good">是</span>',
             f"把“一条河”拆成 {M.N_JET} 个小循环"],
        ], widths=["14%", "10%", "16%", "20%", "14%", "26%"]))
    s.append(F2.fig_jet_mechanism())
    s.append('<p class="figcap"><strong>图 5-3</strong>　'
             '冲击射流三区与本设计的无量纲取值窗。'
             'Re<sub>D</sub> 落在窗外，必须由 CFD 校正。</p>')
    s.append('<div class="papergrid">')
    s.append(imgfig(
        "assets/src/hussain_fig1_jet_regions.jpg", "图 5-4",
        "论文原图 · 射流三区",
        "自由射流、驻点、壁面射流。本设计 H/D=4 落在驻点核完整、"
        "交叉流尚未主导的窗口。来源：Hussain et al., Energies 2021, Fig. 1。"))
    s.append(imgfig(
        "assets/src/hussain_fig7_HD.jpg", "图 5-5",
        "论文原图 · H/D 对换热的影响",
        "过近则势核未展开，过远则到达速度衰减。本设计取 4，不取 2 或 8。"
        "来源：Hussain et al., Energies 2021, Fig. 7。"))
    s.append("</div>")
    s.append(note(
        "<strong>为什么短槽必须短：</strong>若改成贯穿 28 mm 的长槽，"
        "下游孔看到的是上游废液，交叉流把驻点核推离 die 中心，"
        "两 die 温差与单 die 内部温差会一起坏。"
        f"短槽把每条流程截在 {G['L_flow_max']:.0f} mm 以内，"
        f"等于把一条河拆成 {M.N_JET} 个独立小循环。", "ok"))

    s.append(h3("5.5　流量与压降预算"))
    s.append(table(
        ["项", "DP-A", "DP-B", "说明"],
        [
            ["总流量（水）", f"{A['Q']:.1f} L/min", f"{B['Q']:.1f} L/min",
             f"候选值，{FR}；比流量 "
             f"{A['Q']/(A['P']/1000):.2f} L/min·kW⁻¹"],
            ["GPU 支路", f"{A['Qg']:.2f} L/min", f"{B['Qg']:.2f} L/min",
             f"80% 是流量份额，由 {M.N_JET} 孔总面积 "
             f"{M.A_JET*1e6:.2f} mm² 限流"],
            ["HBM 支路", f"{A['hbm']['Q_lpm']:.2f} L/min",
             f"{B['hbm']['Q_lpm']:.2f} L/min", "20%，独立进液缝 + 宽槽"],
            ["流体温升", f"{A['dTf']:.2f} K", f"{B['dTf']:.2f} K",
             "0 维能量平衡，<strong>不可反推流量</strong>"],
            ["板内压降（实算）",
             f"{A['dp']['total'][0]/1000:.1f}–"
             f"{A['dp']['total'][1]/1000:.1f} kPa",
             f"{B['dp']['total'][0]/1000:.1f}–"
             f"{B['dp']['total'][1]/1000:.1f} kPa",
             f"目标 ≤{G['dP_target']:.0f}，上限 {G['dP_limit']:.0f}"],
            ["一对 UQD（参考）", "4–8 kPa", "同左",
             "是否计入 20 kPa 窗须在 ICD 声明"],
        ]))
    s.append(note(
        "<strong>流量不是用 10 K 反推出来的。</strong>"
        "1.0–1.5 L/min·kW⁻¹ 只是行业初筛区间。"
        f"本设计取 {A['Q']:.1f} L/min（约 "
        f"{A['Q']/(A['P']/1000):.2f} L/min·kW⁻¹），"
        f"理由是：① 要维持 {M.N_JET} 个孔的孔速与驻点换热；"
        "② 给 PG25 与脏污留裕量。"
        "机柜侧仍服从整柜表，单板流量由托盘孔板决定，SAT 必须实测。", "risk"))
    s.append("</section>")
    return "".join(s)

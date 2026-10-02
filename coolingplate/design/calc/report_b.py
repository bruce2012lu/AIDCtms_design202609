# -*- coding: utf-8 -*-
"""报告章节 6–14：机械设计、原理图、详细设计图纸、一维计算、
三维仿真需求、试验验收、风险、开放项、来源、附录。"""
import model as M
import figures as FG
import figures2 as F2
from rhtml import (h2, h3, h4, p, lead, note, ul, ol, table, cards, fig,
                   imgfig, formula, CONF)

A = M.solve("DP-A")
B = M.solve("DP-B")
AP = M.solve("DP-A", M.PG25_40)
BP = M.solve("DP-B", M.PG25_40)
G = M.GEO
MC = M.mech_checks()
SW = M.orifice_sweep()
HI, MI, LO, FR = CONF["H"], CONF["M"], CONF["L"], CONF["F"]


# ============================================================
def ch6_mech():
    s = ['<section id="mech">']
    s.append(h2("6.", "机械设计", "mech"))
    s.append(lead(
        "机械设计要同时满足四件事：<strong>导热</strong>（余铜足够厚）、"
        "<strong>刚度</strong>（压装不塌、承压不鼓）、"
        "<strong>可制造</strong>（槽宽与孔径在机加能力内）、"
        "<strong>可密封</strong>（钎料不流进 0.40 mm 槽）。"
        "这四件事互相拉扯，厚度链是它们的交汇点。"))

    s.append(h3("6.1　材料选型"))
    s.append(table(
        ["零件", "材料", "关键性能", "选择理由", "备选"],
        [
            ["换热底板 JM01-100", "C110 / C1020 紫铜",
             "k ≈ 390 W·m⁻¹K⁻¹；退火态屈服 ≈ 70 MPa",
             "导热最优；铲齿/CNC 工艺成熟；与钎焊相容", "C102（含氧低）"],
            ["喷嘴盖板 JM01-200", "同铜",
             "同上",
             "与底板同材，避免钎焊热膨胀失配；微钻 0.50 mm 可行",
             "无（异种材料会引入 CTE 失配）"],
            ["钎料框 JM01-400", "Ag 基或 Cu-P 钎料",
             "熔点 &lt; 铜；润湿可控",
             "真空钎焊工艺成熟；框形结构限制钎料流动路径", "扩散焊（无钎料）"],
            ["进出水嘴 JM01-310/320", "铜或不锈钢",
             "与 UQD 配合",
             f"跟托盘 UQD，不自创口径，{FR}", "—"],
            ["接触面镀层", "可选化学镀 Ni",
             "3–8 μm",
             "防氧化、改善与 TIM2 的浸润；<strong>不得进流道</strong>", "无镀层"],
        ], widths=["18%", "16%", "20%", "30%", "16%"]))
    s.append(note(
        "<strong>不采用整板金属增材（LPBF）作为出货基线。</strong>"
        f"残粉对 ⌀{G['D_jet']:.2f} mm 孔不可接受，"
        "且致密度不足会折损导热率。增材只允许用于喷嘴盖板的"
        "<strong>验证件</strong>，密封面仍须机加。"))

    s.append(h3("6.2　层叠结构与厚度链"))
    s.append(table(
        ["层", "厚度 / mm", "功能", "工艺", "厚度取值理由"],
        [
            ["进液盖 / 喷嘴板", f"{G['t_lid']:.1f}",
             f"静压箱 + {M.N_JET} 个喷嘴 + 回液缝；HBM 区无喷嘴",
             "微钻或蚀刻；密封面精铣",
             "孔长/孔径 = 5，保证射流出口方向稳定；<br>"
             "太薄则孔难加工且刚度不足"],
            ["射流间隙 H", f"{G['H_jet']:.1f}",
             "自由射流段", "由盖板与肋顶间距形成",
             f"H/D = {M.HD:.1f}，落在 2–6 窗内"],
            ["换热槽层", f"{G['ch_h']:.1f}",
             "GPU 短槽 + HBM 宽槽 + 隔离肋", "铲齿或 CNC",
             f"肋效率 {A['con']['eta']:.3f}（仍 &gt;0.9）；<br>"
             "<strong>偏厚，存在优化空间</strong>，见下方注"],
            ["接触面余铜", f"{G['base_cu']:.1f}",
             "扩热、刚度、防铣穿", "与底板一体",
             f"一维热阻仅 {M.R_WALL:.4f} °C/W；<br>"
             "同时满足平面度 0.05 与防穿透"],
            ["<strong>腔体小计</strong>",
             f"<strong>{G['t_lid']+G['H_jet']+G['ch_h']+G['base_cu']:.1f}"
             f"</strong>", "—", "—", "四层相加"],
            ["周边钎缝 / 水嘴台阶", f"{G['t_braze']:.1f}", "封接",
             "钎焊", "工艺余量"],
            ["<strong>外形总厚</strong>",
             f"<strong>{G['plate_T']:.1f}</strong>", "—", "—",
             "不含 UQD"],
        ], widths=["17%", "10%", "24%", "16%", "33%"]))
    s.append(note(
        "<strong>已识别的优化项（登记为 OPT-1）：</strong>"
        "按真实“就近抽走”拓扑，槽内流速只有 "
        f"{A['ch']['V']:.3f} m/s，说明 {G['ch_h']:.1f} mm 槽深对这个流量"
        "<strong>明显过大</strong>，下部存在低速死体积。"
        "把槽深减到 0.8–1.0 mm 可以缩短导热路径并减重，"
        "但会改变厚度链与全套图纸。"
        "本版<strong>保留 1.5 mm 作为冻结基线</strong>（图纸自洽优先），"
        "槽深优化交由 CFD 在 DR3 一并判定。", "risk"))

    s.append(h3("6.3　承压与变形校核"))
    s.append(p(
        f"模型：两端固支板条，试验压力 {MC['p_test']/1e5:.0f} bar（表压）。"
        "σ = p·L²/(2t²)，挠度 w = p·L⁴/(32·E·t³)，"
        f"铜屈服强度保守取 {MC['sy']/1e6:.0f} MPa（退火态）。"))
    s.append(table(
        ["校核工况", "弯曲应力 σ / MPa", "挠度 / μm", "安全系数", "判定"],
        [[nm, f"{s_/1e6:.2f}", f"{w_*1e6:.2f}", f"{n_:,.0f}",
          '<span class="good">通过</span>' if n_ > 3 else
          '<span class="bad">复核</span>']
         for nm, s_, w_, n_ in MC["cases"]]))
    s.append(note(
        "三个工况的安全系数都在数百到数万量级，"
        "<strong>承压不是本设计的约束</strong>。"
        "真正的机械风险是<strong>压装偏载传到 HBM 焊球</strong>"
        "和<strong>焊后平面度</strong>，"
        "这两项由隔离肋布置与焊后精铣控制，不能靠应力计算证明，"
        "必须靠首件三坐标与红外验证。", "ok"))

    s.append(h3("6.4　压装与载荷路径"))
    s.append(ul([
        f"<strong>隔离肋参与承载：</strong>宽 {G['rib']:.1f} mm，"
        "与封装加强环对位，把压装力从 GPU 区传到边框，"
        "使 HBM 区压强低于 GPU 区。",
        "<strong>压装力：</strong>估 300–500 N（待 ICD，IN-M2）。"
        "加载点为四角 ⌀3.4 沉孔，须配弹性元件保证 TIM2 厚度稳定。",
        "<strong>TIM2 装配窗：</strong>冷板不规定 TIM2 品牌，"
        "但必须在 ICD 中约定装配压力与目标厚度 —— "
        f"TIM2 在保守端占掉 {M.R_TIM2[1]/A['R_hi']*100:.0f}% 的热阻预算，"
        "是最敏感的装配变量。",
        "<strong>禁止：</strong>把压装力全部经由薄盖板传递；"
        "盖板只封流道，不做主承载件。",
    ]))

    s.append(h3("6.5　公差与形位公差"))
    s.append(table(
        ["部位", "尺寸 / 公差", "形位公差", "检测手段", "理由"],
        [
            ["接触面（与封装盖贴合）", "—",
             "平面度 <strong>0.05 mm</strong>；Ra ≤ 0.8 μm",
             "三坐标 / 平晶 / 轮廓仪",
             "直接决定 TIM2 厚度与接触热阻"],
            ["GPU 短槽宽", f"{G['ch_w']:.2f} ±0.03 mm", "—",
             "影像测量", "偏差影响流量分配与肋效率"],
            ["喷嘴孔径", f"⌀{G['D_jet']:.2f} +0.03 / 0 mm",
             "轴线垂直度 0.05", "针规 / 影像",
             "孔径散差直接造成射流不均"],
            ["喷嘴阵与 die 对位", "±0.20 mm",
             "位置度 ⌀0.4（MMC）", "焊后 X-ray / 工装定位",
             "驻点必须对准 die 中心，偏了就出现冷斑错位"],
            ["射流间隙 H", f"{G['H_jet']:.1f} ±0.10 mm", "平行度 0.05",
             "焊后剖切抽检", "H/D 直接影响驻点 h"],
            ["外形", f"{G['plate_L']:.0f}×{G['plate_W']:.0f} ±0.15 mm",
             "—", "卡尺 / 三坐标", "托盘装配"],
            ["总厚", f"{G['plate_T']:.1f} ±0.10 mm", "—", "千分尺",
             "压装行程"],
        ], widths=["22%", "20%", "20%", "18%", "20%"]))

    s.append(h3("6.6　工艺路线与封合"))
    s.append(table(
        ["工序", "内容", "关键控制点"],
        [
            ["1 底板开流道", "铲齿或 CNC 铣 GPU 短槽 + HBM 宽槽 + 隔离肋",
             f"槽宽 ±0.03；不得铣穿余铜（留 {G['base_cu']:.1f} mm）"],
            ["2 盖板加工", f"微钻 {M.N_JET} × ⌀{G['D_jet']:.2f} mm + "
             "回液缝 + 静压箱腔",
             "孔无毛刺、不堵；孔位 ±0.10"],
            ["3 清洗", "超声 + 去离子冲洗 + 烘干",
             f"颗粒 ≤ 孔径 1/10（{G['D_jet']*100:.0f} μm）"],
            ["4 铺钎料框", "空心框形，不是整层铺",
             "<strong>钎料不得流入 0.40 mm 槽</strong>"],
            ["5 对位与夹具", "盖板与底板对位 ±0.20", "工装定位销，不靠目视"],
            ["6 真空钎焊", "首选真空钎焊；备选扩散焊",
             "温度曲线；防塌陷（细肋支撑）"],
            ["7 接触面精铣", "焊后加工", "平面度 0.05；Ra ≤0.8"],
            ["8 水嘴装配", "钎焊或一体", "跟 UQD 口径"],
            ["9 检漏", "100% 氦质谱检漏 + 保压",
             f"{MC['p_test']/1e5:.0f} bar 保压"],
            ["10 出厂测试", "流量–压降曲线、TTV 热阻、红外",
             "三条曲线随件出厂"],
        ], widths=["14%", "44%", "42%"]))
    s.append('<div class="papergrid">')
    s.append(imgfig(
        "assets/principle-skived-fin.png", "图 6-1",
        "铲齿铜底板工艺（自绘示意）",
        "底板优先铲齿或 CNC 短槽，<strong>不是</strong>整板增材。"
        "铲齿一体翅根导热好、适合量产；本设计 GPU 区槽长短"
        f"（≤{G['L_flow_max']:.0f} mm），比传统长铲齿更易控流。"))
    s.append(imgfig(
        "assets/src/sciopen_fig8_fmhs.jpg", "图 6-2",
        "论文原图 · 盖板 + 微通道封合",
        "机加/蚀刻盖板与底板封合，是本设计量产路线的同类结构。"
        "来源：SciOpen 微通道强化换热综述 Fig. 8。"))
    s.append("</div>")

    s.append(h3("6.7　质量与维护"))
    s.append(table(
        ["项", "值 / 要求", "说明"],
        [
            ["外形体积", f"{MC['volume']*1e6:.1f} cm³",
             f"{G['plate_L']:.0f}×{G['plate_W']:.0f}×{G['plate_T']:.1f} mm"],
            ["估算质量", f"≈ {MC['mass']*1e3:.0f} g",
             f"按 {MC['fill']*100:.0f}% 实体率、铜密度 8900 kg/m³"],
            ["可维护性", "本版为钎焊一体件，喷嘴盖<strong>不可现场拆卸</strong>",
             "结构预留拆芯凸台，为专利方案 B（可换喷嘴芯）留接口"],
            ["防堵策略", f"孔径 {G['D_jet']:.2f} mm + 系统过滤 ≤25 μm + "
             "跨板压差监测",
             "压差上升即为堵塞前兆；本版不做在架反冲洗"],
            ["失冷窗口", "不写保证秒数",
             "行业经验约 90 s，<strong>非 NVIDIA 官方指标</strong>，"
             "不作承诺"],
        ]))
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch7_schematic():
    s = ['<section id="schem">']
    s.append(h2("7.", "原理图", "schem"))
    s.append(lead(
        "三张原理图分别回答三个层次的问题："
        "<strong>系统图</strong>说明冷板在回路中的位置与口径分界；"
        "<strong>内部流路图</strong>说明流量怎么分、压降落在哪里；"
        "<strong>机理图</strong>（见 §5.4 图 5-3）说明换热靠什么物理过程。"))

    s.append(h3("7.1　系统水力原理图"))
    s.append(F2.fig_pid())
    s.append('<p class="figcap"><strong>图 7-1</strong>　'
             '系统水力原理图。四块冷板必须并联。</p>')
    s.append(table(
        ["界面", "口径", "责任方", "本冷板的义务"],
        [
            ["机柜一次/二次侧", "25–45 °C ↔ 59–177 L/min；16–127 kPa",
             "CDU / 机柜", "只吃掉自己的 ΔP，不对整柜曲线负责"],
            ["托盘分流", "由孔板分配到 4 块 GPU 冷板",
             "OEM", f"设计按 {A['Q']:.1f} L/min，SAT 实测确认"],
            ["UQD 快接", "参考 4–8 kPa/对",
             "OEM", "跟托盘口径，不自创；是否计入 20 kPa 窗须 ICD 明确"],
            ["Grace 冷板", "独立冷板，300 W 级",
             "OEM / 他方", "不与 B300 共一块铜；本文件不画其流道"],
            ["漏液链", "分层：冷板本体氦检",
             "冷板厂 / 系统", "托盘与机柜漏液检测不在本供货"],
        ]))
    s.append(note(
        "<strong>禁止的三种口径混用：</strong>"
        "① 把整柜 59–177 L/min 中的某一档写成单板保证流量；"
        "② 把 NVSwitch 托盘的 2–50 °C 水温窗写成 GPU 冷板保证；"
        "③ 把 ASHRAE W45 等级当成机柜进液保证值。", "risk"))

    s.append(h3("7.2　冷板内部流路原理图"))
    s.append(F2.fig_internal())
    s.append('<p class="figcap"><strong>图 7-2</strong>　'
             '内部流路与压降分段（DP-A 实算值）。</p>')
    s.append(p(
        "读图要点：<strong>流量 80/20 与功率 78/18 是两件不同的事</strong>。"
        "功率拆分决定各区要带走多少热；流量拆分决定各区能得到多少质量流量。"
        "两者比例接近只是巧合，不能互相推导。"
        "分流靠孔阻与隔墙实现，不靠外置阀门 —— "
        "因为 72 块冷板不可能逐块调阀。"))

    s.append(h3("7.3　温度语义：三条不能混画的线"))
    s.append(F2.fig_temp_path())
    s.append('<p class="figcap"><strong>图 7-3</strong>　'
             '沿程三种温度。保守模型下 T<sub>j</sub> 上界已顶到包络上沿。</p>')
    s.append(table(
        ["符号", "含义", f"DP-A 量级（水 {A['Tin']:.0f} °C 进）",
         "图上怎么认", "常见误用"],
        [
            ["T<sub>f</sub>", "当地 / 混合流体温度",
             f"{A['Tin']:.0f} → {A['Tin']+A['dTf']:.1f} °C "
             f"（+{A['dTf']:.2f} K）",
             "蓝色实线、箭头与歧管配色",
             "把出液 48 °C 当成芯片温度"],
            ["T<sub>w</sub> / T<sub>c</sub>", "铜壁 / 壳温",
             f"{A['Tc'][0]:.0f} – {A['Tc'][1]:.0f} °C（驻点最高）",
             "橙色带（乐观↔保守）",
             "用一张虹彩图把壁温和流体温糊在一起"],
            ["T<sub>j</sub>", "结温",
             f"{A['Tj'][0]:.0f} – {A['Tj'][1]:.0f} °C",
             "红色虚线，比壁峰更高",
             "忽略封装内阻，直接拿壳温当结温"],
        ]))
    s.append(formula(
        "ΔT<sub>f</sub> = P / (ṁ · c<sub>p</sub>)，"
        "ṁ = ρ · Q = "
        f"{M.WATER40.rho:.1f} × {A['Q']:.1f}/60000 = "
        f"{M.mass_flow(M.WATER40, A['Q']):.4f} kg/s",
        f"ΔT<sub>f</sub> = {A['dTf']:.2f} K",
        "混合温升只由总功率与总流量决定，与是射流还是平槽无关"))
    s.append(note(
        "<strong>处处成立：T<sub>j</sub> &gt; T<sub>w</sub> &gt; "
        "T<sub>f</sub>。</strong>"
        f"出液流体即使到 {A['Tin']+A['dTf']:.1f} °C，"
        f"也比驻点壁温低二十多度。因此<strong>不能把出液歧管涂成“芯片红”</strong>，"
        "也不能用 10 K 温升反推流量 —— 那是把结果当成输入。", "ok"))
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch8_drawings():
    s = ['<section id="dwg">']
    s.append(h2("8.", "详细设计：CAD 图纸", "dwg"))
    s.append(lead(
        "型号 <strong>CP-B300-JM-01</strong>，外形候选 "
        f"<strong>{G['plate_L']:.0f} × {G['plate_W']:.0f} × "
        f"{G['plate_T']:.1f} mm</strong>（不含 UQD）。"
        "本章所有图为<strong>按毫米真比例绘制的矢量图</strong>，"
        "1 图形单位 = 1 mm，可直接量取。"
        "NVIDIA 未公布 B300 盖板轮廓，§8.1 的锁定坐标表是全文唯一几何来源。"))

    s.append(h3("8.1　锁定封装坐标（唯一几何来源）"))
    s.append(p("原点：冷板左下角；X 向右，Y 向上；单位 mm。"))
    s.append(table(
        ["对象", "x₀", "y₀", "宽 × 高", "数量", "备注"],
        [
            ["冷板外形", "0", "0",
             f"{G['plate_L']:.0f} × {G['plate_W']:.0f} × {G['plate_T']:.1f}",
             "1", f"候选，{FR}"],
            ["Die-A", f"{G['die_a_x']:.1f}", f"{G['die_a_y']:.1f}",
             f"{G['die_w']:.0f} × {G['die_h']:.0f}", "1", "左计算 die"],
            ["NV-HBI 缝", f"{G['die_a_x']+G['die_w']:.1f}",
             f"{G['die_a_y']:.1f}", f"{G['hbi']:.0f} × {G['die_h']:.0f}",
             "1", "不打密集射流"],
            ["Die-B", f"{G['die_a_x']+G['die_w']+G['hbi']:.1f}",
             f"{G['die_a_y']:.1f}",
             f"{G['die_w']:.0f} × {G['die_h']:.0f}", "1", "右计算 die"],
            ["射流阵 A / B", f"{G['jet_a_x']:.1f} / "
             f"{G['jet_a_x']+G['die_w']+G['hbi']:.1f}",
             f"{G['jet_a_y']:.1f}",
             f"{G['jet_span_x']:.1f} × {G['jet_span_y']:.1f}", "2",
             f"9×12，节距 {G['S_jet_x']:.1f}×{G['S_jet_y']:.1f}，"
             f"中心距 {G['jet_span_x']:.1f}×{G['jet_span_y']:.1f}，"
             f"覆盖 {G['covered_x']:.1f}×{G['covered_y']:.1f}，"
             f"Y 向比 die 宽 {G['overhang_y']:.1f} mm，"
             f"板外包络 {G['envelope_y']:.1f} mm，余 {G['envelope_margin_y']:.1f} mm"],
            ["HBM-L1…L4", f"{G['hbm_x_l']:.1f}",
             f"{G['hbm_y0']:.1f} + n×{G['hbm_dy']:.0f}",
             f"{G['hbm_w']:.0f} × {G['hbm_h']:.0f}", "4",
             "y = 12.5 / 25.5 / 38.5 / 51.5"],
            ["HBM-R1…R4", f"{G['hbm_x_r']:.1f}",
             f"{G['hbm_y0']:.1f} + n×{G['hbm_dy']:.0f}",
             f"{G['hbm_w']:.0f} × {G['hbm_h']:.0f}", "4", "同上"],
            ["隔离肋 左 / 右", f"{G['rib_x_l']:.1f} / {G['rib_x_r']:.1f}",
             f"{G['rib_y0']:.1f}",
             f"{G['rib']:.1f} × {G['rib_len']:.0f}", "2",
             "切断 GPU↔HBM 串流"],
            ["隔离肋 南 / 北", f"{G['die_a_x']:.1f}", "21.5 / 51.5",
             f"57 × {G['rib']:.1f}", "2", "die 上下边"],
            ["进液歧管带", f"{G['man_x']:.0f}", f"{G['man_in_y']:.0f}",
             f"{G['man_w']:.0f} × {G['man_h']:.0f}", "1", "板上沿，IN"],
            ["出液歧管带", f"{G['man_x']:.0f}", f"{G['man_out_y']:.0f}",
             f"{G['man_w']:.0f} × {G['man_h']:.0f}", "1", "板下沿，OUT"],
            ["安装沉孔", "4.5 / 90.5", "4.5 / 70.5", "⌀3.4", "4",
             f"四角，{FR}"],
        ], widths=["16%", "13%", "13%", "17%", "8%", "33%"]))

    s.append(h4("尺寸链闭合校核"))
    s.append(table(
        ["校核项", "算式", "结果 / mm", "期望 / mm", "判定"],
        [[nm, f"<code>{expr}</code>", f"{got:.1f}", f"{want:.1f}",
          '<span class="good">闭合</span>' if abs(got - want) < 1e-6
          else '<span class="bad">不闭合</span>']
         for nm, expr, got, want in M.geometry_checks()]))
    s.append(note(
        "五项尺寸链全部闭合，说明布置在几何上自洽。"
        "这是图纸可以出的前提 —— v1.x 未做此校核。", "ok"))

    s.append(h3("8.2　图纸清单"))
    s.append(table(
        ["图号", "名称", "类型", "比例", "状态"],
        [
            ["JM01-A0", "外形三视图（含标题栏、安装孔、剖切符号）",
             "2D 矢量", "1:1", "候选"],
            ["JM01-A1", "底板流道平面图", "2D 矢量", "1:1", "候选"],
            ["JM01-A2", "剖面 A-A（过 Die-A 中心，GPU 射流区）",
             "2D 矢量", "1:1", "候选"],
            ["JM01-A3", "剖面 B-B（过 HBM 列，无射流）",
             "2D 矢量", "1:1", "候选"],
            ["JM01-A4", "射流单元详图", "2D 矢量", "1:1", "候选"],
            ["JM01-A5", "喷嘴盖板孔位图", "2D 矢量", "1:1（孔径示意放大）",
             "候选"],
            ["JM01-3D", "等轴测装配图", "3D 等轴测", "示意", "候选"],
            ["JM01-A6", "爆炸装配图", "3D 等轴测", "示意", "候选"],
            ["JM01-L1", "分区布置图（性能设计用）", "2D 矢量", "1:1",
             "见图 8-1"],
        ]))

    s.append(h3("8.3　分区布置图"))
    s.append(FG.fig_layout())
    s.append('<p class="figcap"><strong>图 8-1 · JM01-L1</strong>　'
             '分区布置（1:1 真比例）。'
             '两颗 die 中心偏红 = <strong>壁面驻点</strong>，'
             f'不是流体 {A["Tin"]+A["dTf"]:.0f} °C；'
             '青绿 8 块 = HBM，只走平流；深蓝竖条 = 隔离肋。'
             '密点为 9×12 射流落点。Y 向胞列 28.8 mm，比 die 的 28 mm 宽 0.8 mm。</p>')

    s.append(h3("8.4　2D：外形三视图（JM01-A0）"))
    s.append(FG.fig_3view())
    s.append('<p class="figcap"><strong>图 8-2 · JM01-A0</strong>　'
             '第三视角三视图。俯视图含 die/HBM 轮廓（虚线）、'
             '四角安装沉孔、水嘴中心线与 A-A / B-B 剖切符号；'
             '主视与左视按 8.5 mm 薄板真比例绘制。</p>')

    s.append(h3("8.5　2D：底板流道平面图（JM01-A1）"))
    s.append(FG.fig_base_plan())
    s.append('<p class="figcap"><strong>图 8-3 · JM01-A1</strong>　'
             '底板流道。GPU 区短槽沿 X 向、节距 0.80；'
             'HBM 区宽槽沿 Y 向；橙色虚线为盖板回液缝投影，'
             '它把槽内流程截断在 ≤8 mm。红色虚线为 die 轮廓。</p>')

    s.append(h3("8.6　2D：剖面图（JM01-A2 / A3）"))
    s.append(FG.fig_section_gpu())
    s.append('<p class="figcap"><strong>图 8-4 · JM01-A2</strong>　'
             '剖面 A-A（GPU 射流区），1:1 真比例。'
             '厚度链：孔板 2.5 + H 2.0 + 槽 1.5 + 余铜 2.0 = 8.0 mm 腔体。'
             '<strong>水缝不得画得比余铜厚</strong> —— '
             '这是位图示意最常犯的错。</p>')
    s.append(FG.fig_section_hbm())
    s.append('<p class="figcap"><strong>图 8-5 · JM01-A3</strong>　'
             '剖面 B-B（HBM 区），1:1。'
             '盖板此区<strong>无喷嘴</strong>，槽更宽（0.60 vs 0.40）'
             '以降低近壁流速。铜层厚度语言与 A-A 一致，便于对比。</p>')

    s.append(h3("8.7　2D：射流单元详图（JM01-A4）"))
    s.append(FG.fig_unit_cell())
    s.append('<p class="figcap"><strong>图 8-6 · JM01-A4</strong>　'
             f'射流单元，节距 {G["S_jet_x"]:.1f} mm × {G["S_jet_y"]:.1f} mm，1:1。'
             f'整板 GPU 区就是这一格重复 {M.N_JET} 次。'
             '水缝与余铜同厚，箱体不能画成大厅。</p>')

    s.append(h3("8.8　2D：喷嘴盖板孔位图（JM01-A5）"))
    s.append(FG.fig_lid_holes())
    s.append('<p class="figcap"><strong>图 8-7 · JM01-A5</strong>　'
             f'{M.N_JET} 个 ⌀{G["D_jet"]:.2f} mm 喷嘴按真实坐标绘制'
             '（图示直径放大 2.6× 以便看清），'
             '含阵列基准中心线、回液缝与 HBM 区“无喷嘴”明示。</p>')

    s.append(h3("8.9　3D：等轴测装配图（JM01-3D）"))
    s.append(FG.fig_iso())
    s.append('<p class="figcap"><strong>图 8-8 · JM01-3D</strong>　'
             '等轴测装配。按 8.5 mm 薄板绘制，'
             '不要理解成空心箱体。顶面蓝框为两处射流阵，'
             '绿框为 HBM 区（盖板无孔）。</p>')

    s.append(h3("8.10　3D：爆炸装配图（JM01-A6）"))
    s.append(FG.fig_exploded())
    s.append('<p class="figcap"><strong>图 8-9 · JM01-A6</strong>　'
             '爆炸装配。<strong>只有三件 + 水嘴</strong>：'
             '喷嘴盖 2.5 + 钎焊框 0.5（空心框，不是整层水层）+ '
             '底板 3.5。爆炸间隙仅为显示需要。</p>')

    s.append(h3("8.11　零件表（BOM）"))
    s.append(table(
        ["图号", "名称", "数量", "材料", "关键特征", "工艺"],
        [
            ["JM01-100", "换热底板", "1", "C110 / C1020",
             f"GPU 短槽 {M.N_CH_DIE}×2 条 + HBM 宽槽 "
             f"{G['n_hbm_ch']} 条 + 隔离肋 4 条", "铲齿或 CNC"],
            ["JM01-200", "喷嘴盖板", "1", "同铜",
             f"{M.N_JET} × ⌀{G['D_jet']:.2f} 喷嘴 + 回液缝 6 条 + 静压箱",
             "微钻 / 蚀刻"],
            ["JM01-310", "进液水嘴", "1", "铜或不锈钢", f"跟 UQD，{FR}",
             "钎焊或一体"],
            ["JM01-320", "出液水嘴", "1", "同上", "同上", "同上"],
            ["JM01-400", "钎料 / 封接框", "1 套", "Ag 基或 Cu-P",
             "空心框；不得流入 0.40 mm 槽", "真空钎焊"],
            ["JM01-500", "接触面（焊后精铣）", "—", "—",
             "平面度 0.05；Ra ≤0.8 μm", "精铣"],
            ["JM01-600", "接触面镀层（可选）", "—", "化学镀 Ni 3–8 μm",
             "局部镀，不进流道", "化学镀"],
        ], widths=["10%", "16%", "7%", "15%", "34%", "18%"]))
    s.append(note(
        "<strong>本章图纸的工程状态：</strong>"
        "尺寸真实、尺寸链闭合、可用于评审与打样询价，"
        "但<strong>不是可直接投产的正式图纸</strong>。"
        "投产前必须补：完整公差标注体系（GD&T）、"
        "表面处理规范、焊接符号、检验要求表，"
        "并以 OEM 封装图替换 §8.1 的候选坐标。", "risk"))
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch9_calc():
    s = ['<section id="calc">']
    s.append(h2("9.", "一维性能计算", "calc"))
    s.append(lead(
        "本章是<strong>可复算的计算书</strong>：每一步给公式、代入值、结果。"
        f"全部数值由 <code>calc/model.py</code> 计算，"
        f"<code>calc/cp_b300_1d.py</code> 输出文本计算书。"
        "一维计算的作用是<strong>判断方案是否值得做三维仿真</strong>，"
        "不是给出保证值。"))

    s.append(h3("9.1　计算口径与方法学"))
    s.append(table(
        ["项", "取法", "理由"],
        [
            ["工质物性", f"饱和水 {A['Tin']:.0f} °C（见 §3.2）",
             "设计进液温度；不随沿程温升修正（一维保守做法）"],
            ["热源模型", "两 die 面均热流 + 2.5 倍热点系数",
             "官方 power map 未获得"],
            ["换热模型", "<strong>三个独立模型给上下界</strong>",
             "单一关联式在本 Re 区间不可靠，见 §9.4"],
            ["压降模型", "孔口局部损失 + 层流摩阻 + 歧管估值",
             "歧管段必须由 CFD 替换"],
            ["安全取向", "热阻取<strong>区间</strong>而非单值",
             "避免用乐观单值掩盖不确定性"],
        ]))

    s.append(h3("9.2　能量平衡与流体温升"))
    s.append(formula(
        "ṁ = ρ·Q ；　ΔT<sub>f</sub> = P / (ṁ·c<sub>p</sub>)"))
    s.append(table(
        ["Q / L·min⁻¹", "ṁ / kg·s⁻¹",
         f"ΔT<sub>f</sub> @ {A['P']:.0f} W",
         f"ΔT<sub>f</sub> @ {B['P']:.0f} W", "备注"],
        [[f"{q:.1f}", f"{M.mass_flow(M.WATER40, q):.4f}",
          f"{M.delta_tf(M.WATER40, q, 1100):.2f} K",
          f"{M.delta_tf(M.WATER40, q, 1400):.2f} K",
          ("<strong>DP-A 设计点</strong>" if q == 2.0 else
           ("<strong>DP-B 设计点</strong>" if q == 2.4 else
            ("GPU 支路流量" if q == 1.6 else "PG25 备选")))]
         for q in (1.6, 2.0, 2.2, 2.4)]))
    s.append(note(
        f"设计点流体温升 {A['dTf']:.2f} K，与行业常用“&lt;10 K”一致。"
        "<strong>但不得把这个关系倒过来用</strong>："
        "先定 10 K 再除以功率得到流量，是把计算结果当成设计输入。"
        "流量必须由换热需求（孔速）和系统约束（托盘分流）共同决定。"))

    s.append(h3("9.3　射流水力"))
    s.append(formula(
        f"A<sub>jet</sub> = N·πD²/4 = {M.N_JET} × π × "
        f"({G['D_jet']:.2f}/2)² = {M.A_JET*1e6:.2f} mm²"))
    s.append(formula(
        "V<sub>jet</sub> = Q<sub>GPU</sub> / A<sub>jet</sub> ；　"
        "Re<sub>D</sub> = ρ·V<sub>jet</sub>·D / μ ；　"
        "ΔP<sub>孔口</sub> = K·ρV²/2　(K = "
        f"{M.K_ORIFICE})"))
    s.append(table(
        ["设计点", "Q<sub>GPU</sub> / L·min⁻¹", "V<sub>jet</sub> / m·s⁻¹",
         "Re<sub>D</sub>", "ΔP<sub>孔口</sub> / kPa", "流态判定"],
        [
            ["DP-A", f"{A['Qg']:.2f}", f"{A['jet']['V']:.3f}",
             f"<strong>{A['jet']['Re']:.0f}</strong>",
             f"{A['jet']['dP']/1000:.2f}", "层流–过渡"],
            ["DP-B", f"{B['Qg']:.2f}", f"{B['jet']['V']:.3f}",
             f"<strong>{B['jet']['Re']:.0f}</strong>",
             f"{B['jet']['dP']/1000:.2f}", "层流–过渡"],
        ]))

    s.append(h3("9.4　换热系数：三个模型的上下界"))
    s.append(p(
        "这是本报告最重要的一节。"
        "单一关联式在 Re<sub>D</sub> ≈ "
        f"{A['jet']['Re']:.0f} 这个区间不可靠，"
        "因此用三个物理含义不同的模型互相约束："))

    s.append(h4("模型 A · 驻点量级式（只代表驻点核）"))
    s.append(formula(
        "Nu₀ = 0.5·Re<sub>D</sub><sup>0.5</sup>·Pr<sup>0.4</sup> ；　"
        "h<sub>stag</sub> = Nu₀·k / D",
        f"h<sub>stag</sub> = {A['con']['h_stag']:,.0f} W·m⁻²K⁻¹",
        "只在孔正下方约 1 mm² 的核内成立，不能代表整区"))

    s.append(h4("模型 B · Martin(1977) 圆孔阵列面平均（乐观）"))
    s.append(formula(
        "Nu / Pr<sup>0.42</sup> = K(f, H/D) · Re<sup>2/3</sup> ；　"
        "K = [1 + (H/D ÷ (0.6/√f))⁶]<sup>−0.05</sup> · √f · "
        "(2 − 2.2√f) / (1 + 0.2(H/D − 6)√f)",
        f"K 与 Nu <strong>不计算</strong>。"
        f"Re_D = {A['jet']['Re']:.0f} &lt; 2000，Martin 1977 不采用",
        f"有效域：2000 ≤ Re ≤ 10⁵，0.004 ≤ f ≤ 0.04，2 ≤ H/D ≤ 12。"
        f"本设计 f = {M.F_AREA:.5f}，H/D = {M.HD:.1f}，"
        f"<strong>Re = {A['jet']['Re']:.0f}，低于下限，关联式不采用</strong>"))
    s.append(note(
        f"<strong>模型 B 不采用。</strong>设计点 Re<sub>D</sub> = "
        f"{A['jet']['Re']:.0f}，低于 Martin 1977 下限 2000。"
        "不把外推的 Nu 或 h 写进热阻。"
        "壳–进液只保留模型 C（短槽）加上 R_TIM2 区间。", "risk"))

    s.append(h4("模型 C · 短槽当肋 + 导管对流（保守）"))
    s.append(p(
        "按真实“就近抽走”拓扑：每个孔的流量只在其 "
        f"{G['S_jet_x']:.1f} mm × {G['S_jet_y']:.1f} mm 的单元内左右分走，流程 "
        f"L<sub>f</sub> = {G['L_flow']:.1f} mm。此时槽内是<strong>低速流</strong>，"
        "槽的作用是扩展表面（肋），不是高速导管。"))
    s.append(formula(
        "Nu<sub>ch</sub> = max(4.0, 1.86·Gz<sup>1/3</sup>)，"
        "Gz = (D<sub>h</sub>/L)·Re·Pr ；　"
        "h<sub>ch</sub> = Nu·k / D<sub>h</sub>",
        f"Nu<sub>ch</sub> = {A['con']['Nu']:.2f}，"
        f"h<sub>ch</sub> = {A['con']['h_ch']:,.0f} W·m⁻²K⁻¹",
        "恒热流全发展层流下界 Nu = 4.0；短槽属热入口段"))
    s.append(formula(
        "肋效率 η<sub>f</sub> = tanh(mL)/mL，m = √(2h/(k<sub>Cu</sub>·t))",
        f"η<sub>f</sub> = {A['con']['eta']:.3f}",
        f"肋厚 {G['ch_w']:.2f} mm、肋高 {G['ch_h']:.2f} mm、"
        f"k<sub>Cu</sub> = {M.K_CU:.0f} W·m⁻¹K⁻¹"))
    s.append(formula(
        "hA = h<sub>ch</sub>·(A<sub>肋</sub>·η<sub>f</sub> + "
        "A<sub>槽底</sub>) + (h<sub>stag</sub> − h<sub>ch</sub>)·"
        "A<sub>驻点</sub>　（每 die，再 ×2）",
        f"hA = {A['con']['hA']:.1f} W/K → "
        f"h<sub>eff</sub>(footprint) = {A['con']['h_eff']:,.0f} W·m⁻²K⁻¹"))

    s.append(h4("三模型对比"))
    s.append(table(
        ["模型", "物理含义", f"h / W·m⁻²K⁻¹（DP-A）",
         "R<sub>conv</sub> / °C/W", "可靠性评价"],
        [
            ["A 驻点式", "孔正下方核内峰值",
             f"{A['con']['h_stag']:,.0f}", "不可直接用",
             "只说明驻点量级"],
            ["B Martin 阵列", "整个冲击面的面平均",
             "不采用", "不采用",
             '<span class="bad">Re&lt;2000，不外推</span>'],
            ["C 肋 + 导管", "把槽当扩展表面，叠加驻点强化",
             f"{A['con']['h_eff']:,.0f}",
             f"<strong>{A['con']['R']:.4f}</strong>",
             '<span class="warn2">保守下界，忽略射流对槽内的强化</span>'],
        ]))
    s.append(note(
        "模型 B 因 Re<sub>D</sub> &lt; 2000 <strong>不采用</strong>，"
        "没有 Martin 下界可与模型 C 相除。"
        f"设计热阻用模型 C：R<sub>conv</sub> = {A['con']['R']:.4f} °C/W，"
        f"再加 R_wall = {M.R_WALL:.4f} 与 R_TIM2 = "
        f"{M.R_TIM2[0]:.3f}–{M.R_TIM2[1]:.3f}。"
        f"DP-A 壳–进液 {A['R_lo']:.4f}–{A['R_hi']:.4f} °C/W。"
        "<strong>把这个区间用三维共轭 CFD 收窄，仍是核心任务。</strong>",
        "risk"))

    s.append(h3("9.5　通道侧流动（两种拓扑对比）"))
    s.append(formula(
        f"D<sub>h</sub> = 2wh/(w+h) = 2×{G['ch_w']:.2f}×{G['ch_h']:.2f}/"
        f"({G['ch_w']:.2f}+{G['ch_h']:.2f}) = {M.DH_CH*1e3:.4f} mm ；　"
        f"f·Re = {M.FRE_CH:.2f}（Shah & London 矩形层流，"
        f"α = {min(G['ch_w'],G['ch_h'])/max(G['ch_w'],G['ch_h']):.3f}）"))
    s.append(table(
        ["拓扑模型", "流动假设", "V / m·s⁻¹", "Re", "L / mm",
         "ΔP<sub>槽</sub> / kPa", "评价"],
        [
            ["cell（真实）",
             "每孔流量在单元内就近左右分走",
             f"{A['ch']['V']:.3f}", f"{A['ch']['Re']:.0f}",
             f"{A['ch']['L']*1e3:.1f}", f"{A['ch']['dP']/1000:.4f}",
             "<strong>与射流拓扑自洽</strong>"],
            ["bank（对比）",
             "全流量单向穿过全部槽（相当于没有射流）",
             f"{A['ch_bank']['V']:.3f}", f"{A['ch_bank']['Re']:.0f}",
             f"{A['ch_bank']['L']*1e3:.1f}",
             f"{A['ch_bank']['dP']/1000:.4f}",
             "v1.x 采用，与射流<strong>互相矛盾</strong>"],
        ]))
    s.append(table(
        ["项", "值", "说明"],
        [
            ["每 die 槽数", f"{M.N_CH_DIE} 条",
             f"{G['die_h']:.0f} mm ÷ {G['ch_p']:.2f} mm 节距"],
            ["单 die 肋面积", f"{M.A_FIN_DIE*1e6:.0f} mm²",
             f"{M.N_CH_DIE} × 2 面 × {G['ch_h']:.2f} mm × "
             f"{G['die_w']:.0f} mm"],
            ["单 die 槽底面积", f"{M.A_BOT_DIE*1e6:.0f} mm²", "—"],
            ["单 die 湿润面积", f"<strong>{M.A_WET_DIE*1e6:.0f} mm²</strong>",
             f"footprint {M.A_DIE*1e6:.0f} mm² 的 "
             f"<strong>{M.AREA_GAIN:.2f} 倍</strong>"],
        ]))
    s.append(note(
        "<strong>这是对 v1.x 的一处实质修正。</strong>"
        "v1.x 按 bank 模型算出槽内 0.74 m/s、Re 710、ΔP 0.4 kPa，"
        "但那个流动图像要求全部流量从槽的一端流到另一端 —— "
        "与“射流垂直冲击后就近抽走”不能同时成立。"
        "按自洽的 cell 模型，槽内压降可忽略，"
        f"槽的价值在于 {M.AREA_GAIN:.2f} 倍面积放大和 "
        f"{A['con']['eta']:.3f} 的肋效率。", "risk"))

    s.append(h3("9.6　HBM 区校核"))
    s.append(formula(
        f"D<sub>h,HBM</sub> = {M.DH_HBM*1e3:.3f} mm ；　"
        f"V = Q<sub>HBM</sub> / (N<sub>ch</sub>·w·h) ；　"
        f"f·Re = {M.FRE_HBM:.2f}"))
    s.append(table(
        ["设计点", "Q<sub>HBM</sub> / L·min⁻¹", "V / m·s⁻¹",
         f"流速帽 {G['V_cap_hbm']:.2f}", "Re", "ΔP / kPa", "判定"],
        [
            ["DP-A", f"{A['hbm']['Q_lpm']:.2f}", f"{A['hbm']['V']:.3f}",
             f"余量 {(1-A['hbm']['V']/G['V_cap_hbm'])*100:.0f}%",
             f"{A['hbm']['Re']:.0f}", f"{A['hbm']['dP']/1000:.2f}",
             '<span class="good">通过</span>'],
            ["DP-B", f"{B['hbm']['Q_lpm']:.2f}", f"{B['hbm']['V']:.3f}",
             f"余量 {(1-B['hbm']['V']/G['V_cap_hbm'])*100:.0f}%",
             f"{B['hbm']['Re']:.0f}", f"{B['hbm']['dP']/1000:.2f}",
             '<span class="good">通过</span>'],
        ]))

    s.append(h3("9.7　热阻链与温度汇总"))
    s.append(formula(
        f"R<sub>wall</sub> = t / (k<sub>Cu</sub>·A<sub>2die</sub>) = "
        f"{G['base_cu']:.1f}e-3 / ({M.K_CU:.0f} × {M.A_2DIE*1e4:.2f}e-4)",
        f"R<sub>wall</sub> = {M.R_WALL:.5f} °C/W"))
    s.append(formula(
        "R<sub>θ,c-in</sub> = R<sub>TIM2</sub> + R<sub>wall</sub> + "
        "R<sub>conv</sub> ；　T<sub>c</sub> = T<sub>in</sub> + "
        "R<sub>θ,c-in</sub>·P ；　T<sub>j</sub> = T<sub>c</sub> + "
        "R<sub>pkg</sub>·P"))
    s.append(table(
        ["设计点", "组合", "R<sub>TIM2</sub>", "R<sub>wall</sub>",
         "R<sub>conv</sub>", "<strong>R<sub>θ,c-in</sub></strong>",
         "ΔT<sub>c</sub>", "T<sub>c</sub>", "T<sub>j</sub>", "对目标"],
        [
            ["DP-A", "短槽 + TIM2=0.004", f"{M.R_TIM2[0]:.3f}",
             f"{M.R_WALL:.4f}", f"{A['con']['R']:.4f}",
             f"<strong>{A['R_lo']:.4f}</strong>", f"{A['dTc'][0]:.1f} K",
             f"{A['Tc'][0]:.1f} °C", f"{A['Tj'][0]:.1f} °C",
             '<span class="good">低于目标</span>' if A['pass_lo']
             else '<span class="bad">高于目标</span>'],
            ["DP-A", "短槽 + TIM2=0.008", f"{M.R_TIM2[1]:.3f}",
             f"{M.R_WALL:.4f}", f"{A['con']['R']:.4f}",
             f"<strong>{A['R_hi']:.4f}</strong>", f"{A['dTc'][1]:.1f} K",
             f"{A['Tc'][1]:.1f} °C", f"{A['Tj'][1]:.1f} °C",
             '<span class="good">低于目标</span>' if A['pass_hi']
             else '<span class="bad">高于目标</span>'],
            ["DP-B", "短槽 + TIM2=0.004", f"{M.R_TIM2[0]:.3f}",
             f"{M.R_WALL:.4f}", f"{B['con']['R']:.4f}",
             f"<strong>{B['R_lo']:.4f}</strong>", f"{B['dTc'][0]:.1f} K",
             f"{B['Tc'][0]:.1f} °C", f"{B['Tj'][0]:.1f} °C",
             '<span class="good">低于目标</span>' if B['pass_lo']
             else '<span class="bad">高于目标</span>'],
            ["DP-B", "短槽 + TIM2=0.008", f"{M.R_TIM2[1]:.3f}",
             f"{M.R_WALL:.4f}", f"{B['con']['R']:.4f}",
             f"<strong>{B['R_hi']:.4f}</strong>", f"{B['dTc'][1]:.1f} K",
             f"{B['Tc'][1]:.1f} °C", f"{B['Tj'][1]:.1f} °C",
             '<span class="good">低于目标</span>' if B['pass_hi']
             else '<span class="bad">高于目标</span>'],
        ], widths=["8%", "20%", "8%", "8%", "9%", "11%", "8%", "9%",
                   "9%", "10%"]))

    s.append(h3("9.8　压降预算"))
    s.append(table(
        ["分段", "模型", f"DP-A / kPa", f"DP-B / kPa", "备注"],
        [
            ["喷嘴孔口", f"K·ρV²/2，K = {M.K_ORIFICE}",
             f"{A['dp']['orifice']/1000:.2f}",
             f"{B['dp']['orifice']/1000:.2f}", "主要可控项"],
            ["GPU 短槽", "层流摩阻（cell 拓扑）",
             f"{A['dp']['channel']/1000:.3f}",
             f"{B['dp']['channel']/1000:.3f}",
             "<strong>可忽略</strong>"],
            ["HBM 槽", "层流摩阻，L = 50 mm",
             f"{A['dp']['hbm']/1000:.2f}", f"{B['dp']['hbm']/1000:.2f}",
             "低速"],
            ["盖板静压箱 / 隔墙", "<strong>估值</strong>",
             f"{A['dp']['manifold'][0]/1000:.0f} – "
             f"{A['dp']['manifold'][1]/1000:.0f}",
             f"{B['dp']['manifold'][0]/1000:.0f} – "
             f"{B['dp']['manifold'][1]/1000:.0f}",
             "<strong>必须由 CFD 替换</strong>（AS-7）"],
            ["<strong>板内合计</strong>", "—",
             f"<strong>{A['dp']['total'][0]/1000:.1f} – "
             f"{A['dp']['total'][1]/1000:.1f}</strong>",
             f"<strong>{B['dp']['total'][0]/1000:.1f} – "
             f"{B['dp']['total'][1]/1000:.1f}</strong>",
             f"目标 ≤{G['dP_target']:.0f}，上限 {G['dP_limit']:.0f}"],
            ["一对 UQD（参考）", "厂家曲线", "4 – 8", "同左",
             "不计入冷板窗则须 ICD 声明"],
        ]))
    s.append(note(
        f"<strong>压降余量是本设计最大的资产。</strong>"
        f"板内只用掉 {A['dp']['total'][1]/1000:.1f} kPa，"
        f"距 {G['dP_target']:.0f} kPa 目标还有 "
        f"{G['dP_target']-A['dp']['total'][1]/1000:.0f} kPa 可用。"
        "热阻却已超标 —— 所以正确的优化方向是"
        "<strong>拿压降去换换热</strong>（减小孔径、加密阵列），"
        "而不是继续优化压降。", "ok"))

    s.append(h3("9.9　PG25 复算"))
    s.append(table(
        ["项", "DI 水 40 °C", "PG25 40 °C", "变化", "影响"],
        [
            ["Pr", f"{M.WATER40.Pr:.2f}", f"{M.PG25_40.Pr:.2f}",
             f"×{M.PG25_40.Pr/M.WATER40.Pr:.2f}", "—"],
            ["Re<sub>D</sub>（同流量）", f"{A['jet']['Re']:.0f}",
             f"{AP['jet']['Re']:.0f}",
             f"{(AP['jet']['Re']/A['jet']['Re']-1)*100:+.0f}%",
             "更深入层流区"],
            ["Martin h", "不采用", "不采用", "—",
             "Re&lt;2000，两侧都不外推"],
            ["R<sub>conv</sub>（模型 C）", f"{A['con']['R']:.4f}",
             f"{AP['con']['R']:.4f}",
             f"<strong>{(AP['con']['R']/A['con']['R']-1)*100:+.1f}%</strong>",
             "短槽模型，216 胞并联"],
            ["ΔT<sub>f</sub>", f"{A['dTf']:.2f} K", f"{AP['dTf']:.2f} K",
             f"{(AP['dTf']/A['dTf']-1)*100:+.1f}%", "c<sub>p</sub> 较低"],
            ["ΔP<sub>孔口</sub>", f"{A['jet']['dP']/1000:.2f} kPa",
             f"{AP['jet']['dP']/1000:.2f} kPa",
             f"{(AP['jet']['dP']/A['jet']['dP']-1)*100:+.1f}%",
             "密度略高，影响小"],
        ]))
    s.append(note(
        f"<strong>PG25 不沿用水的 Martin 百分比。</strong>"
        "两侧 Re 都低于 2000，Martin h 不计算。"
        "根因仍是 PG25 的导热率只有水的 "
        f"{M.PG25_40.k/M.WATER40.k*100:.0f}%，"
        f"而粘度是 {M.PG25_40.mu/M.WATER40.mu:.2f} 倍。"
        f"短槽模型 R_conv 从 {A['con']['R']:.4f} 变为 {AP['con']['R']:.4f} °C/W。"
        "<strong>若项目最终选 PG25，必须单独定流量并重做 CFD</strong>，"
        "不能沿用水的 2.0 L/min。", "risk"))

    s.append(h3("9.10　敏感性分析：孔径"))
    s.append(F2.fig_orifice_chart())
    s.append('<p class="figcap"><strong>图 9-1</strong>　'
             f'孔径敏感性。孔数固定 {M.N_JET}，GPU 支路流量固定 1.60 L/min。'
             'Re<sub>D</sub> 全部低于 2000，Martin h 不采用。</p>')
    s.append(table(
        ["D / mm", "Sx/D", "Sy/D", "H/D", "V / m·s⁻¹", "Re<sub>D</sub>",
         "Martin", "ΔP<sub>孔口</sub> / kPa", "评价"],
        [[f"{r['D']:.2f}", f"{r['sd_x']:.1f}", f"{r['sd_y']:.1f}",
          f"{r['hd']:.1f}", f"{r['V']:.3f}", f"{r['Re']:.0f}",
          "不采用", f"{r['dP']/1000:.2f}",
          ("<strong>当前基线</strong>" if r["D"] == 0.50 else
           ("CFD 单胞孔径，仍低于 Re=2000" if r["D"] == 0.40 else
            ("DP-B 储备（过滤收紧）" if r["D"] == 0.35 else
             ("极限，堵塞风险高" if r["D"] == 0.30 else "中间档"))))]
         for r in SW]))
    s.append(p(
        "Martin 1977 在 Re<sub>D</sub> &lt; 2000 时不采用，"
        "因此本表不给 h，也不给由 Martin 反推的 R<sub>θ,c-in</sub>。"))
    s.append(table(
        ["杠杆", "效果", "代价", "建议"],
        [
            ["孔径 0.50 → 0.40 mm",
             f"Re {SW[0]['Re']:.0f} → {SW[2]['Re']:.0f}，仍低于 2000",
             f"孔口 ΔP {SW[0]['dP']/1000:.2f} → {SW[2]['dP']/1000:.2f} kPa；"
             f"过滤收紧到 {0.40*100:.0f} μm",
             "单胞 CFD 用 0.40 mm；Martin 仍不采用"],
            ["孔径 → 0.35 mm",
             f"Re {SW[3]['Re']:.0f}",
             f"ΔP {SW[3]['dP']/1000:.2f} kPa；堵塞后果严重",
             "仅作 DP-B 储备"],
            ["流量 2.0 → 2.4 L/min",
             f"Re {A['jet']['Re']:.0f} → {B['jet']['Re']:.0f}",
             "系统侧需确认分流能力；ΔP 上升",
             "受托盘约束，非本方可控"],
            ["TIM2 0.008 → 0.004 °C/W",
             f"直接省 {(M.R_TIM2[1]-M.R_TIM2[0])*1000:.0f} mK/W，"
             f"约占预算 {(M.R_TIM2[1]-M.R_TIM2[0])/A['target']*100:.0f}%",
             "TIM 成本与装配工艺",
             "<strong>性价比最高，优先推进</strong>"],
            ["阵列已定为 9×12",
             f"每 die {G['n_jet_per_die']} 孔，两 die {M.N_JET} 孔",
             "Y 向胞列 28.8 mm，比 die 28 mm 宽 0.8 mm；板外包络 29.2 mm，余 0.4 mm",
             "热流按 216 胞摊全部 GPU 热量，不按 756 mm² 满铺"],
        ], widths=["18%", "30%", "28%", "24%"]))

    s.append(h3("9.11　差距闭合矩阵"))
    s.append(p(
        "问题定义：保守模型给出的等效 h（footprint 基准）为 "
        f"<strong>{A['con']['h_eff']:,.0f} W·m⁻²K⁻¹</strong>。"
        "要达标需要多大的 h？"))
    s.append(formula(
        "h<sub>required</sub> = 1 / [(R<sub>target</sub> − R<sub>wall</sub> − "
        "R<sub>TIM2</sub>) · A<sub>covered</sub>]"))
    rows = []
    for nm, sol in (("DP-A", A), ("DP-B", B)):
        for t2, tag in ((0.008, "常规导热垫（差）"),
                        (0.006, "常规导热垫（好）"),
                        (0.004, "高性能 TIM2"),
                        (0.002, "液金 / 焊接")):
            hr = M.h_required(sol["target"], t2)
            if hr == float("inf"):
                rows.append([nm, f"{t2:.3f}", tag, "—",
                             '<span class="bad">预算被 TIM2 吃光</span>',
                             "不可行"])
            else:
                gap = hr / sol["con"]["h_eff"] - 1
                ok = gap <= 0
                rows.append([
                    nm, f"{t2:.3f}", tag, f"{hr:,.0f}",
                    (f'<span class="good">已满足</span>' if ok else
                     f'<span class="bad">差 {gap*100:+.0f}%</span>'),
                    ("保守模型即可达标" if ok else
                     ("需孔径优化" if gap < 0.2 else
                      "需孔径优化 + 流量提升"))])
    s.append(table(
        ["设计点", "R<sub>TIM2</sub>", "TIM2 档次",
         "需要 h / W·m⁻²K⁻¹", "对比保守模型", "闭合手段"],
        rows))
    s.append(F2.fig_gap_chart())
    s.append('<p class="figcap"><strong>图 9-2</strong>　'
             '差距闭合。红线为保守模型天花板，'
             '线上方的柱子都是保守模型打不到的目标。</p>')

    s.append(h3("9.12　一维计算结论"))
    s.append(ol([
        "<strong>水力全面达标且余量大</strong>：压降、HBM 流速、"
        "流体温升三项均通过，余量充足。",
        "<strong>热性能不判定</strong>：区间跨越目标线，"
        "乐观端达标、保守端超标。一维计算无法收敛，"
        "<strong>这是转入三维仿真的技术理由</strong>。",
        "<strong>若真实性能接近保守端</strong>，DP-A 需要 TIM2 ≤ 0.004 °C/W "
        "才勉强达标；DP-B 需要液金级 TIM2 叠加孔径优化。",
        "<strong>最优先的两个杠杆</strong>：TIM2 升级（省 "
        f"{(M.R_TIM2[1]-M.R_TIM2[0])*1000:.0f} mK/W，"
        "无几何代价）与孔径 0.50→0.40 mm（h +16%，ΔP 代价可接受）。",
        "<strong>已识别的模型缺陷</strong>：Re 低于关联式有效域（§9.4）、"
        "槽深过大存在死体积（§6.2 OPT-1）、"
        "歧管压降为估值（AS-7）。三项都只能由 CFD 关闭。",
    ]))
    s.append(note(
        "复算方法：<code>cd design/calc && set PYTHONIOENCODING=utf-8 && "
        "python cp_b300_1d.py</code>，"
        "输出 <code>cp_b300_1d_out.txt</code>。"
        "修改 <code>model.py</code> 中的 <code>GEO</code> / "
        "<code>DESIGN_POINTS</code> 后重新生成本报告，全文数值同步更新。",
        "ok"))
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch10_cfd():
    s = ['<section id="cfd">']
    s.append(h2("10.", "三维仿真需求（CFD 工具待定）", "cfd"))
    s.append(lead(
        "本章是<strong>仿真需求规格书</strong>，不是仿真报告。"
        "它规定要回答什么问题、用什么网格和模型、"
        "以及什么条件下才算通过 —— "
        "以便在工具选定后由任何一方执行并被复核。"
        "<strong>工具刻意不指定</strong>，只给能力要求。"))

    s.append(h3("10.1　仿真要回答的问题（按优先级）"))
    s.append(table(
        ["#", "问题", "为什么一维答不了", "判据 / 交付"],
        [
            ["Q1", "壳–进液热阻的真值是多少？",
             f"Martin 因 Re = {A['jet']['Re']:.0f} &lt; 2000 不采用，"
             "一维只剩短槽模型",
             "给出 R<sub>θ,c-in</sub> 单值，"
             "与网格无关性误差 &lt; 3%"],
            ["Q2", f"{M.N_JET} 个孔的流量一致性如何？",
             "一维无法解静压箱内部压力分布",
             "各孔流量偏差 ≤ ±10%；给出最差孔位置"],
            ["Q3", "两 die 之间与 die 内部的温差分布？",
             "一维是集中参数，没有空间分布",
             "两 die 中心温差 ≤ 5 K；给出壁温云图"],
            ["Q4", "静压箱与隔墙的真实压降是多少？",
             "一维只能给 3–5 kPa 估值（AS-7）",
             "替换 §9.8 的估值；总 ΔP ≤ 18 kPa"],
            ["Q5", "交叉流是否把下游驻点吹偏？",
             "一维没有流场",
             "驻点位置偏移 &lt; 0.5 mm；给出流线图"],
            ["Q6", "HBM 区是否存在局部高速冲蚀风险？",
             "一维只算平均流速",
             f"全域近壁速度 ≤ {G['V_cap_hbm']:.2f} m/s"],
            ["Q7", "槽深从 1.5 减到 0.8–1.0 mm 是否更优？（OPT-1）",
             "一维无法评估死体积效应",
             "给出槽深 0.8/1.0/1.5 mm 的 R 与 ΔP 对比"],
            ["Q8", "PG25 工况下性能与流量需求？",
             "一维外推更不可靠（Re 更低）",
             "给出 PG25 的推荐流量"],
        ], widths=["5%", "24%", "33%", "38%"]))

    s.append(h3("10.2　工具候选与选型准则"))
    s.append(p("工具<strong>待定</strong>。选型不按品牌，按以下能力要求判定："))
    s.append(table(
        ["能力要求", "为什么必须", "验证方法"],
        [
            ["共轭传热（CHT，流固耦合）",
             "铜的横向扩热是分区设计成立的前提，不能用等温壁代替",
             "跑一个已知解析解的平板算例"],
            ["低 Re / 转捩流动建模",
             f"Re<sub>D</sub> ≈ {A['jet']['Re']:.0f} 处于层流–过渡区，"
             "全湍流模型会高估换热",
             "同一算例跑层流与转捩 SST，对比差异"],
            ["高纵横比小特征网格",
             f"⌀{G['D_jet']:.2f} mm 孔与 {G['ch_w']:.2f} mm 槽，"
             "与 95 mm 板尺度相差 200 倍",
             "网格质量指标：最小正交质量 &gt; 0.15"],
            ["多孔/多通道流量后处理",
             "Q2 要逐孔流量，需要面通量统计能力",
             "能输出 128 个孔的质量流量列表"],
            ["参数化与批量求解",
             "§10.7 工况矩阵有 12+ 算例，OPT-1 还要扫槽深",
             "支持脚本化批处理"],
        ]))
    s.append(note(
        "常见候选包括通用 CFD 求解器与电子散热专用求解器两类。"
        "<strong>专用电子散热工具的风险</strong>是对 0.5 mm 射流孔"
        "常用降阶/多孔介质模型，可能无法解析驻点边界层；"
        "<strong>通用求解器的风险</strong>是网格量与人工成本。"
        "建议：先用通用求解器做 1/4 对称精细模型定标，"
        "再用降阶模型做全板工况扫描。"))

    s.append(h3("10.3　计算域与简化"))
    s.append(F2.fig_cfd_domain())
    s.append('<p class="figcap"><strong>图 10-1</strong>　'
             '共轭计算域分层、网格要求与边界条件。</p>')
    s.append(table(
        ["项", "要求", "理由"],
        [
            ["对称简化", "允许沿 X 中线取 1/2；"
             "<strong>不允许</strong>取 1/4",
             "两 die 对称可用；但 IN/OUT 沿 Y 不对称，Y 向不能切"],
            ["入口延长段", "≥ 10 D<sub>h</sub>", "避免入口回流污染解"],
            ["出口延长段", "≥ 10 D<sub>h</sub>", "避免出口回压反射"],
            ["固体域", "必须含余铜 + 槽肋 + 盖板；"
             "TIM2 与封装盖用等效导热层",
             "铜横向扩热必须解出来"],
            ["允许的简化", "水嘴内部细节可简化为等效入口；"
             "安装沉孔可忽略",
             "对 R 与 ΔP 影响 &lt; 1%"],
            ["禁止的简化", "① 把喷嘴孔当多孔介质；"
             "② 用等温壁代替共轭；"
             "③ 只算 1 个单元胞外推整板",
             "分别会丢掉驻点、扩热和边缘效应"],
        ]))

    s.append(h3("10.4　网格要求"))
    s.append(table(
        ["部位", "网格要求", "判据"],
        [
            ["驻点区（孔正下方）", "首层厚度 ≤ 3 μm，法向 ≥ 15 层",
             "y⁺ &lt; 1"],
            ["喷嘴孔内", "径向 ≥ 12 单元，轴向 ≥ 8 单元",
             "解析孔口收缩"],
            ["射流间隙 H = 2.0 mm", "法向 ≥ 20 层", "解析自由射流发展"],
            ["短槽内（0.40 × 1.50）", "宽度方向 ≥ 8，深度方向 ≥ 12",
             "层流剖面需解析"],
            ["肋与余铜", "厚度方向 ≥ 6 层", "共轭导热梯度"],
            ["总网格量", "预计 3 000 万 – 8 000 万（全模）",
             "1/2 对称可减半"],
            ["网格无关性", "至少三套网格（粗/中/细，比例 1:1.5:2.25）",
             "<strong>R 与 ΔP 相邻两套差异 &lt; 3%</strong>"],
        ]))

    s.append(h3("10.5　物理模型"))
    s.append(table(
        ["项", "设定", "备注"],
        [
            ["流态", "不可压、稳态为主",
             "瞬态仅用于失冷/负载突变专题"],
            ["湍流模型", "<strong>转捩 SST（γ-Reθ）为基线</strong>；"
             "k-ω SST 低 Re 修正为对照",
             f"Re<sub>D</sub> = {A['jet']['Re']:.0f} 处于过渡区"],
            ["层流对照算例", "<strong>必做</strong>",
             "与转捩模型构成包络；若两者差异 &gt; 20% 需专题"],
            ["浮升力", "可忽略（Ri &lt;&lt; 1）",
             "抽吸由压差驱动，与热浮力无关"],
            ["物性", "温变物性（μ、k 随温度）",
             "水在 40→48 °C 区间 μ 变化约 15%，不可忽略"],
            ["固体导热", f"Cu {M.K_CU:.0f} W·m⁻¹K⁻¹（各向同性）", "—"],
            ["接触热阻", "TIM2 以等效热阻层加载，"
             f"扫 {M.R_TIM2[0]}/{M.R_TIM2[1]} 两档",
             "TIM2 是最敏感参数（§9.11）"],
        ]))

    s.append(h3("10.6　边界条件与热源加载"))
    s.append(table(
        ["边界", "类型", "取值"],
        [
            ["入口", "质量流入口 + 温度",
             f"ṁ = {M.mass_flow(M.WATER40, A['Q']):.4f} kg/s（DP-A），"
             f"T = {A['Tin']:.0f} °C"],
            ["出口", "压力出口", "0 Pa（表压）"],
            ["外表面", "绝热（保守）",
             "实际有少量对流散热，忽略偏保守"],
            ["热源 — 基线", "两 die 区域均匀面热流",
             f"{A['q_die']:.1f} W/cm² × 2；HBM {A['q_hbm']:.1f} W/cm² × 8"],
            ["热源 — 热点工况", "die 内叠加 2.5 倍热点分布",
             f"峰值 {A['q_die']*2.5:.0f} W/cm²；"
             "热点位置与面积须做敏感性"],
            ["热源 — 真实热图", "<strong>获得官方 power map 后必须重跑</strong>",
             "IN-T4，当前缺失"],
            ["壁面", "无滑移、光滑",
             "粗糙度影响留作敏感性（Ra 0.8 μm）"],
        ]))

    s.append(h3("10.7　工况矩阵（最小集）"))
    s.append(table(
        ["#", "功率 / W", "流量 / L·min⁻¹", "工质", "进液 / °C",
         "热源分布", "目的"],
        [
            ["C01", f"{A['P']:.0f}", f"{A['Q']:.1f}", "水", "40", "均匀",
             "<strong>基线</strong>，与 §9 对比"],
            ["C02", f"{A['P']:.0f}", f"{A['Q']:.1f}", "水", "40",
             "热点 2.5×", "壁温峰值"],
            ["C03", f"{A['P']:.0f}", "1.6", "水", "40", "均匀",
             "低流量敏感性"],
            ["C04", f"{A['P']:.0f}", f"{B['Q']:.1f}", "水", "40", "均匀",
             "高流量收益"],
            ["C05", f"{A['P']:.0f}", f"{A['Q']:.1f}", "水", "45",
             "热点 2.5×", "<strong>最恶工况</strong>"],
            ["C06", f"{B['P']:.0f}", f"{B['Q']:.1f}", "水", "40",
             "热点 2.5×", "DP-B 包络"],
            ["C07", f"{B['P']:.0f}", f"{B['Q']:.1f}", "水", "45",
             "热点 2.5×", "DP-B 最恶"],
            ["C08", f"{A['P']:.0f}", f"{A['Q']:.1f}", "PG25", "40", "均匀",
             "工质敏感性（Q8）"],
            ["C09", f"{A['P']:.0f}", "2.2", "PG25", "40", "热点 2.5×",
             "PG25 补流量后能否达标"],
            ["C10", f"{A['P']:.0f}", f"{A['Q']:.1f}", "水", "40", "均匀",
             "HBM 支路堵塞 20%（鲁棒性）"],
            ["C11", f"{A['P']:.0f}", f"{A['Q']:.1f}", "水", "40", "均匀",
             "孔径 0.40 mm 变体（§9.10）"],
            ["C12", f"{A['P']:.0f}", f"{A['Q']:.1f}", "水", "40", "均匀",
             "槽深 0.8 / 1.0 mm 变体（OPT-1）"],
        ], widths=["6%", "10%", "12%", "9%", "10%", "14%", "39%"]))

    s.append(h3("10.8　收敛与后处理判据"))
    s.append(table(
        ["项", "判据"],
        [
            ["残差", "连续性与动量 &lt; 1e-4，能量 &lt; 1e-6"],
            ["监测量稳定", "R<sub>θ,c-in</sub> 与 ΔP 连续 500 步漂移 "
             "&lt; 0.5%"],
            ["能量守恒", "出入口焓差与总热源偏差 &lt; 1%"],
            ["质量守恒", "进出口质量流偏差 &lt; 0.1%"],
            ["网格无关性", "相邻网格 R 与 ΔP 差异 &lt; 3%"],
            ["模型不确定性", "转捩 SST 与层流两模型差异须报告；"
             "若 &gt; 20% 则结论只能给区间"],
        ]))
    s.append(h4("必须交付的后处理"))
    s.append(ul([
        "壁温云图（余铜接触面），标出最高点坐标与两 die 中心温差；",
        "流体温度云图与流线（含驻点与交叉流可视化）；",
        f"逐孔质量流量列表（{M.N_JET} 行）与偏差统计；",
        "沿程压力分段（入口→静压箱→孔口→槽→回液→出口）；",
        "近壁速度云图，标出 HBM 区最大值；",
        "R<sub>θ,c-in</sub>、ΔP、ΔT<sub>f</sub> 三个标量的汇总表（全工况）。",
    ]))

    s.append(h3("10.9　验证与确认（V&V）"))
    s.append(table(
        ["层级", "对比对象", "可接受偏差", "不达标怎么办"],
        [
            ["V1 代码验证", "解析解（层流平板、圆管 f·Re）", "&lt; 2%",
             "换求解器或修正设置"],
            ["V2 与一维对比", "§9 的 ΔT<sub>f</sub>（能量平衡）",
             "&lt; 2%（这是硬约束）",
             "能量不守恒，说明边界或热源加载错误"],
            ["V3 与一维对比", "§9 的压降分段",
             "孔口 &lt; 20%；歧管以 CFD 为准",
             "复核 K 值假设"],
            ["V4 与文献对比", "Martin 阵列关联式（在其有效域内的算例）",
             "&lt; 15%",
             "先跑一个 Re = 3000 的算例落在有效域内做交叉验证"],
            ["V5 与试验确认", "TTV 实测 R<sub>θ,c-in</sub>", "&lt; 15%",
             "触发 §4.2 的 R2 回路，反标定模型"],
        ]))
    s.append(note(
        "<strong>V4 是本项目特有的必要步骤。</strong>"
        f"因为设计点 Re = {A['jet']['Re']:.0f} 在关联式有效域之外，"
        "无法直接用文献校验。"
        "解决办法：<strong>额外跑一个 Re ≈ 3000 的算例</strong>"
        "（把流量临时提到有效域内），"
        "先证明 CFD 设置能复现 Martin 关联式，"
        "再用同一套设置外推到设计点。"
        "这一步不做，CFD 结果就没有可信度锚点。", "risk"))

    s.append(h3("10.10　仿真交付物清单"))
    s.append(ol([
        "仿真需求符合性矩阵（逐条对照 §10.1 Q1–Q8）；",
        "网格无关性研究报告（三套网格）；",
        "湍流模型敏感性报告（转捩 SST vs 层流）；",
        "全工况结果汇总表（§10.7 C01–C12）；",
        "§10.8 的六类后处理图；",
        "V&V 报告（§10.9 V1–V4，V5 待样件）；",
        "对 §9 一维模型的修正建议（哪个模型更接近真值、经验系数取值）；",
        "对 §8 几何的修改建议（孔径、槽深、歧管形状）。",
    ]))
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch11_test():
    s = ['<section id="test">']
    s.append(h2("11.", "试验与验收", "test"))
    s.append(lead(
        "试验分三层：<strong>出厂检验</strong>（每件）、"
        "<strong>型式试验</strong>（首件 / 设计验证）、"
        "<strong>系统验收</strong>（装机后 SAT）。"
        "三层的判据不能互相替代。"))

    s.append(h3("11.1　出厂检验（100%）"))
    s.append(table(
        ["#", "项目", "方法", "判据"],
        [
            ["1", "外观与外形", "目视 + 卡尺",
             f"{G['plate_L']:.0f}×{G['plate_W']:.0f} ±0.15；无磕碰"],
            ["2", "接触面平面度与粗糙度", "三坐标 / 轮廓仪",
             "平面度 ≤0.05 mm；Ra ≤0.8 μm"],
            ["3", "密封性", "氦质谱检漏",
             f"100% 检；{MC['p_test']/1e5:.0f} bar 保压"],
            ["4", "流阻", "水、40 °C 流量–压降曲线",
             f"{A['Q']:.1f} L/min 下 ΔP ≤ {G['dP_target']:.0f} kPa"],
            ["5", "喷嘴通畅性", "流量一致性或气流检查",
             "无堵孔；总流量偏差 ≤ ±5%"],
        ]))

    s.append(h3("11.2　型式试验（首件 / 设计验证）"))
    s.append(table(
        ["#", "项目", "方法", "判据", "对应设计目标"],
        [
            ["T1", "热阻", "TTV 等效加热块（两块 25×25 mm 模拟双 die + "
             "八块小加热块模拟 HBM），水 40 °C、"
             f"{A['Q']:.1f} L/min、{A['P']:.0f} W",
             f"R<sub>θ,c-in</sub> &lt; {A['target']} °C/W",
             "§1.2 热-1"],
            ["T2", "均温性", "两加热区温差 + 红外",
             "两 die 中心温差 ≤ 5 K", "§1.2 热-3"],
            ["T3", "驻点对位", "红外热像",
             "两驻点对准 die 中心；HBM 区<strong>无射流冷斑网格</strong>",
             "§5.2"],
            ["T4", "分区流量", "分区流量计",
             "GPU : HBM = 80 : 20 ±10%", "§1.2 水力-4"],
            ["T5", "包络工况", f"{B['P']:.0f} W 仿真 + 试验校核",
             f"R ≤ {B['target']} °C/W；<strong>不写入首批保证</strong>",
             "§1.2 热-2"],
            ["T6", "PG25 复测", "同几何换工质",
             "记录流量与热阻修正量（预期 h −29%）", "§9.9"],
            ["T7", "耐久与堵塞", "循环 + 颗粒注入",
             "压差上升率可接受；无不可恢复堵塞", "§12"],
            ["T8", "压装影响", f"{MC['p_test']/1e5:.0f} bar + 压装力下"
             "平面度与热阻复测",
             "热阻变化 ≤ 5%；无永久变形", "§6.4"],
        ], widths=["6%", "12%", "32%", "34%", "16%"]))

    s.append(h3("11.3　系统验收（SAT）"))
    s.append(ul([
        "只验证本板落在 OEM 分流后的<strong>实际流量–压降点</strong>，"
        "以及该点下的壳温；",
        "<strong>不得</strong>在冷板厂用 10 K 温升公式出系统报告；",
        "整柜 25–45 °C ↔ 59–177 L/min 是机柜表，单板指标由托盘分流决定，"
        "必须实测。",
    ]))
    s.append(note(
        "<strong>在输入未闭合前可以做的事：</strong>"
        "按 §8 几何出 1:1 铜样和透明流道样（PMMA 盖板），"
        "用两块 25×25 mm 加热块模拟双 die、八块小加热块模拟 HBM，"
        "先把热阻量级、流量分配与可制造性打通。"
        "透明样件可以直接用 PIV 或染色法验证 §9.5 的流动拓扑争议"
        "（cell 还是 bank），成本远低于 CFD。", "ok"))
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch12_risk():
    s = ['<section id="risk">']
    s.append(h2("12.", "风险登记册", "risk"))
    s.append(p("等级 = 影响 × 概率。<strong>红</strong>需在 DR3 前关闭，"
               "<strong>橙</strong>需有缓解措施并监控。"))
    s.append(table(
        ["编号", "风险", "影响", "概率", "等级", "缓解措施", "责任阶段"],
        [
            ["RK-01",
             "热阻真值落在保守端，DP-A 无法达标",
             "高（产品不可交付）", "中", '<span class="bad">红</span>',
             "① CFD 收窄区间；② TIM2 升级到 ≤0.004；"
             "③ 孔径 0.50→0.40 mm；④ 必要时提流量",
             "DR3"],
            ["RK-02",
             f"射流 Re = {A['jet']['Re']:.0f} 在关联式有效域外，"
             "一维预测系统性偏差",
             "高（设计依据不可靠）", "高", '<span class="bad">红</span>',
             "§10.9 V4：额外跑 Re≈3000 算例做关联式锚定",
             "DR3"],
            ["RK-03",
             "HBM 实际为 12 组（§2.3 口径冲突）",
             "中（HBM 区须重画）", "低", '<span class="warn2">橙</span>',
             "以电气宽度 8192-bit 判定为 8 组；索取 OEM 封装图确认",
             "DR0 / C-02"],
            ["RK-04", "喷嘴堵塞",
             "高（热点失守）", "中", '<span class="warn2">橙</span>',
             f"孔径取 {G['D_jet']:.2f} mm（非更小）；系统过滤 ≤25 μm；"
             "跨板压差监测；结构预留拆芯凸台",
             "设计 + 运维"],
            ["RK-05", "钎料流入 0.40 mm 槽造成堵塞",
             "高（整板报废）", "中", '<span class="warn2">橙</span>',
             "钎料做成空心框、远离细槽；X-ray / CT 抽检；焊后流阻筛查",
             "工艺"],
            ["RK-06", "交叉流把下游驻点吹偏",
             "中（均温变差）", "中", '<span class="warn2">橙</span>',
             "短槽 L≤8 mm + 回液缝错排；CFD Q5 验证",
             "DR3"],
            ["RK-07", "压装偏载传到 HBM 焊球",
             "高（芯片损伤）", "低", '<span class="warn2">橙</span>',
             "隔离肋参与承载并与加强环对位；HBM 区压强低于 GPU 区；"
             "ICD 明确压装力",
             "DR3 / ICD"],
            ["RK-08", "PG25 性能损失比预期大（实算 −29%）",
             "中（需重定流量）", "中（若项目选 PG25）",
             '<span class="warn2">橙</span>',
             "§9.9 已量化；PG25 单独定流量并重做 CFD（C08/C09）",
             "DR3 / 商务"],
            ["RK-09", "单板流量与设计值不符（托盘分流）",
             "中", "中", '<span class="warn2">橙</span>',
             "设计按 2.0 L/min 并给 1.6/2.4 敏感性；SAT 实测确认",
             "SAT"],
            ["RK-10", "槽深 1.5 mm 存在低速死体积（OPT-1）",
             "低（性能与重量略损）", "高", "黄",
             "CFD C12 扫槽深 0.8/1.0/1.5；DR3 决定是否改厚度链",
             "DR3"],
            ["RK-11", "失冷（断流）导致超温",
             "高", "低", '<span class="warn2">橙</span>',
             "<strong>不承诺保证秒数</strong>；"
             "行业经验约 90 s 仅作参考，非 NVIDIA 官方指标；"
             "由系统侧冗余保障",
             "系统"],
        ], widths=["7%", "18%", "12%", "9%", "8%", "31%", "15%"]))
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch13_open():
    s = ['<section id="open">']
    s.append(h2("13.", "开放项：开模 / 送样前必须关闭", "open"))
    s.append(table(
        ["编号", "项", "当前状态", "关闭条件", "关闭前的影响", "门"],
        [
            ["C-01", "B300 封装外形、螺钉位、TIM 窗、die 坐标",
             '<span class="bad">缺失</span>',
             "OEM 封装图或 SXM ICD",
             "§8.1 全部坐标为候选，图纸不能投产", "DR0"],
            ["C-02", "官方热图（两 die + HBM 功率分布、堆叠数）",
             '<span class="bad">缺失</span>',
             "NVIDIA / OEM power map",
             "AS-1/2/3/5 无法替换；CFD 热源只能用假设分布", "DR0"],
            ["C-03", "单板额定流量与压降窗",
             '<span class="bad">缺失</span>',
             "托盘分流计算 + 机柜表",
             f"{A['Q']:.1f} L/min 为候选；所有性能结论随之浮动", "DR0"],
            ["C-04", "UQD 型号、水嘴方向、压装力",
             '<span class="bad">缺失</span>', "订单 ICD",
             "§6.4 载荷路径与 §8 水嘴位置不能定稿", "DR1"],
            ["C-05", "工质（DI 水 vs PG25）与缓蚀方案",
             '<span class="warn2">待商务</span>', "订单",
             "若选 PG25 需按 §9.9 重定流量", "DR2"],
            ["C-06", "保证点写 1100 还是兼 1400",
             '<span class="warn2">待商务</span>', "商务决策",
             "本设计默认<strong>只保证 1100 W</strong>", "DR2"],
            ["C-07", "共轭 CFD 完成并达标",
             '<span class="bad">未做</span>',
             "§10 全部交付物 + V&V 通过",
             "<strong>热性能不判定，不得开量产模具</strong>", "DR3"],
            ["C-08", "TIM2 选型与实测面积热阻",
             '<span class="bad">缺失</span>', "TIM 供应商样品实测",
             f"§9.11 显示 TIM2 决定能否达标", "DR3"],
            ["C-09", "首件 TTV 实测热阻",
             '<span class="bad">未做</span>', "§11.2 T1–T4 通过",
             "无实测锚点，模型不确定性无法消除", "DR4"],
            ["C-10", "正式 FTO（自由实施）检索",
             '<span class="warn2">仅初筛</span>',
             "对 Intel DLMJ、US12029008B2、US10244654、CN111328245B、"
             "CN113871359A、WO2026103052A1 等做权利要求对照",
             "存在侵权风险，不能量产",
             "DR3"],
            ["OPT-1", "GPU 槽深优化（1.5 → 0.8–1.0 mm）",
             '<span class="warn2">已识别</span>',
             "CFD C12 结果",
             "当前保留 1.5 mm 以保图纸自洽", "DR3"],
        ], widths=["7%", "22%", "11%", "26%", "24%", "6%"]))
    s.append(note(
        "<strong>C-01 至 C-03 是三块地基。</strong>"
        "它们不闭合，本报告的几何与性能结论就只能是候选方案。"
        "但这不意味着现在什么都做不了 —— 见 §11.3 的注："
        "1:1 铜样 + 透明流道样 + TTV 加热块可以在输入闭合前"
        "把方案的物理可行性、流量分配和可制造性全部打通。", "risk"))
    s.append("</section>")
    return "".join(s)


# ============================================================
def ch14_refs():
    s = ['<section id="refs">']
    s.append(h2("14.", "来源、局限与版本", "refs"))

    s.append(h3("14.1　一次来源（官方）"))
    s.append(ol([
        "NVIDIA，<em>Inside NVIDIA Blackwell Ultra: The Chip Powering the "
        "AI Factory Era</em>，NVIDIA Technical Blog。"
        "双 reticle die、NV-HBI 10 TB/s、208B 晶体管、TSMC 4NP、160 SM / "
        "8 GPC / 640 第五代 Tensor Core、288 GB HBM3E / 8 TB/s、"
        "八组 12-Hi 堆叠 + 16×512-bit 控制器（8192-bit）、"
        "NVLink 5 1.8 TB/s、NVLink-C2C 900 GB/s、PCIe Gen6 ×16、"
        "最大 TGP up to 1400 W；"
        "Grace Blackwell Ultra 超级芯片 1 CPU + 2 GPU、1 TB 统一内存。"
        "<strong>注：该文末尾有 HBM 堆叠数更正声明，见 §2.3 辨析。</strong>",

        "NVIDIA，<em>GB300 NVL72</em> 产品页与 <em>Blackwell Ultra "
        "Datasheet</em>。72 GPU + 36 Grace、2592 Arm Neoverse V2 核、"
        "NVLink 130 TB/s、快速内存 37 TB、GPU 内存 20 TB / 最高 576 TB/s、"
        "CPU 内存 17 TB LPDDR5X、FP4 1440 PFLOPS（稀疏）/ "
        "1080 PFLOPS（稠密）、1.44 exaFLOPS、全液冷机架级架构；"
        "数据手册另有 279 GB HBM3E 口径。",

        "Lenovo Press LP2357。B300 SXM DLC TGP <strong>1100 W</strong>；"
        "GB300 NVL72 135 kW TDP / 155 kW EDP；"
        "Table 27 温度–流量–压降对应表（25–45 °C ↔ 59–177 L/min，"
        "16–127 kPa）；HBM 288 GB / 7.7 TB/s（该页口径）。",
    ]))

    s.append(h3("14.2　本仓库上游文件"))
    s.append(ol([
        "《NVIDIA GB300 NVL72 冷却系统总体设计报告 v2.2》"
        "—— 整柜热负荷、液风分担、机柜水力口径。",
        "《AI 算力芯片液冷冷板专利分析报告 v1.4》"
        "—— 方案 A 权项结构（GPU 射流 / HBM 禁射流 / 隔离肋 / 压降窗）、"
        "已公开杂交架构清单与规避要点、加工工艺三分流。",
        "《AI 算力芯片液冷冷板技术调查分析报告 v1.3》"
        "—— 射流三区、H/D 与 S/D 设计窗、微通道强化综述、行业热阻标尺。",
    ]))

    s.append(h3("14.3　关联式与文献"))
    s.append(ol([
        "Martin, H. (1977), <em>Heat and Mass Transfer between Impinging "
        "Gas Jets and Solid Surfaces</em>, Advances in Heat Transfer. "
        "—— 圆孔阵列面平均换热关联式，本报告模型 B。"
        "<strong>有效域 2000 ≤ Re ≤ 10⁵</strong>。",
        "Shah, R.K. & London, A.L., <em>Laminar Flow Forced Convection in "
        "Ducts</em>. —— 矩形通道层流 f·Re 与 Nu，本报告模型 C。",
        "Hussain et al., <em>Energies</em> 2021 —— 射流三区与 H/D 影响"
        "（图 5-4、5-5 原图来源）。",
        "SciOpen 2025 微通道强化换热综述 —— 盖板 + 微通道封合结构"
        "（图 6-2 原图来源）。",
        "arXiv:2604.10941 —— GB200 模组非均匀热图（图 2-2 原图来源）。",
        "OCP / Meta 公开资料 —— TIM2 面积热阻 0.1–0.2 °C·cm²/W。",
    ]))

    s.append(h3("14.4　局限声明"))
    s.append(note(
        "<strong>一、输入局限。</strong>"
        "B300 封装坐标、官方 power map、单板 ICD 流量三项均未获得。"
        "§2.5、§8.1 的几何与 §9 的计算是候选设计，"
        "用于评审和打样，<strong>不能直接作为采购保证</strong>。<br><br>"
        "<strong>二、模型局限。</strong>"
        f"设计点射流 Re<sub>D</sub> = {A['jet']['Re']:.0f} 低于 Martin 1977 "
        "下限 2000，模型 B 不采用。"
        f"壳–进液只用短槽模型，R_conv = {A['con']['R']:.4f} °C/W。"
        "<strong>本报告因此不给出由 Martin 外推的热阻单值</strong>。<br><br>"
        "<strong>三、状态局限。</strong>"
        "三维仿真未做，样件未做，FTO 仅初筛。"
        "本文件不是 NVIDIA / Lenovo 订单 ICD，不是 FAT 保证书，"
        "不构成侵权风险结论。", "risk"))

    s.append(h3("14.5　版本变更记录"))
    s.append(table(
        ["版本", "日期", "主要变更"],
        [
            ["v1.0 / v1.1", "2026-09-13",
             "首版。提出分区杂交方案、几何候选、0 维估算与图纸清单。"],
            ["<strong>v2.0</strong>", "<strong>2026-09-14</strong>",
             "<strong>结构重构 + 数值修正版：</strong>"
             "① 按设计目标 / 芯片规格 / 设计输入 / 设计流程 / 性能设计 / "
             "机械设计 / 原理图 / 详细设计 / 一维计算 / 三维仿真需求 "
             "重新编排，消除 v1.x 中“工作原理”与第 3、6、7 章的大量重复；"
             "② <strong>修复全部图片失效</strong>"
             "（v1.x 在 design/ 下引用 assets/ 但该目录只存在于 patent/）；"
             "③ 全部工程图改为<strong>按毫米真比例的矢量图</strong>，"
             "含尺寸标注、标题栏、剖切符号、三视图、爆炸图；"
             "④ <strong>数值全部由脚本生成</strong>"
             "（<code>calc/model.py</code>），消除手抄不一致；"
             "⑤ <strong>纠正槽内流动拓扑错误</strong>："
             "v1.x 的 bank 模型（0.74 m/s）与射流冲击不自洽，"
             "改为 cell 模型并说明槽是肋而非导管（§9.5）；"
             "⑥ <strong>指出 Re 低于关联式有效域</strong>，"
             "热阻改为给区间而非单值，结论由“可行”改为“方案通过、性能待证”"
             "（§9.4）；"
             "⑦ <strong>PG25 损失由假设 15% 修正为实算 29%</strong>（§9.9）；"
             "⑧ 新增尺寸链闭合校核、机械承压校核、孔径敏感性、"
             "差距闭合矩阵、CFD 需求规格书、风险登记册；"
             "⑨ 新增 HBM 堆叠数（8 vs 12）口径辨析（§2.3）。"],
        ], widths=["10%", "12%", "78%"]))
    s.append("</section>")
    return "".join(s)


# ============================================================
def appendix():
    s = ['<section id="appx">']
    s.append(h2("附录", "符号表与复算说明", "appx"))
    s.append(h3("A　符号表"))
    s.append(table(
        ["符号", "含义", "单位", "本设计取值 / 来源"],
        [
            ["P", "芯片功率（TGP）", "W",
             f"{A['P']:.0f}（DP-A）/ {B['P']:.0f}（DP-B）"],
            ["Q", "体积流量", "L·min⁻¹", f"{A['Q']:.1f} / {B['Q']:.1f}"],
            ["ṁ", "质量流量", "kg·s⁻¹",
             f"{M.mass_flow(M.WATER40, A['Q']):.4f}"],
            ["D", "喷嘴孔径", "mm", f"{G['D_jet']:.2f}"],
            ["Sx × Sy", "喷嘴节距（沿 27 mm × 沿 28 mm）", "mm",
             f"{G['S_jet_x']:.1f} × {G['S_jet_y']:.1f}"],
            ["H", "喷距（孔板到靶面）", "mm", f"{G['H_jet']:.1f}"],
            ["N", "喷嘴总数", "—", f"{M.N_JET}（每 die {G['n_jet_per_die']}）"],
            ["f", "相对喷嘴面积 (πD²/4)/(Sx·Sy)", "—", f"{M.F_AREA:.5f}"],
            ["D<sub>h</sub>", "水力直径", "mm",
             f"GPU 槽 {M.DH_CH*1e3:.4f}；HBM 槽 {M.DH_HBM*1e3:.3f}"],
            ["Re<sub>D</sub>", "孔雷诺数 ρVD/μ", "—",
             f"{A['jet']['Re']:.0f}（DP-A）"],
            ["Pr", "普朗特数 μc<sub>p</sub>/k", "—",
             f"水 {M.WATER40.Pr:.2f}；PG25 {M.PG25_40.Pr:.2f}"],
            ["Nu", "努塞尔数 hD/k 或 hD<sub>h</sub>/k", "—", "见 §9.4"],
            ["h", "对流换热系数", "W·m⁻²K⁻¹", "见 §9.4 三模型"],
            ["η<sub>f</sub>", "肋效率 tanh(mL)/mL", "—",
             f"{A['con']['eta']:.3f}"],
            ["R<sub>θ,c-in</sub>", "壳–进液热阻", "°C/W",
             f"{A['R_lo']:.4f} – {A['R_hi']:.4f}"],
            ["R<sub>pkg</sub>", "封装内热阻（硅+TIM1+盖）", "°C/W",
             f"{M.R_PKG[0]}–{M.R_PKG[1]}（假设）"],
            ["R<sub>TIM2</sub>", "TIM2 热阻", "°C/W",
             f"{M.R_TIM2[0]}–{M.R_TIM2[1]}（假设）"],
            ["T<sub>f</sub> / T<sub>w</sub> / T<sub>j</sub>",
             "流体 / 壁面 / 结温", "°C", "见 §7.3"],
            ["ΔT<sub>f</sub>", "流体混合温升", "K",
             f"{A['dTf']:.2f}（DP-A）"],
            ["ΔP", "压降", "kPa",
             f"板内 {A['dp']['total'][0]/1000:.1f}–"
             f"{A['dp']['total'][1]/1000:.1f}"],
            ["K", "孔口局部阻力系数", "—", f"{M.K_ORIFICE}"],
            ["q″", "热流密度", "W·cm⁻²",
             f"die 面均 {A['q_die']:.1f}（DP-A）"],
            ["k<sub>Cu</sub>", "铜导热率", "W·m⁻¹K⁻¹", f"{M.K_CU:.0f}"],
        ]))

    s.append(h3("B　复算与再生成"))
    s.append(table(
        ["文件", "作用"],
        [
            ["<code>calc/model.py</code>",
             "<strong>唯一数值来源</strong>：物性、几何、关联式、工况求解"],
            ["<code>calc/cp_b300_1d.py</code>",
             "一维计算书，输出 <code>cp_b300_1d_out.txt</code>"],
            ["<code>calc/svg.py</code>",
             "SVG 原语：工程尺寸标注、剖面填充、等轴测投影"],
            ["<code>calc/figures.py</code>",
             "详细设计图纸（三视图 / 流道 / 剖面 / 单元 / 孔位 / 3D / 爆炸）"],
            ["<code>calc/figures2.py</code>",
             "原理图、流程图与数据图"],
            ["<code>calc/report_a.py</code> / "
             "<code>report_b.py</code>", "报告正文章节"],
            ["<code>calc/build_report.py</code>",
             "装配并输出本 HTML 文件"],
        ]))
    s.append(note(
        "<strong>复算命令：</strong><br>"
        "<code>cd design/calc</code><br>"
        "<code>set PYTHONIOENCODING=utf-8</code><br>"
        "<code>python cp_b300_1d.py &gt; cp_b300_1d_out.txt</code>"
        "　（生成计算书）<br>"
        "<code>python build_report.py</code>　（重新生成本报告）<br><br>"
        "改变 <code>model.py</code> 中的几何或设计点后重新运行，"
        "报告全文数值、表格与图形会同步更新 —— "
        "<strong>不存在需要手工同步的数字</strong>。", "ok"))
    s.append("</section>")
    return "".join(s)

"""组装 papers-jet 登记条目 → entries.json；file 块取自 downloads.log.jsonl；做 schema 关键规则自检。"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
LIB = HERE.parents[1]
TODAY = "2026-10-02"
VALID = "2027-10-02"
BY = "papers-jet 子智能体"

log = {}
for line in (LIB / "_staging" / "downloads.log.jsonl").read_text(encoding="utf-8").splitlines():
    if line.strip():
        r = json.loads(line)
        log[r["id"]] = r

PAY = "机构订阅 / 单篇购买 / 联系作者索取作者版"
E = []


def add(**kw):
    kw.setdefault("language", "en")
    kw.setdefault("retrieved_by", BY)
    kw.setdefault("last_verified", TODAY)
    kw.setdefault("valid_until", VALID)
    kw.setdefault("status", "active")
    kw.setdefault("benchmark_candidate", False)
    if kw["id"] in log and kw["access"]["status"] == "downloaded":
        r = log[kw["id"]]
        kw["file"] = {k: r[k] for k in ("path", "sha256", "bytes", "pages", "source_url", "downloaded_at")}
    E.append(kw)


def kd(q, v, loc, unit=None, cond=None, vf="fulltext"):
    d = {"quantity": q, "value": v, "locator": loc, "verified_from": vf}
    if unit:
        d["unit"] = unit
    if cond:
        d["condition"] = cond
    return d


# ---------------------------------------------------------------- 已下载全文
add(id="pap-2021-wei-microjet-correlations-feed-drain", type="paper",
    title="Heat transfer and pressure drop correlations for direct on-chip microscale jet impingement cooling with alternating feeding and draining jets",
    title_zh="交替进/排液微射流直接芯片冷却的换热与压降关联式",
    authors=["Tiwei Wei", "Herman Oprins", "Liang Fang", "Vladimir Cherman", "Eric Beyne", "Martine Baelmans"],
    org="imec / KU Leuven", year=2021,
    venue="International Journal of Heat and Mass Transfer 182 (2022) 121865（2021-10-01 在线）",
    identifiers={"doi": "10.1016/j.ijheatmasstransfer.2021.121865"},
    url="https://doi.org/10.1016/j.ijheatmasstransfer.2021.121865",
    access={"status": "downloaded", "license": "出版社版权（Elsevier），作者实验室主页 s-pack.org 公开张贴",
            "redistributable": False, "copyright_note": "仅限内部研究引用，不随仓库分发"},
    trust_level="L2", trust_reason="IJHMT 同行评审；关联式由 >1000 例单元 CFD（transition SST，经 LES 校核）拟合，并用 3 款 3D 打印冷板与 Brunschwiler 硅冷板实测验证",
    stages=[3, 4, 5], topics=["jet-array", "distributed-return", "low-Re", "correlation", "pressure-drop", "k-factor"],
    summary_zh="分布回流（每个进液孔周围 4 个排液孔）微射流阵列的 Nu_f–Re_d 与压降 k 因子无量纲关联式，Re_d 32~2048 覆盖层流-过渡区；Re 指数随 d_i/L 变化。工质固定为 DI 水（Pr=7.56），未含 Pr 依赖。文中 Table 1 汇总了 Martin、Womac、Garimella&Rice、Li&Garimella、Robinson&Schnitzler、Fabbri&Dhir、Michna 等关联式的 Re/H/D 适用范围，可作检索索引。",
    formulas=[
        {"name": "面平均 Nu_f（以 d_i 为特征长度，T_s 为芯片-流体界面平均温度）",
         "latex": r"\overline{Nu}_f=\left(5.64\left(\frac{d_i}{L}\right)^2+0.031\frac{d_i}{L}-0.000632\right)\left(\frac{H}{L}\right)^{-0.29}Re_d^{\,0.48\left(d_i/L\right)^{-0.16}}",
         "validity": "d_i/L=d_o/L=a, 0.01≤a≤0.4；0.01≤H/L≤0.4；32≤Re_d≤2048；0.05≤H/d_i≤20；0.01≤t/L≤0.4；DI 水 Pr=7.56；拟合误差 ±30%；L 为进液孔间距（方阵）",
         "locator": "Eq.(19) p.11（已对照页面图像核对）"},
        {"name": "单元压降 k 因子 k=ΔP/(½ρV_in²)",
         "latex": r"k=\left\{\left(21.2\frac{d_i}{L}+14.5\right)Re_d^{-0.73\left(d_i/L\right)^{-0.26}}\left(2.26\frac{t}{L}+0.89\right)\left(0.37\left(\frac{H}{L}\right)^{0.15}+0.55\right)+0.8\right\}",
         "validity": "d_i/L=d_o/L=a, 0.05≤a≤0.6；0.5≤H/d_i≤20；32≤Re_d≤1024；t/L≥0.1；±30%。注：原文印刷为“0.37 (H/L) 0.15 + 0.55”，0.15 为指数还是乘子有歧义，此处按指数解读，使用前需再核",
         "locator": "Eq.(20) p.11"},
        {"name": "Nu 与 Re 定义", "latex": r"Nu_f=\frac{q\,d_i}{(T_s-T_{in})k_{fl}},\quad Re_d=\frac{\rho d_i \bar V_{in}}{\mu},\quad k=\frac{\Delta P}{\tfrac12\rho\bar V_{in}^2}",
         "validity": "T_ref=T_in", "locator": "Eq.(2)(4)(8) p.5"}],
    key_data=[
        kd("DOE 参数范围", "Re_d=32,64,128,216,512,1024,2048；d_i/L 0.01~0.4；d_o/L 0.05~0.5；t/L 0.1~1.2；H/L 0.05~2", "Table 2 p.6"),
        kd("验证样件几何（实测）", "3×3：L=2.67 mm, d_i=0.95 mm, d_i/L=0.36；4×4：L=2 mm, d_i=0.75 mm, d_i/L=0.375；8×8：L=1 mm, d_i=0.38 mm, d_i/L=0.38；三者 H/L=0.33（H=650 µm）；Brunschwiler：L=0.15 mm, d_i=43 µm, d_i/L=0.287", "Table 3 p.12"),
        kd("热测量合成不确定度", "±1.8", "p.11 §4", unit="%", cond="PTCQ 8×8 mm² 热测试芯片，32×32 二极管；流量计 ±0.2%RD；差压计 <±0.5%FS（0.2~5 bar）"),
        kd("验证 Re 范围", "20~2000", "p.13 §5", cond="d=300~800 µm 自制样件 + 43 µm 硅冷板文献数据")],
    benchmark_candidate=True,
    benchmark_note="关联式经实测验证；可复现几何见 Table 3，但 Nu_j–Re_d 实测点只在 Fig.14/15 图中，需数字化取点。",
    notes="id 年份按在线发表 2021；卷期年份 2022。我方 H/L≈0.67~0.83 超出 Nu 式 H/L≤0.4；Pr 外推需另加修正。")

add(id="pap-2020-wei-nozzle-scaling-distributed-returns", type="paper",
    title="Nozzle scaling effects for the thermohydraulic performance of microjet impingement cooling with distributed returns",
    title_zh="分布回流微射流冷却热-水力性能的喷嘴尺度缩放效应",
    authors=["T.-W. Wei", "H. Oprins", "Liang Fang", "V. Cherman", "I. De Wolf", "E. Beyne", "M. Baelmans"],
    org="imec / KU Leuven", year=2020, venue="Applied Thermal Engineering 180 (2020) 115767",
    identifiers={"doi": "10.1016/j.applthermaleng.2020.115767"}, url="https://doi.org/10.1016/j.applthermaleng.2020.115767",
    access={"status": "downloaded", "license": "出版社版权（Elsevier），作者实验室主页公开张贴", "redistributable": False},
    trust_level="L2", trust_reason="ATE 同行评审，实验 + 经验证的数值模型",
    stages=[2, 3, 4, 5, 7], topics=["jet-array", "distributed-return", "nozzle-density", "COP", "3D-printing"],
    summary_zh="固定 d_i/L=0.3，在 8×8 mm² 热测试芯片上比较 3×3/4×4/8×8 等孔阵（孔密度至 100 cm⁻²），并做 N 到 16×16 的数值缩放；给出恒流量与恒泵功下的最优孔密度（恒流量时 30~300 cm⁻²）。",
    key_data=[
        kd("孔阵设计表", "N1 1×1: 1.56 cm⁻², 单元 8 mm, d=2.4 mm；N2 2×2: 6.25, 4, 1.2；N3 3×3: 14.06, 2.6, 0.8；N4 4×4: 25, 2, 0.6；N6 6×6: 56.25, 1.33, 0.4；N8 8×8: 100, 1, 0.3；N12 12×12: 225, 0.67, 0.2", "Table 1 p.4", cond="d_i/L=0.3；腔高 H=0.6 mm；进液腔 2.5 mm"),
        kd("最低归一化热阻", 0.13, "Abstract p.1；p.12", unit="cm²·K/W", cond="8×8 阵列，1×1 mm² 单元，DI 水 1000 ml/min"),
        kd("热阻测量不确定度", "±1.8", "p.5 §3.1", unit="%"),
        kd("制造偏差", "4×4、8×8 实测孔径与名义值差 <18%，3×3 达 26%", "p.3 §2.2")],
    benchmark_candidate=True,
    benchmark_note="几何（Table 1）+ 流量 + 热阻实测，可做 1D/CFD 对标；H/d 与我方差异较大（H=0.6 mm）。")

add(id="pap-2020-wei-3d-printed-jet-large-die", type="paper",
    title="Demonstration of Package Level 3D-printed Direct Jet Impingement Cooling applied to High power, Large Die Applications",
    title_zh="封装级 3D 打印直接射流冷却在大尺寸高功率芯片上的演示",
    authors=["T.-W. Wei", "H. Oprins", "V. Cherman", "Z. Yang", "K. Rivera", "G. Van der Plas", "B. J. Pawlak", "L. England", "E. Beyne", "M. Baelmans"],
    org="imec / KU Leuven / GlobalFoundries", year=2020, venue="2020 IEEE 70th ECTC, pp.1422-1429",
    identifiers={"doi": "10.1109/ECTC32862.2020.00225"}, url="https://doi.org/10.1109/ECTC32862.2020.00225",
    access={"status": "downloaded", "license": "IEEE 版权；作者实验室主页张贴（PDF 带 IEEE Xplore 授权水印）", "redistributable": False,
            "copyright_note": "仅内部研究参考"},
    trust_level="L2", trust_reason="IEEE ECTC 会议论文，经同行评审（按规则会议默认 L4，ECTC 经同行评审故 L2）",
    stages=[4, 5, 7], topics=["jet-array", "distributed-return", "large-die", "TTV", "bare-die", "lidded"],
    summary_zh="23×23 mm²（530 mm²）热测试芯片上的 3D 打印聚合物分布回流射流冷板：11×11 进液孔 + 12×12 排液孔，孔距 2 mm，孔径 0.6 mm，腔高 0.6 mm；与 B300 的大 die、孔距 2.4~3.0 mm、D=0.4~0.5 mm 最接近的公开实测案例。",
    key_data=[
        kd("几何", "11×11 进液 / 12×12 排液，孔距 2 mm，d=0.6 mm（实测 0.63 mm），腔高 H=0.6 mm", "p.2 §II"),
        kd("平均芯片温升", 17.5, "Abstract p.1；p.3", unit="°C", cond="DI 水 3.25 LPM，裸片，ΔP=0.7 bar，温度不均匀度 6%；功率摘要写 285 W、正文 p.3 写 275 W（原文不一致）"),
        kd("平均热阻", 0.14, "p.4", unit="K/W", cond="1 LPM"),
        kd("每孔流量", 27, "p.4", unit="ml/min", cond="对应 3.25 LPM 总流量；按此推算水 20°C 时 Re_d≈950（推算值，非原文）"),
        kd("TIM 参数（加盖封装）", "大 die 封装：TIM 20 µm, 2.3 W/m·K；2.5D 中介层封装：90 µm, 1.9 W/m·K", "Table 2 p.4"),
        kd("RTD 温度系数标定", "3553±2 ppm/°C（10~70°C）", "p.2-3")],
    benchmark_candidate=True,
    benchmark_note="大 die + 孔阵 + 流量 + ΔT + ΔP 齐全，可直接做 1D/CFD 对标（DI 水，需按 PG25 物性换算）。")

add(id="pap-2020-wei-jet-lidded-lidless-3d-manifold", type="paper",
    title="Experimental and numerical investigation of direct liquid jet impinging cooling using 3D printed manifolds on lidded and lidless packages for 2.5D integrated systems",
    title_zh="2.5D 集成系统加盖/无盖封装上的 3D 打印歧管直接液体射流冷却实验与数值研究",
    authors=["T.W. Wei", "H. Oprins", "V. Cherman", "E. Beyne", "M. Baelmans"], org="imec / KU Leuven", year=2020,
    venue="Applied Thermal Engineering 164 (2020) 114535",
    identifiers={"doi": "10.1016/j.applthermaleng.2019.114535"}, url="https://doi.org/10.1016/j.applthermaleng.2019.114535",
    access={"status": "downloaded", "license": "出版社版权（Elsevier），作者实验室主页公开张贴；另有 KU Leuven Lirias 作者版", "redistributable": False},
    trust_level="L2", trust_reason="ATE 同行评审",
    stages=[4, 5, 7], topics=["jet-array", "lidded-vs-bare-die", "TIM", "manifold", "2.5D"],
    summary_zh="双芯片 2.5D 封装上比较盖上射流与裸片射流；横向进出液歧管比竖直进液节省 60% 泵功、厚度减半。含 TIM 热阻文献值，可用于加盖方案 TIM 预算。",
    key_data=[
        kd("冷板几何", "4×4 进液 / 5×5 排液，d_i=d_o=0.6 mm，腔高 H=0.6 mm，喷嘴板厚 t=0.55 mm，进液腔 2.5 mm", "Table p.5"),
        kd("实测平均孔径", "570±20 µm（名义 600 µm）", "p.7"),
        kd("TIM 热阻率（文献综述值）", "常用脂/凝胶/PCM 低至 10 mm²·K/W；铜纳米弹簧 nanoTIM ~1 mm²·K/W；TIM-热沉界面热阻 2~20 mm²·K/W", "p.2 §1", vf="fulltext"),
        kd("不确定度构成", "功率 ±0.1%、平均芯片温度 ±1.5%、入口温度 ±1%、孔径 ±3.5%", "p.7")],
    benchmark_candidate=True, benchmark_note="几何+流量+热阻完整；热测试芯片 PTCQ。")

add(id="pap-2019-wei-jet-ttv-model-validation", type="paper",
    title="Experimental characterization and model validation of liquid jet impingement cooling using a high spatial resolution and programmable thermal test chip",
    title_zh="用高空间分辨率可编程热测试芯片表征液体射流冷却并验证模型",
    authors=["T.W. Wei", "H. Oprins", "V. Cherman", "G. Van der Plas", "I. De Wolf", "E. Beyne", "M. Baelmans"], org="imec / KU Leuven", year=2019,
    venue="Applied Thermal Engineering 152 (2019) 308-318",
    identifiers={"doi": "10.1016/j.applthermaleng.2019.02.075"}, url="https://doi.org/10.1016/j.applthermaleng.2019.02.075",
    access={"status": "downloaded", "license": "出版社版权（Elsevier），作者实验室主页公开张贴；Lirias 有作者版", "redistributable": False},
    trust_level="L2", trust_reason="ATE 同行评审；TTV 实测与 CFD 对比",
    stages=[5, 7], topics=["TTV", "CFD-validation", "single-jet", "jet-array"],
    summary_zh="8×8 mm² PTCQ 热测试芯片（32×32 二极管，240 µm 分辨率）上做单射流（d=2 mm）与 4×4 分布回流阵列（0.5 mm）实测，与 CFD 比较给出逐点误差，是 CFD 方法验证的直接范例。",
    key_data=[
        kd("单射流平均热阻", 0.32, "p.6", unit="K/W", cond="d=2 mm，600 ml/min（Re_d=4286），模拟压降 0.4 kPa，24 W，T_in=10°C"),
        kd("4×4 阵列平均热阻", 0.25, "p.7", unit="K/W", cond="d=0.5 mm，600 ml/min，50 W，模拟压降 15 kPa"),
        kd("CFD-实测最大误差（单射流）", "芯片边缘 13.4%/8.7%/25.2%，驻点 3.9%/8.8%/10%", "p.7", cond="200/300/600 ml/min"),
        kd("热测量合成不确定度", "±1.8", "p.5", unit="%")],
    benchmark_candidate=True, benchmark_note="可复现几何 + 工况 + 实测热阻 + CFD 误差，适合作 ⑤ CFD 验证基准。")

add(id="pap-2019-wei-chip-level-3d-microjet", type="paper",
    title="Experimental Characterization of a Chip-Level 3-D Printed Microjet Liquid Impingement Cooler for High-Performance Systems",
    title_zh="芯片级 3D 打印微射流液体冲击冷却器实验表征",
    authors=["Tiwei Wei", "Herman Oprins", "Vladimir Cherman", "Shoufeng Yang", "Ingrid De Wolf", "Eric Beyne", "Martine Baelmans"], org="imec / KU Leuven", year=2019,
    venue="IEEE Trans. Components, Packaging and Manufacturing Technology 9(9):1815-1824",
    identifiers={"doi": "10.1109/TCPMT.2019.2905610"}, url="https://doi.org/10.1109/TCPMT.2019.2905610",
    access={"status": "downloaded", "license": "IEEE 版权；作者实验室主页张贴", "redistributable": False},
    trust_level="L2", trust_reason="IEEE 期刊同行评审",
    stages=[4, 5, 7], topics=["jet-array", "distributed-return", "3D-printing", "pressure-drop-breakdown"],
    summary_zh="4×4 阵列（名义 600 µm，实测 575 µm）SLA 打印冷板直接装在裸片上；给出 100~1000 mL/min 的热阻、压降及压降分项（出液腔 57%），CFD 与实测误差 4%~12%。",
    key_data=[
        kd("最低热阻", 0.16, "Abstract p.1；p.9", unit="cm²·K/W", cond="1000 mL/min，ΔP=0.3 bar"),
        kd("平均热阻", "0.45 K/W（0.29 cm²·K/W）", "p.7", cond="600 mL/min"),
        kd("压降分项", "出液腔 57%，进液腔 21%，喷嘴板 22%", "p.8", cond="1000 mL/min"),
        kd("CFD-实测最大误差", "12%（100 mL/min）→ 4%（1000 mL/min）", "p.8"),
        kd("Re_d 研究范围", "10~3500", "p.4")],
    benchmark_candidate=True, benchmark_note="几何 + 流量 + 热阻 + 压降分项完整。")

add(id="pap-2019-wei-microjet-cht-feed-drain", type="paper",
    title="Conjugate Heat Transfer and Fluid Flow Modeling for Liquid Microjet Impingement Cooling with Alternating Feeding and Draining Channels",
    title_zh="交替进/排液通道液体微射流冷却的耦合传热与流动建模",
    authors=["Tiwei Wei", "Herman Oprins", "Vladimir Cherman", "Eric Beyne", "Martine Baelmans"], org="imec / KU Leuven", year=2019,
    venue="Fluids 4(3):145 (MDPI)", identifiers={"doi": "10.3390/fluids4030145"}, url="https://doi.org/10.3390/fluids4030145",
    access={"status": "downloaded", "license": "CC-BY-4.0（MDPI 开放获取）", "redistributable": True},
    trust_level="L2", trust_reason="MDPI Fluids 同行评审；RANS 与 LES 对比",
    stages=[5], topics=["CFD-method", "unit-cell", "LES", "transition-SST", "distributed-return"],
    summary_zh="单元模型 + 全冷板模型的 CHT 方法：RANS transition SST 与 LES 对比，确定 Re_d≈300~2000 过渡区的湍流模型选择与网格（单元模型 RANS 0.4 M 网格 20 µm）。可直接作为我方 ⑤ CFD 设置参考。",
    key_data=[
        kd("模型规模", "全模型 8.5 M/80 µm/24 h；单元 RANS 0.4 M/20 µm/2 h；单元 LES 3 M/1 µm/12 h", "Table p.6"),
        kd("边界条件", "芯片底面恒热流 37.5 W/cm²；d_i=d_o=0.6 mm；8×8 mm² 芯片", "p.4, p.6"),
        kd("电子冷却典型 Re_d", "300~2000（300 mL/min~2 L/min）", "p.3"),
        kd("LES 判定稳态", "Re=2048 时 600 时间步后无速度脉动", "p.7")],
    benchmark_candidate=False, notes="与 Wei 2022 关联式配套，CFD 方法学参考。")

add(id="pap-2018-wei-3d-printed-jet-cooler", type="paper",
    title="3D Printed Liquid Jet Impingement Cooler: Demonstration, Opportunities and Challenges",
    title_zh="3D 打印液体射流冷却器：演示、机遇与挑战",
    authors=["T.-W. Wei", "H. Oprins", "V. Cherman", "S. Yang", "I. De Wolf", "E. Beyne", "M. Baelmans"], org="imec / KU Leuven", year=2018,
    venue="2018 IEEE 68th ECTC, pp.2389-2396", identifiers={"doi": "10.1109/ECTC.2018.00360"}, url="https://doi.org/10.1109/ECTC.2018.00360",
    access={"status": "downloaded", "license": "KU Leuven Lirias 作者提交版（other-oa）", "redistributable": False},
    trust_level="L2", trust_reason="IEEE ECTC 经同行评审会议论文",
    stages=[2, 3, 6], topics=["3D-printing", "design-guideline", "nozzle-diameter", "manufacturability"],
    summary_zh="3D 打印射流冷板设计准则：材料选择、进液腔厚度、临界孔径与结构完整性；d_i/L 0.025~0.4 的优化在 530 mL/min 恒流量下进行，指出热性能在孔径约 100 µm 量级趋于饱和。",
    key_data=[kd("优化工况", "恒流量 530 mL/min；d_i/L 0.025~0.4；孔径 0.2~1 mm 扫描", "p.2-3"),
              kd("材料对比", "Cu / Si / 塑料，流量 50~600 ml/min", "p.4")],
    benchmark_candidate=False)

add(id="pap-2009-whelan-nozzle-geometry-jet-array", type="paper",
    title="Nozzle geometry effects in liquid jet array impingement", title_zh="液体射流阵列冲击中的喷嘴几何效应",
    authors=["Brian P. Whelan", "Anthony J. Robinson"], org="Trinity College Dublin", year=2009,
    venue="Applied Thermal Engineering 29(11-12):2211-2221", identifiers={"doi": "10.1016/j.applthermaleng.2008.11.003"},
    url="https://doi.org/10.1016/j.applthermaleng.2008.11.003",
    access={"status": "downloaded", "license": "HAL 存储的 Elsevier 录用稿（PEER 项目）", "redistributable": False},
    trust_level="L2", trust_reason="ATE 同行评审（录用稿版本）",
    stages=[3, 4, 7], topics=["jet-array", "confined-submerged", "free-surface", "nozzle-geometry", "pressure-drop", "water"],
    summary_zh="45 孔、d=1 mm、S/d=5 的水射流阵列，比较直孔/倒角/圆角等 6 种喷嘴，在淹没受限（H/d=2）与自由表面（H/d=20）下测 Nu_L 与摩擦系数；复核 Robinson & Schnitzler 2007 关联式，认为其淹没式可用到 Re≈10000。",
    formulas=[
        {"name": "Robinson & Schnitzler 2007 淹没受限阵列关联式（转引）",
         "latex": r"\frac{Nu_L}{Pr^{0.4}}=23.39\,Re_{d_n}^{0.46}\left(\frac{S}{d_n}\right)^{-0.442}\left(\frac{H}{d_n}\right)^{-0.00716}",
         "validity": "水，d_n=1 mm，650≤Re≤6500（本文认为可到 ~10000），2≤H/d_n≤3，3≤S/d_n≤7；Nu_L 以加热面特征长度 L_c=D/2=15.75 mm 定义（非孔径）",
         "locator": "Eq.(2) p.10；L_c 定义 Eq.(6) p.16"},
        {"name": "Robinson & Schnitzler 2007 自由表面阵列关联式（转引）",
         "latex": r"\frac{Nu_L}{Pr^{0.4}}=7.8\,Re_{d_n}^{0.49}\exp\left(-0.025\frac{S}{d_n}\right)", "validity": "自由表面水射流，同上", "locator": "Eq.(1) p.10"},
        {"name": "喷嘴摩擦系数定义", "latex": r"f=\frac{\Delta P}{\tfrac12\rho V_n^2}\cdot\frac{d_n}{t}", "validity": "t=喷嘴板厚 3 mm", "locator": "Eq.(9) p.16"}],
    key_data=[
        kd("试件几何", "45 孔，d_n=1.0 mm，S=5 mm（S/d_n=5），喷嘴板 t=3 mm，加热面 Ø31.5 mm 无氧铜，名义热流 25.66 W/cm²", "Abstract p.2；p.13-14"),
        kd("淹没受限工况", "H/d_n=2；Re 约 1000~10000", "p.2；p.17"),
        kd("实验不确定度", "Nu_L 7%（2 LPM）/5%（9 LPM）；f 10%~20%；另列 12%", "Table 2 p.41（数值与列对应需对照原表）"),
        kd("自由表面积液失效", "体积流量 >~10 L/min（Re~5000）时加热面积液，换热下降", "p.18")],
    benchmark_candidate=True, benchmark_note="水、d=1 mm、S/d=5、H/d=2 阵列 Nu–Re 与 f–Re 实测（Fig.3/4 需数字化）；Re 下限接近我方。")

add(id="pap-1995-lienhard-liquid-jet-impingement", type="paper",
    title="Liquid Jet Impingement", title_zh="液体射流冲击（综述）", authors=["John H. Lienhard V"], org="MIT", year=1995,
    venue="Annual Review of Heat Transfer 6:199-270 (Begell House)", identifiers={"doi": "10.1615/AnnualRevHeatTransfer.v6.60"},
    url="https://doi.org/10.1615/AnnualRevHeatTransfer.v6.60",
    access={"status": "downloaded", "license": "作者 MIT 个人主页公开扫描件（版权归 Begell House）", "redistributable": False},
    trust_level="L2", trust_reason="经同行评审的年度综述",
    stages=[3, 4], topics=["review", "free-surface-jet", "stagnation-zone", "laminar-jet"],
    summary_zh="无淹没（自由表面）液体射流冲击换热综述，含层流/湍流驻点区与下游区关联式、平面射流与飞溅。我方为淹没受限射流，只作驻点区层流理论与 Pr 依赖的参考。",
    key_data=[], benchmark_candidate=False,
    notes="PDF 为扫描件无文字层（fitz 仅取到约 2300 字符），关联式未提取；需 OCR 或人工阅读后补 formulas。")

# ---------------------------------------------------------------- 开放获取但自动下载被拦（待用户浏览器下载）
PU = "Purdue e-Pubs（CTRC Research Publications）公开作者版；自动请求返回 HTTP 403，请在浏览器打开 URL 手动下载后放入 files/papers/<id>.pdf 并补 sha256"
add(id="pap-2001-li-garimella-prandtl-jet", type="paper",
    title="Prandtl-number effects and generalized correlations for confined and submerged jet impingement",
    title_zh="受限淹没射流冲击的 Pr 效应与通用关联式", authors=["Chin-Yuan Li", "Suresh V. Garimella"], org="Purdue University", year=2001,
    venue="International Journal of Heat and Mass Transfer 44(18):3471-3480", identifiers={"doi": "10.1016/S0017-9310(01)00003-5"},
    url="https://docs.lib.purdue.edu/coolingpubs/64/",
    access={"status": "pending_user", "license": "Purdue e-Pubs 作者版（版权 Elsevier）", "redistributable": False, "how_to_get": PU + "：https://docs.lib.purdue.edu/cgi/viewcontent.cgi?article=1061&context=coolingpubs"},
    trust_level="L2", trust_reason="IJHMT 同行评审",
    stages=[3, 4], topics=["single-jet", "confined-submerged", "Prandtl-effect", "correlation", "FC-77", "water", "air"],
    summary_zh="空气/水/FC-77 单孔受限淹没射流，提出覆盖 Pr 0.7~25.2 的驻点与面平均 Nu 通用关联式，Pr 指数由拟合得到（约 0.44），是 PG25 高 Pr 修正的首选依据；但 Re 下限 4000（湍流），我方 Re≈478 远低于下限。",
    formulas=[{"name": "液体驻点 Nu₀（Liquids 通用式）",
               "latex": r"Nu_0=1.409\,Re^{0.497}\,Pr^{0.444}\left(\frac{l}{d}\right)^{0.058}\left(\frac{D_e}{d}\right)^{-0.272}",
               "validity": "d 1.59~6.35 mm；Pr 7.1~25.2；Re 4000~23000；H/d 1~5；l/d 0.25~12；D_e=11.28 mm；物性按膜温；平均(最大)偏差 9.27%(26.69%)。⚠ 网页文本丢失负号：(l/d)、(D_e/d) 指数符号待对照 PDF 核对（D_e/d 取负号的依据：文中称 Nu₀ 随 d 增大而增大）",
               "locator": "Table 1 Eq.(8)"},
              {"name": "全流体驻点 Nu₀（All fluids）", "latex": r"Nu_0=1.427\,Re^{0.496}\,Pr^{0.444}\left(\frac{l}{d}\right)^{0.058}\left(\frac{D_e}{d}\right)^{-0.272}",
               "validity": "Pr 0.7~25.2；Re 4000~23000；H/d 1~5；偏差 9.08%(27.12%)；符号同上待核", "locator": "Table 1 Eq.(9)"}],
    key_data=[kd("h 不确定度", "<5%（20:1）", "§Experiments（Purdue 作者版全文，经网页文本读取）", cond="主要来自加热面积 ~4%；温度 ±0.3°C"),
              kd("加热器", "10×10 mm² 不锈钢箔 0.075 mm", "§Experiments"),
              kd("面平均式系数（Liquids, Eq.13）", "1.064 / 1.291，指数 Re 0.513 / 0.630，Pr 0.441，l/d 0.071，D_e/d 0.266 / 1.063，含 A_r 分区；结构需对照 PDF", "Table 2 Eq.(13)")],
    benchmark_candidate=False,
    notes="全文经 WebSearch 抓取 Purdue 公开 PDF 文本读取（非本地文件），公式符号存疑处已标注；verified_from 记为 fulltext（网页文本）。")

add(id="pap-2006-lee-garimella-developing-microchannel", type="paper",
    title="Thermally developing flow and heat transfer in rectangular microchannels of different aspect ratios",
    title_zh="不同宽高比矩形微通道的热发展流动与换热", authors=["Poh-Seng Lee", "Suresh V. Garimella"], org="Purdue University", year=2006,
    venue="International Journal of Heat and Mass Transfer 49(17-18):3060-3067", identifiers={"doi": "10.1016/j.ijheatmasstransfer.2006.02.011"},
    url="https://docs.lib.purdue.edu/coolingpubs/23/",
    access={"status": "pending_user", "license": "Purdue e-Pubs 作者版（版权 Elsevier）", "redistributable": False, "how_to_get": PU + "：https://docs.lib.purdue.edu/cgi/viewcontent.cgi?article=1014&context=coolingpubs"},
    trust_level="L2", trust_reason="IJHMT 同行评审（数值）",
    stages=[3, 4], topics=["microchannel", "thermally-developing", "laminar", "H1", "correlation"],
    summary_zh="宽高比 1~10 的矩形微通道层流热发展区（H1 边界）局部与平均 Nu 通用关联式及热入口长度式；HBM 通道 0.45×2.00 mm（α≈4.4）与 Grace 通道 0.40×1.20 mm（α=3）均在范围内。",
    formulas=[{"name": "平均 Nu（热发展区）",
               "latex": r"Nu_{m}=\frac{1}{C_1\,(x^*)^{C_2}+C_3}+C_4,\quad x^*=\frac{x}{Re\,Pr\,D_h}",
               "validity": "1≤α≤10，层流，H1 边界，x*<x*_th；C1=(2.757e-3)α³,(3.274e-2)α²,(7.464e-5)α,4.476 四项组合；C2=0.6391；C3=(1.604e-4)α²,(2.622e-3)α,(2.568e-2)；C4=7.301,(13.11)/α,(15.19)/α²,(6.094)/α³。⚠ 网页文本丢失正负号，各项符号务必对照 PDF Eq.(13) 核对后再用",
               "locator": "Eq.(13)"},
              {"name": "局部 Nu", "latex": r"Nu_{x}=\frac{1}{C_1\,(x^*)^{C_2}+C_3}+C_4", "validity": "同上；C1 系数 3.122e-3/2.435e-2/2.143e-1/7.325，C2=0.6412，C3 1.589e-4/2.603e-3/2.444e-2，C4 7.148/13.28/15.15/5.936（符号待核）", "locator": "Eq.(12)"}],
    key_data=[kd("网格无关性", "α=5、Re=1100、z=60 mm 时三套网格 Nu=6.21/6.15/6.11", "§Numerical（作者版全文，经网页文本读取）")],
    benchmark_candidate=False)

add(id="pap-2005-lee-garimella-rect-microchannel-ht", type="paper",
    title="Investigation of heat transfer in rectangular microchannels", title_zh="矩形微通道换热研究",
    authors=["Poh-Seng Lee", "Suresh V. Garimella", "Dong Liu"], org="Purdue University", year=2005,
    venue="International Journal of Heat and Mass Transfer 48(9):1688-1704", identifiers={"doi": "10.1016/j.ijheatmasstransfer.2004.11.019"},
    url="https://docs.lib.purdue.edu/coolingpubs/",
    access={"status": "pending_user", "license": "Purdue e-Pubs 作者版", "redistributable": False, "how_to_get": PU + "：https://docs.lib.purdue.edu/cgi/viewcontent.cgi?article=1010&context=coolingpubs"},
    trust_level="L2", trust_reason="IJHMT 同行评审，实验 + 数值",
    stages=[4, 5, 7], topics=["microchannel", "experiment", "copper", "validation"],
    summary_zh="铜微通道（D_h 318~903 µm）水实验与常规 N-S 数值对比，结论：入口/边界条件匹配时经典理论适用于微通道；可作 HBM/Grace 微通道 1D 与 CFD 的实验基准。",
    key_data=[], benchmark_candidate=True, benchmark_note="有几何、Re、Nu 实测；需取得 PDF 后填 key_data。",
    notes="DOI/卷期已经 Crossref 核对；D_h 范围来自 Lee&Garimella 2006 文中转述，待取得全文核对。")

add(id="pap-2013-rau-garimella-jet-array-two-phase", type="paper",
    title="Local two-phase heat transfer from arrays of confined and submerged impinging jets", title_zh="受限淹没射流阵列的局部两相换热",
    authors=["Matthew J. Rau", "Suresh V. Garimella"], org="Purdue University", year=2013,
    venue="International Journal of Heat and Mass Transfer 67:487-498", identifiers={"doi": "10.1016/j.ijheatmasstransfer.2013.08.041"},
    url="https://docs.lib.purdue.edu/coolingpubs/",
    access={"status": "pending_user", "license": "Purdue e-Pubs 作者版", "redistributable": False, "how_to_get": PU + "：https://docs.lib.purdue.edu/cgi/viewcontent.cgi?article=1201&context=coolingpubs"},
    trust_level="L2", trust_reason="IJHMT 同行评审",
    stages=[4, 7], topics=["jet-array", "confined-submerged", "single-phase-validation", "HFE-7100"],
    summary_zh="受限淹没射流阵列局部换热（含单相段），s/d=4、H/d=4，Re 1920~39400；单相驻点 Nu 与 Li & Garimella 2001 Eq.(8) 吻合、面平均与其 Eq.(18) 吻合（MAE 1.3%），可作为 Li & Garimella 在阵列上适用性的旁证。",
    key_data=[kd("工况", "流量 450/900/1800 ml/min，Re 1920~39400，s/d=4，H/d=4", "全文（经网页摘要读取）", vf="secondary")],
    benchmark_candidate=False)

add(id="pap-2007-natarajan-microjet-distributed-returns", type="paper",
    title="Microjet Cooler with Distributed Returns", title_zh="分布回流微射流冷却器", authors=["Govindarajan Natarajan", "Raschid J. Bezama"], org="IBM", year=2007,
    venue="Heat Transfer Engineering 28(8-9):779-787", identifiers={"doi": "10.1080/01457630701328627"}, url="https://doi.org/10.1080/01457630701328627",
    access={"status": "pending_user", "license": "OpenAlex 标为出版社 OA（T&F），自动下载 HTTP 403", "redistributable": False,
            "how_to_get": "浏览器打开 https://www.tandfonline.com/doi/pdf/10.1080/01457630701328627 下载；否则机构订阅"},
    trust_level="L2", trust_reason="HTE 同行评审", stages=[2, 3, 4], topics=["microjet", "distributed-return", "ceramic", "IBM"],
    summary_zh="IBM 陶瓷分布回流微射流冷却器，低 Re 液体射流阵列 + 局部抽吸回流，是 Brunschwiler 2006 的姊妹工作。", key_data=[], benchmark_candidate=False)

add(id="pap-2012-whelan-cpu-jet-array-waterblock", type="paper",
    title="A liquid-based system for CPU cooling implementing a jet array impingement waterblock and a tube array remote heat exchanger",
    title_zh="采用射流阵列水冷头与管束远端换热器的 CPU 液冷系统", authors=["B.P. Whelan", "R. Kempers", "A.J. Robinson"], org="Trinity College Dublin", year=2012,
    venue="Applied Thermal Engineering 39:86-94", identifiers={"doi": "10.1016/j.applthermaleng.2012.01.013"}, url="https://doi.org/10.1016/j.applthermaleng.2012.01.013",
    access={"status": "pending_user", "license": "TCD TARA 机构库全文（833 KB）", "redistributable": False,
            "how_to_get": "浏览器打开 https://www.tara.tcd.ie/items/b8d50c81-18a5-4331-aad5-3b555c531414 下载（自动请求 403）"},
    trust_level="L2", trust_reason="ATE 同行评审", stages=[4, 7], topics=["jet-array", "CPU-waterblock", "system-level"],
    summary_zh="面向 8.24 cm² IHS 的射流阵列水冷头系统，200 W 时总热阻 0.18 K/W、水力功率约 1.5 W、芯片-空气温差 45°C（摘要）。",
    key_data=[kd("系统总热阻", 0.18, "Abstract", unit="K/W", cond="200 W，8.24 cm²，水力功率 ~1.5 W", vf="abstract")], benchmark_candidate=False)

add(id="pap-2020-hobby-jet-extraction-exp-cfd", type="paper",
    title="Comparison of Experimental and Computational Heat Transfer Characterization of Water Jet Impingement Array with Interspersed Fluid Extraction",
    title_zh="带穿插抽液口的水射流阵列换热实验与计算对比", authors=["David Hobby", "Tom Walker", "Alex Rattner", "Chris Jacobsen", "David Sherrer", "Todd Bandhauer"],
    org="Colorado State Univ. / Penn State", year=2020, venue="Heat Transfer Engineering 42(6):549-564 (2021)",
    identifiers={"doi": "10.1080/01457632.2019.1707404"}, url="https://doi.org/10.1080/01457632.2019.1707404",
    access={"status": "pending_user", "license": "Penn State ScholarSphere 投稿版", "redistributable": False,
            "how_to_get": "浏览器打开 https://scholarsphere.psu.edu/resources/504cebaf-5b3d-446f-9f7c-53c1c0e3dd74 下载（自动请求被拦）"},
    trust_level="L2", trust_reason="HTE 同行评审", stages=[5, 7], topics=["jet-array", "interspersed-extraction", "CFD-validation", "3D-printing"],
    summary_zh="3D 打印带穿插抽液口射流阵列，水实验与 1/4 射流重复单元 CFD 对比：压降在扣除歧管损失（降阶模型）后吻合极好，换热趋势有差异；用于验证 Rattner 2017 关联式。",
    key_data=[], benchmark_candidate=True, benchmark_note="待取得全文后补几何与数据。")

# ---------------------------------------------------------------- 付费，仅元数据
add(id="pap-2017-rattner-jet-array-extraction-ports", type="paper",
    title="General Characterization of Jet Impingement Array Heat Sinks With Interspersed Fluid Extraction Ports for Uniform High-Flux Cooling",
    title_zh="带穿插抽液口射流阵列热沉的通用表征", authors=["Alexander S. Rattner"], org="Penn State", year=2017,
    venue="Journal of Heat Transfer 139(8):082201", identifiers={"doi": "10.1115/1.4036090"}, url="https://doi.org/10.1115/1.4036090",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY + "；配套仿真数据集在 Penn State ScholarSphere（scholarsphere.psu.edu/files/bv73c0509）公开"},
    trust_level="L2", trust_reason="ASME JHT 同行评审（数值关联式）", stages=[3, 4],
    topics=["jet-array", "interspersed-extraction", "laminar", "low-Re", "high-Pr", "correlation", "k-factor"],
    summary_zh="层流单相射流阵列 + 穿插抽液口，>1000 例随机 CFD 拟合 Nu 与压降 k 因子关联式：Re_j 20~500、Pr 1~100、p/D_j 1.8~7.1、D_j/间隙高 0.1~4.0——参数范围与我方（Re≈478、Pr 15~25）重合度最高的文献，强烈建议获取。",
    key_data=[kd("关联式适用范围", "Re_j 20~500；Pr 1~100；p/D_j 1.8~7.1；D_j/th 0.1~4.0", "Abstract", vf="abstract"),
              kd("共轭对比工况", "5×5 mm 加热面，500 W/m²（摘要原文单位）", "Abstract", vf="abstract")],
    benchmark_candidate=False)

add(id="pap-1977-martin-impinging-gas-jets", type="paper",
    title="Heat and Mass Transfer between Impinging Gas Jets and Solid Surfaces", title_zh="冲击气体射流与固体表面间的传热传质",
    authors=["Holger Martin"], year=1977, venue="Advances in Heat Transfer 13:1-60 (Academic Press)",
    identifiers={"doi": "10.1016/S0065-2717(08)70221-1"}, url="https://doi.org/10.1016/S0065-2717(08)70221-1",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY + "（Elsevier ScienceDirect 书章）"},
    trust_level="L2", trust_reason="经典综述（被引 1700+）", stages=[3, 4], topics=["jet-array", "gas-jet", "classic-correlation"],
    summary_zh="单孔/阵列圆孔与缝隙射流经典关联式。针对气体（Pr≈0.7）建立，用 Pr^0.42 外推液体；我方 Re≈478 低于其下限 2000。",
    formulas=[{"name": "圆孔阵列平均 Nu（Martin 式，二手转引）",
               "latex": r"\frac{\overline{Nu}}{Pr^{0.42}}=\left[1+\left(\frac{H/D}{0.6/\sqrt{f}}\right)^{6}\right]^{-0.05}\frac{\sqrt{f}\,(1-2.2\sqrt{f})}{1+0.2\,(H/D-6)\sqrt{f}}\,Re^{2/3}",
               "validity": "2000≤Re≤100000；2≤H/D≤12；0.004≤f≤0.04（f=孔面积/冷却单元面积）。范围来源：Wei 2022 Table 1 p.3（Re 与 H/D、指数 0.67 已核）；f 范围与式子本体来自 Incropera《Fundamentals of Heat and Mass Transfer》转引，未对照 Martin 原文",
               "locator": "原文 §（未得）；二手：pap-2021-wei-microjet-correlations-feed-drain Table 1 p.3"}],
    key_data=[kd("适用范围（阵列）", "2000<Re<100000；2≤H/D≤12；Re 指数 0.67；T_ref=T_in", "pap-2021-wei Table 1 p.3", vf="secondary")],
    benchmark_candidate=False)

add(id="pap-1993-womac-single-liquid-jet", type="paper",
    title="Correlating Equations for Impingement Cooling of Small Heat Sources With Single Circular Liquid Jets", title_zh="小热源单圆孔液体射流冲击冷却关联式",
    authors=["D. J. Womac", "S. Ramadhyani", "F. P. Incropera"], org="Purdue University", year=1993, venue="Journal of Heat Transfer 115(1):106-115",
    identifiers={"doi": "10.1115/1.2910635"}, url="https://doi.org/10.1115/1.2910635",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY + "（ASME Digital Collection）"},
    trust_level="L2", trust_reason="ASME JHT 同行评审", stages=[3, 4], topics=["single-jet", "liquid", "FC-77", "water", "impingement-plus-wall-jet"],
    summary_zh="水与 FC-77 单孔液体射流（自由与淹没）对小热源的关联式，采用驻点区 + 壁射流区面积加权形式；Li & Garimella 2001 沿用此分区思路。",
    key_data=[], benchmark_candidate=False)

add(id="pap-1994-womac-multiple-liquid-jets", type="paper",
    title="Correlating Equations for Impingement Cooling of Small Heat Sources With Multiple Circular Liquid Jets", title_zh="小热源多圆孔液体射流冲击冷却关联式",
    authors=["D. J. Womac", "F. P. Incropera", "S. Ramadhyani"], org="Purdue University", year=1994, venue="Journal of Heat Transfer 116(2):482-486",
    identifiers={"doi": "10.1115/1.2911423"}, url="https://doi.org/10.1115/1.2911423",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY + "（ASME Digital Collection）"},
    trust_level="L2", trust_reason="ASME JHT 同行评审", stages=[3, 4], topics=["jet-array", "liquid", "FC-77", "water", "confined-submerged"],
    summary_zh="水与 FC-77 多孔液体射流阵列关联式（驻点区 + 壁射流区），受限淹没时 2≤H/D≤4 内对喷距不敏感（据 Wei 2022 p.2 转述）；是少数液体、阵列、中低 Re 的经典式，优先级高。",
    key_data=[kd("适用范围（转引，原文待核）", "Re 指数 0.5/0.8（层流/湍流两段）；Wei 2022 表列 Re<5000 与 5000~200000 两档、2≤S/D≤4（转引表述存疑）", "pap-2021-wei Table 1 p.3", vf="secondary")],
    benchmark_candidate=False)

add(id="pap-1995-garimella-rice-confined-submerged", type="paper",
    title="Confined and Submerged Liquid Jet Impingement Heat Transfer", title_zh="受限淹没液体射流冲击换热",
    authors=["S. V. Garimella", "R. A. Rice"], org="Univ. of Wisconsin–Milwaukee", year=1995, venue="Journal of Heat Transfer 117(4):871-877",
    identifiers={"doi": "10.1115/1.2836304"}, url="https://doi.org/10.1115/1.2836304",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY + "（ASME）"},
    trust_level="L2", trust_reason="ASME JHT 同行评审", stages=[3, 4], topics=["single-jet", "confined-submerged", "FC-77", "secondary-peak"],
    summary_zh="FC-77（Pr≈20~25，与 PG25 接近）单孔受限/非受限淹没射流局部换热：d 0.79~6.35 mm、Re 4000~23000、Z/d 1~14；给出驻点与平均 Nu 关联式，受限小喷距下 r/d≈2 出现次峰。",
    key_data=[kd("参数范围", "d 0.79~6.35 mm；Re 4000~23000；1≤Z/d≤14；FC-77", "Abstract（经 OpenAlex/Exa 摘要）", vf="abstract")], benchmark_candidate=False)

add(id="pap-2007-robinson-schnitzler-jet-array", type="paper",
    title="An experimental investigation of free and submerged miniature liquid jet array impingement heat transfer", title_zh="自由与淹没微型液体射流阵列冲击换热实验",
    authors=["A.J. Robinson", "E. Schnitzler"], org="Trinity College Dublin", year=2007, venue="Experimental Thermal and Fluid Science 32(1):1-13",
    identifiers={"doi": "10.1016/j.expthermflusci.2006.12.006"}, url="https://doi.org/10.1016/j.expthermflusci.2006.12.006",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY + "；作者 TCD 主页/TARA 可能有作者版"},
    trust_level="L2", trust_reason="ETFS 同行评审", stages=[3, 4, 7], topics=["jet-array", "confined-submerged", "free-surface", "water", "pressure-drop"],
    summary_zh="d=1 mm 水射流阵列（S/d=3/5/7，即 121/45/21 孔，加热面 780 mm²），2≤H/d≤30、650≤Re≤6500、2~9 L/min 的面平均 h 与压降；给出淹没与自由表面两组关联式（见 Whelan 2009 转引）。S/d 覆盖我方 5~7.5，Re 下限接近 478。",
    formulas=[{"name": "淹没受限阵列（转引）", "latex": r"\frac{Nu_L}{Pr^{0.4}}=23.39\,Re_{d_n}^{0.46}\left(\frac{S}{d_n}\right)^{-0.442}\left(\frac{H}{d_n}\right)^{-0.00716}",
               "validity": "水；650≤Re≤6500；2≤H/d≤3；3≤S/d≤7；Nu_L 以加热面特征长度定义", "locator": "pap-2009-whelan Eq.(2) p.10（二手）"}],
    key_data=[kd("几何与工况", "d=1.0 mm；S/d=3,5,7（121/45/21 孔）；加热面 780 mm²；2~9 L/min；2≤H/d≤30；650≤Re≤6500", "Abstract + 正文片段（ScienceDirect 页面）", vf="landing_page"),
              kd("喷距敏感性", "淹没时 2≤H/d≤3 不敏感；5≤H/d≤20 单调下降", "pap-2009-whelan p.10", vf="secondary")],
    benchmark_candidate=True, benchmark_note="实验几何清楚、有 h 与 ΔP，与我方 S/d 接近；需全文取数据点。")

add(id="pap-2005-fabbri-dhir-microjet-arrays", type="paper",
    title="Optimized Heat Transfer for High Power Electronic Cooling Using Arrays of Microjets", title_zh="微射流阵列高功率电子冷却换热优化",
    authors=["Matteo Fabbri", "Vijay K. Dhir"], org="UCLA", year=2005, venue="Journal of Heat Transfer 127(7):760-769",
    identifiers={"doi": "10.1115/1.1924624"}, url="https://doi.org/10.1115/1.1924624",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY + "（ASME）"},
    trust_level="L2", trust_reason="ASME JHT 同行评审", stages=[3, 4, 7], topics=["microjet-array", "low-Re", "water", "FC-40", "correlation"],
    summary_zh="水与 FC-40 自由表面微射流阵列（孔径 65~250 µm），Re 73~3813，给出含 Pr 的阵列 Nu 关联式与喷嘴板压降；覆盖我方 Re 与高 Pr，但为自由表面而非淹没。",
    key_data=[kd("适用范围（转引）", "73<Re<3813；65 µm<d_n<250 µm；水与 FC-40；Re 指数 0.78", "pap-2021-wei Table 1 p.3", vf="secondary")], benchmark_candidate=False)

add(id="pap-2009-michna-microjet-stagnation", type="paper",
    title="Single-Phase Microscale Jet Stagnation Point Heat Transfer", title_zh="单相微尺度射流驻点换热",
    authors=["Gregory J. Michna", "Eric A. Browne", "Yoav Peles", "Michael K. Jensen"], org="RPI", year=2009, venue="Journal of Heat Transfer 131(11):111402",
    identifiers={"doi": "10.1115/1.3154750"}, url="https://doi.org/10.1115/1.3154750",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY + "（ASME）"},
    trust_level="L2", trust_reason="ASME JHT 同行评审", stages=[3, 4], topics=["microjet", "stagnation", "low-Re", "confined-submerged"],
    summary_zh="微尺度（54/112 µm）淹没受限射流驻点换热，Re 约 50~3500（据 Wei 2022 Table 1 对 Michna 系列的转述），低 Re 驻点 Nu 关联。",
    key_data=[kd("适用范围（转引）", "50<Re_d<3500；D=54 与 112 µm；Re 指数 0.55", "pap-2021-wei Table 1 p.3", vf="secondary")], benchmark_candidate=False)

add(id="pap-2010-browne-microjet-array", type="paper",
    title="Experimental Investigation of Single-Phase Microjet Array Heat Transfer", title_zh="单相微射流阵列换热实验",
    authors=["Eric A. Browne", "Gregory J. Michna", "Michael K. Jensen", "Yoav Peles"], org="RPI", year=2010, venue="Journal of Heat Transfer 132(4):041013",
    identifiers={"doi": "10.1115/1.4000888"}, url="https://doi.org/10.1115/1.4000888",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY + "（ASME）"},
    trust_level="L2", trust_reason="ASME JHT 同行评审", stages=[3, 4, 7], topics=["microjet-array", "low-Re", "confined-submerged", "water", "R134a"],
    summary_zh="微射流阵列（淹没受限）单相换热实验与关联式，Re 范围与 Michna 2009 相近；与我方低 Re 阵列直接相关。",
    key_data=[], benchmark_candidate=False, notes="卷期与文章号 041013 已经 Crossref 核对。")

add(id="pap-2006-brunschwiler-jet-distributed-return", type="paper",
    title="Direct Liquid Jet-Impingement Cooling With Micron-Sized Nozzle Array and Distributed Return Architecture", title_zh="微米喷嘴阵列与分布回流结构的直接液体射流冷却",
    authors=["T. Brunschwiler", "H. Rothuizen", "M. Fabbri", "U. Kloter", "B. Michel", "R. J. Bezama", "G. Natarajan"], org="IBM Zurich Research", year=2006,
    venue="ITherm 2006 (10th Intersociety Conf. on Thermal and Thermomechanical Phenomena), pp.196-203",
    identifiers={"doi": "10.1109/ITHERM.2006.1645343"}, url="https://doi.org/10.1109/ITHERM.2006.1645343",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY + "（IEEE Xplore）"},
    trust_level="L2", trust_reason="IEEE ITherm 经同行评审会议论文",
    stages=[3, 4, 7], topics=["microjet-array", "distributed-return", "silicon", "low-Re", "IBM"],
    summary_zh="IBM 硅基微米喷嘴阵列（最多约 47000 孔）+ 分布回流，H/D=1.2、Re<800 层流，给出 ±9% 的简单关联式；其 43 µm/19044 孔数据被 Wei 2022 用作外部验证。",
    key_data=[kd("工况（转引）", "H/D=1.2；Re<800；关联式置信 ±9%；19044 孔、d=43 µm、单元 150 µm", "pap-2021-wei p.3, p.12-13", vf="secondary")],
    benchmark_candidate=False, notes="作者列表与页码已经 Crossref 核对。")

add(id="pap-2009-ndao-cooling-technologies-comparison", type="paper",
    title="Multi-objective thermal design optimization and comparative analysis of electronics cooling technologies", title_zh="电子冷却技术多目标热设计优化与对比",
    authors=["Sidy Ndao", "Yoav Peles", "Michael K. Jensen"], org="RPI", year=2009, venue="International Journal of Heat and Mass Transfer 52(19-20):4317-4326",
    identifiers={"doi": "10.1016/j.ijheatmasstransfer.2009.03.069"}, url="https://doi.org/10.1016/j.ijheatmasstransfer.2009.03.069",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY},
    trust_level="L2", trust_reason="IJHMT 同行评审", stages=[2], topics=["technology-comparison", "microchannel", "jet-array", "pin-fin", "optimization"],
    summary_zh="基于关联式的多目标优化，比较微通道、射流阵列、针肋等冷却方式的热阻-泵功帕累托前沿，可支撑 ② 选型论证（射流 vs 微通道）。", key_data=[], benchmark_candidate=False)

add(id="pap-2002-qu-mudawar-microchannel", type="paper",
    title="Experimental and numerical study of pressure drop and heat transfer in a single-phase micro-channel heat sink", title_zh="单相微通道热沉压降与换热的实验与数值研究",
    authors=["Weilin Qu", "Issam Mudawar"], org="Purdue University", year=2002, venue="International Journal of Heat and Mass Transfer 45(12):2549-2565",
    identifiers={"doi": "10.1016/S0017-9310(01)00337-4"}, url="https://doi.org/10.1016/S0017-9310(01)00337-4",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY},
    trust_level="L2", trust_reason="IJHMT 同行评审，被引 1000+", stages=[4, 5, 7], topics=["microchannel", "experiment", "CFD-validation", "copper", "benchmark"],
    summary_zh="铜微通道热沉（231 µm×713 µm 通道）水实验 + 3D 共轭数值，压降与温度分布吻合，是微通道 CFD 验证最常用基准，适用于 HBM/Grace 微通道。",
    key_data=[], benchmark_candidate=True, benchmark_note="经典基准；通道尺寸依记忆，取得全文后核对并补数据点。")

add(id="pap-1981-tuckerman-pease-vlsi", type="paper",
    title="High-performance heat sinking for VLSI", title_zh="VLSI 高性能热沉", authors=["D. B. Tuckerman", "R. F. W. Pease"], org="Stanford University", year=1981,
    venue="IEEE Electron Device Letters 2(5):126-129", identifiers={"doi": "10.1109/EDL.1981.25367"}, url="https://doi.org/10.1109/EDL.1981.25367",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY + "（IEEE Xplore）"},
    trust_level="L2", trust_reason="IEEE EDL 同行评审，开创性工作", stages=[2, 3], topics=["microchannel", "silicon", "classic"],
    summary_zh="硅微通道热沉开创性论文（790 W/cm² 量级），微通道设计理论起点；注意同年另有勘误 10.1109/EDL.1981.25406。", key_data=[], benchmark_candidate=False)

add(id="hbk-1978-shah-london-laminar-flow", type="handbook",
    title="Laminar Flow Forced Convection in Ducts (Advances in Heat Transfer, Supplement 1)", title_zh="管道内层流强制对流",
    authors=["R. K. Shah", "A. L. London"], org="Academic Press", year=1978, venue="Academic Press（Advances in Heat Transfer 增刊 1）",
    identifiers={"isbn": "978-0-12-020051-1"}, url="https://doi.org/10.1016/B978-0-12-020051-1.50012-7",
    access={"status": "paywalled", "redistributable": False, "how_to_get": "购书 / 图书馆借阅 / ScienceDirect 机构订阅（按章节 DOI，如 Rectangular Ducts 10.1016/B978-0-12-020051-1.50012-7, pp.196-222）"},
    trust_level="L1", trust_reason="权威专著", stages=[3, 4], topics=["laminar", "rectangular-duct", "fRe", "Nu_fd", "entrance-region"],
    summary_zh="矩形通道层流 fRe 与 Nu_T/Nu_H1 多项式、入口段数据的权威来源（Rectangular Ducts 章 pp.196-222），HBM（α≈4.4）与 Grace（α=3）通道的 1D 摩擦与充分发展 Nu 首选。",
    key_data=[], benchmark_candidate=False)

add(id="pap-2006-prasher-tim-review", type="paper",
    title="Thermal Interface Materials: Historical Perspective, Status, and Future Directions", title_zh="热界面材料：历史、现状与未来方向",
    authors=["Ravi Prasher"], org="Intel", year=2006, venue="Proceedings of the IEEE 94(8):1571-1586",
    identifiers={"doi": "10.1109/JPROC.2006.879796"}, url="https://doi.org/10.1109/JPROC.2006.879796",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY + "（IEEE Xplore）"},
    trust_level="L2", trust_reason="Proc. IEEE 特邀综述，被引 900+", stages=[3, 4], topics=["TIM", "contact-resistance", "BLT"],
    summary_zh="TIM 热阻 = BLT/k + 两侧接触热阻的模型与各类 TIM（脂、PCM、焊料、凝胶）热阻量级综述，为 TIM1/TIM2 预算提供依据。", key_data=[], benchmark_candidate=False)

add(id="pap-2003-gwinn-webb-tim-testing", type="paper",
    title="Performance and testing of thermal interface materials", title_zh="热界面材料性能与测试", authors=["J. P. Gwinn", "R. L. Webb"], org="Penn State", year=2003,
    venue="Microelectronics Journal 34(3):215-222", identifiers={"doi": "10.1016/S0026-2692(02)00191-X"}, url="https://doi.org/10.1016/S0026-2692(02)00191-X",
    access={"status": "paywalled", "redistributable": False, "how_to_get": PAY},
    trust_level="L2", trust_reason="同行评审期刊", stages=[4, 7], topics=["TIM", "ASTM-D5470", "test-method"],
    summary_zh="TIM 性能对比与测试方法（ASTM D5470 类稳态法）讨论，含高性能 TIM 热阻测量装置精度问题。", key_data=[], benchmark_candidate=False)

add(id="std-2017-astm-d5470", type="standard",
    title="Standard Test Method for Thermal Transmission Properties of Thermally Conductive Electrical Insulation Materials", title_zh="导热电绝缘材料热传输性能标准测试方法",
    org="ASTM International", year=2017, venue="ASTM", identifiers={"std_no": "ASTM D5470"}, url="https://www.astm.org/d5470-17.html",
    access={"status": "paywalled", "redistributable": False, "how_to_get": "ASTM 官网购买 / 机构标准库订阅"},
    trust_level="L1", trust_reason="国际标准", stages=[4, 7], topics=["TIM", "test-method", "standard"],
    summary_zh="TIM 稳态热阻/表观导热率测试（热流计法，多厚度外推接触热阻）的标准方法，⑦ 样件 TIM 测试依据。",
    key_data=[], benchmark_candidate=False, notes="版本号 D5470-17 依记忆登记，现行版本以 ASTM 官网为准，需复核。")

# ---------------------------------------------------------------- 自检
ID_RE = re.compile(r"^(pap|hbk|std|ven|pat|dat|int)-[0-9]{4}-[a-z0-9]+(-[a-z0-9]+)*$")
REQ = ["id", "type", "title", "year", "url", "access", "trust_level", "stages", "last_verified"]
ids = set()
for e in E:
    assert ID_RE.match(e["id"]), e["id"]
    assert e["id"] not in ids, e["id"]
    ids.add(e["id"])
    for k in REQ:
        assert k in e, (e["id"], k)
    assert e["access"]["status"] in {"downloaded", "metadata_only", "pending_user", "paywalled", "login_required", "not_found"}
    if e["access"]["status"] == "downloaded":
        assert "file" in e and re.fullmatch(r"[0-9a-f]{64}", e["file"]["sha256"]), e["id"]
        assert (LIB / e["file"]["path"]).exists(), e["id"]
    for d in e.get("key_data", []):
        assert {"quantity", "value", "locator"} <= d.keys(), e["id"]
(HERE / "entries.json").write_text(json.dumps(E, ensure_ascii=False, indent=2), encoding="utf-8")
print(len(E), "entries;", sum(e["access"]["status"] == "downloaded" for e in E), "downloaded")
for e in E:
    print(f'{e["id"]} | {e["access"]["status"]} | {e["trust_level"]}')

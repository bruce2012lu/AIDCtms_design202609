# AIDC 液冷系统 AI 设计平台 · 项目规划 v1.1

> 文档编号 AIDC-PLAT-PLAN-001 · 版本 v1.1 · 日期 2026-10-02 · 状态：合并定稿草案，待用户评审
>
> 编写：`cp-design` 规划工程师（AI）。本版把 2026-10-02 三个智能体并行写的 v1.0 规划（A：`docs/plan/`；B：`planning/`；C：`plan/`）合并成唯一一套，以 A 的章节和 33 步编号为主体，吸收 B 的技术栈、甘特、候选清单与工程闸门，吸收 C 的环境探测、可并行步和压降风险，并写入用户新增的三项要求（设计工况 D-001、孪生与控制双路线、九阶段门控流程模型）。合并依据与取舍见附录 B 变更记录。
>
> 适用对象：GB300 计算托盘上的 B300 GPU 冷板（CP-B300-JM-01，标杆算例）与 Grace CPU 冷板（CP-GRACE-MC-01），并为托盘、机柜级液冷与 CDU 二次侧预留扩展口。
>
> 路径约定：除特别说明，路径都相对 `agents/AIDCtms/coolingplate/`；`AP/` 代表 `agent/practice01_0926/`。配套文件：《AIDC 液冷设计平台 · 实施计划 v1.1》（同目录）。md 是唯一正文源，html 由同目录 `build_plan.py` 生成。
>
> 治理：本轮不安装技能、不写正式记忆、不 git commit / push。文中候选技能与记忆一律为 `candidate`。

## 0 摘要

### 0.1 结论先行

**结论（置信度 0.75）**：平台不用从零搭。冷板设计链的一维模型、参数化 CAD 规则门、Fluent 单元胞 CFD、MCP 工具服务和设计台界面都已经有了。缺的是四样：

1. 单一来源的设计点数据，并按用户已拍板的 **D-001 设计工况（PG25 · 1400 W 设计基线 · 温升 6~10 K 可调 · 1100 W 校核）** 统一口径；
2. 一条可批处理、能回归的 CAD → CFD → FEA → 出图自动链；
3. ⑦ 样件试验与 V&V 闭环；
4. ⑧ 数字孪生模型与 ⑨ 孪生在环 AI 控制。⑧⑨ 与一维计算一样走两条并列路线：路线 A 为 AI 自研 Python，路线 B 为 MATLAB/Simulink agent。两条路线以一维模型为共同源，以 FMU 为互通接口。

推进顺序是先桌面可验证、后重资产：

- **第一批**（P0，两周内，全部可在本机直接做）：环境与许可只读盘点（S01），设计点注册表与冲突清单（S02，含 D-001），决策会（S03），一维回归基线（S04），以及三个可并行的只读或轻量步骤：已有 CFD 日志收口（S34）、记忆与文档体检（S35）、manifest 规范（S36）。
- **CFD 主力**推荐本机已装的 Ansys 2026 R1 Fluent，自动化层以 journal 打底、PyFluent 作便利层，OpenFOAM 作开源交叉校核（本机已有 WSL2 Ubuntu-22.04）。⑤ 的工具最终选定仍列为用户决策（Q-04）。**CAD 主力**是已有的 build123d 内核，先补上 `pitch_x/pitch_y`。**工程图**先走 ezdxf DXF 自动出图，再由人在 AutoCAD 2024 审图；正式投产图由人在公司 CAD 里定稿。
- **智能体**：继续以 `cp-design` 为主责。MATLAB/Simulink 交给已登记的 `ai-matlab`（经薄加载器与 `user-matlab` MCP），文献交给 `librarian`。前期不新增注册智能体，S33 再评审是否拆分。
- **闸门**：平台三道人工闸门不变。另在模块内试行四道工程闸门：E1 几何冻结、E2 大算例启动、E3 门控放行、E4 实物动作。外协、采购、试验台通电、向真实设备下发设定值，都比照第③道闸门由人确认。

**主要不确定性**：

- OEM 输入缺失：封装图、power map、单板流量窗、UQD、压装力。
- PG25 正式物性未定：两套物性的粘度差约 37%。
- HBM 当前截面在 v2.1 与方案 D 之间未确认，孔径 D0.50 与 D0.40 也未统一。
- Ansys 与 MATLAB 各模块的许可是否真能检出，尚未验证。
- 整板 CFD 算力不足，需要 HPC 或云。

### 0.2 已决策 D-001：设计工况（用户已拍板）

| 项 | 决策 | 说明 |
|---|---|---|
| 冷却液 | **PG25**（丙二醇 25% 水溶液），进液 40 °C（沿用 v2.1；45 °C 作最恶补充工况） | 水口径（v2.0，1100 W · 2.0 L/min）**只作回归对照**，不再作放行判据 |
| 设计基线 | **1400 W**（v2.1 拆分：GPU 核心 910 W、HBM 8 × 43.7 W ≈ 350 W、其他 140 W） | 所有一维、CFD、FEA、孪生的主设计点 |
| 冷却液温升 | **6~10 K 可调**（6 K 为 v2.1 项目值，8 K、10 K 为放宽档） | 温升决定流量；孪生与控制以 6~10 K 为调节范围 |
| 校核工况 | **1100 W** | 与 1400 W 同流量下校核温升与热阻；负载范围 1100~1400 W |
| 正式物性 | **待决**（Q-01） | 下表粗估按 cp ≈ 3.9 kJ/(kg·K)、ρ ≈ 1020 kg/m³ |

工况矩阵与粗估流量（模组级，E1 粗估，Q = P / (ρ·cp·ΔT)）：

| 工况 | 功率 | 温升目标 | 模组流量 | 1100 W 同流量温升 | 0.50 mm 孔速（GPU 支路按 v2.1 比例） | 用途 |
|---|---|---|---|---|---|---|
| PC-1 | 1400 W | 6 K | 约 3.5 L/min（3.52） | 约 4.7 K（PC-4） | 0.897 m/s | 设计基线主点 |
| PC-2 | 1400 W | 8 K | 约 2.6 L/min（2.64） | 约 6.3 K（PC-5） | 约 0.67 m/s | 放宽档 |
| PC-3 | 1400 W | 10 K | 约 2.1 L/min（2.11） | 约 7.9 K（PC-6） | 约 0.54 m/s | 放宽上限，热阻最不利 |
| PC-4/5/6 | 1100 W | — | 同 PC-1/2/3 流量 | 4.7 / 6.3 / 7.9 K | 同上 | 校核工况 |
| WR-A | 1100 W（水） | 7.96 K | 2.0 L/min | — | 0.629 m/s | 仅回归对照（v2.0 DP-A） |

与已有数字的关系：

- **与 v2.1 的 3.512 L/min**：v2.1 用 `model.py` 的 PG25_40（ρ 1022、cp 3900）算出 1400 W · 6 K → 3.512 L/min；按 ρ ≈ 1020 粗估为 3.519 L/min，差 0.2%。两套 PG25 物性的 cp 都取 3900 J/(kg·K)，所以**流量几乎不受物性选择影响**（DOWFROST 的 ρ 1022.5 → 3.511 L/min）。
- **两套 PG25 物性的真正差别**在粘度与导热：`model.py` / v2.1 取 μ 1.15×10⁻³ Pa·s、k 0.452；HBM 1D v1.0 取 DOWFROST LC 25 表值 μ 1.58×10⁻³、k 0.476。粘度高约 37%，会让 Re、压降和 h 都偏移，所以正式物性要先定（Q-01），再出正式热阻与压降。
- **分支流量**：v2.1 的 GPU 核心 2.283 L/min、单颗 HBM 0.1096 L/min 是 6 K 档，8 K / 10 K 档按 6/ΔT 线性缩放（GPU 约 1.71 / 1.37 L/min）。最终分配由 S05 与 S08 复算。
- **压降**：v2.1 的 14–24 kPa 是把水基线 3.5–5.5 kPa 按流量平方**外推到原分配表 4.0–4.2 L/min** 的结果，不是 3.512 L/min 设计流量下的值（A 版把它写成设计流量下的值，本版已更正）。按同一平方律粗估：3.5 L/min 约 10–18 kPa，2.6 L/min 约 6–10 kPa，2.1 L/min 约 4–6 kPa。这些都是 E0 外推，以 S08 水力网络和 S18 半板 CFD 为准。
- **含义**：放宽温升（8~10 K）能缓解 20 kPa 压降风险，但流量降 25–40% 会让对流热阻上升，热性能本来就没有余量（v2.0 DR2 有条件通过）。所以 6 K 是基线，8~10 K 是控制可用的调节区间，设计必须在 PC-1 和 PC-3 两端都校核。

各阶段如何引用 D-001：

| 阶段 | 引用方式 | 对应步骤 |
|---|---|---|
| ④ 一维扫描 | 功率 1100~1400 W × 温升 6~10 K（0.5 K 步长）全扫描，并叠加孔径、TIM2、槽深等杠杆 | S05、S07、S08 |
| ⑤ CFD | 工况矩阵以 PC-1…PC-6 共 6 工况为主；v2.0 C01–C12 中的热点、堵塞、45 °C、几何变体作补充子集；水 WR-A 只作回归 | S18、S19 |
| ⑦ 试验 | TTV 覆盖 PC-1/PC-3/PC-4/PC-6 四个角点 + 中心点 PC-2 | S23、S26 |
| ⑧ 孪生 | 训练与验证包络：P 1100~1400 W、ΔT 6~10 K（流量约 1.7~3.5 L/min）、Tin 40~45 °C | S27、S28、S30 |
| ⑨ 控制 | 温升设定值调节范围 6~10 K，负载 1100~1400 W 阶跃与斜坡，约束 ΔP ≤ 20 kPa、孔速 ≤ 2.0 m/s、HBM 近壁 ≤ 0.80 m/s | S29、S40 |

### 0.3 推荐技术栈（首期）

| 环节 | 主力 | 交叉验证 / 备选 | 本机状态（2026-10-02 只读核实） |
|---|---|---|---|
| ④ 一维 | 路线 A：Python 一维包（扩展 `design/calc/model.py`、`oned.py`、`zones.py`），唯一数值源 | 路线 B：MATLAB R2025b + Simscape Fluids（经 `ai-matlab`），系统级与瞬态对照 | Python 已有；MATLAB 已安装，Simscape Fluids 许可特性在许可文件中 |
| ⑥ CAD | build123d（`cad/.venv`，已接规则门与 MCP） | SpaceClaim 脚本做流体域与命名选择；SolidWorks/NX 只在客户要求原生图时引入 | build123d 0.11.1；SpaceClaim v261 已装 |
| ⑤ CFD/CAE | Ansys Fluent 2026 R1（journal + PyFluent）+ Fluent Meshing；ICEM 只用于单元胞 | OpenFOAM chtMultiRegionFoam（WSL2）作免许可交叉验证；Icepak 只用于托盘级 | Fluent、Meshing、ICEM、CFX 已装；PyFluent 未装；WSL2 Ubuntu-22.04 已有 |
| ⑥ 结构 | Ansys Mechanical / MAPDL（PyMechanical/PyMAPDL） | CalculiX；v2.0 解析板条保留为对照 | `aisol`、`ansys` 目录存在；Py 包未装 |
| ⑥ 工程图 | build123d → ezdxf DXF → AutoCAD 2024 审图 | FreeCAD TechDraw；SolidWorks 工程图 API | ezdxf 1.4.4；AutoCAD 2024 已装；FreeCAD/SolidWorks 未装 |
| 优化 / DOE | Python（scipy、optuna）+ 一维筛选 | optiSLang（CFD 级 DOE 与稳健性） | optiSLang 目录存在 |
| ⑦ 试验 | 自建 TTV 台 + Python DAQ + ASME V&V 20 / PTC 19.1 不确定度 | 外协第三方实验室 | 无台架；MATLAB 许可含 Data Acquisition 特性 |
| ⑧ 孪生 | 路线 A：Python ROM（scikit-learn GP）+ RC 网络 → FMU（pythonfmu / FMPy） | 路线 B：Simscape Fluids 孪生 → FMU（Simulink Compiler）；Ansys TwinAI / Twin Builder ROM | scikit-learn 已在 `cad/.venv`；FMPy 未装；TwinAI 目录存在 |
| ⑨ 控制 | 路线 A：Python SIL（do-mpc / CasADi MPC；RL 研究项） | 路线 B：Simulink + MPC Toolbox / RL Toolbox，Simulink Test SIL，Simulink Real-Time HIL | MPC、RL、Simulink Test、Real-Time 许可特性在许可文件中；CasADi 未装 |
| 编排 | Cursor / Claude Code + `cp-design` + `ai-matlab` + `librarian` | — | 已登记 |

### 0.4 阶段与工期概要

自 2026-10-05（W1，周一）起约 **40 周**，到 2027-07-11 结束。关键路径是 P3 整板 CFD（依赖 HPC）→ P4 图纸 → P5 样件交期与试验，并避开春节（2027-02-06 前后，约 W18）。工期按用户每周投入 10–15 h 估算，详见第 12 章与实施计划第 1 章。

| 阶段 | 内容 | 周次 | 日期 | 步骤 | 门控 |
|---|---|---|---|---|---|
| P0 | 准备、环境、事实底账、决策 | W1–W2 | 10-05 – 10-18 | S01–S03、S34–S36 | M0 规划评审 · DR0 复核 |
| P1 | 一维（双路线）、水力网络、DR0/DR1 复核 | W2–W7 | 10-12 – 11-22 | S04–S09、S37、S38 | DR2′ 一维再基线（PG25） |
| P2 | CAD v2、流体域、接口、Grace | W5–W10 | 11-02 – 12-13 | S10–S13 | DR1′ 几何再选定 |
| P3 | 三维 CFD、V&V、工况矩阵、R1 自动化 | W8–W20 | 11-23 – 2027-02-21 | S14–S19、S39 | DR3 仿真通过 |
| P4 | 机械与图纸（FEA、公差、图纸包） | W15–W22 | 2027-01-11 – 03-07 | S20–S22 | DR3 闸门 |
| P5 | 样件、试验与 V&V | W19–W32 | 02-08 – 05-16 | S23–S26 | DR4 送样放行 |
| P6a | 数字孪生模型（A/B 双路线） | W24–W34 | 03-15 – 05-30 | S27、S28、S30 | DR5 孪生验收 |
| P6b | 孪生在环 AI 控制（A/B 双路线） | W30–W40 | 04-26 – 07-11 | S29、S40 | DR6 控制策略放行 |
| P7 | 平台化（持续，W34 起收口） | W1–W40 | 全程 | S31–S33 | ①② 闸门 · 平台 v1.0 |

### 0.5 最先需要用户拍板的事项

主设计点已经由 D-001 定下，不再列为开放问题。按阻塞程度排序（完整清单见第 13 章）：

1. **Q-01 PG25 正式物性**：取 `model.py` PG25_40、DOWFROST LC 25 表值，还是供应商实测表？它阻塞 S05、S07、S08 的正式数字。
2. **Q-02 D-001 下的放行判据**：1400 W 设计基线的热阻目标沿用 v2.0 DP-B 的 < 0.025 °C/W，还是按 Tj 倒推？1100 W 校核沿用 < 0.028？20 kPa 是否计入 UQD？它阻塞 S07、S09、S19、S26。
3. **Q-03 HBM 当前截面**与 **Q-04 GPU 孔径**：它们阻塞 S10、S12、S17。
4. **Q-05 数据保密、仓库可见性，以及 `practice01_0926/` 纳入 git 跟踪**：它阻塞首次提交。
5. **Q-06 工程闸门 E1–E4 与③的比照映射**：它阻塞 S10 起的所有写入与实物步骤。

## 1 项目愿景与范围

### 1.1 愿景

建一个“AI 驱动的算力中心（AIDC）液冷系统设计平台”。人负责定目标、做判断、签闸门；AI 负责查资料、算数、写脚本、跑批处理、对账和写报告。平台把附图的门控流程（扩展为 ① 需求与输入 → ⑨ 孪生在环 AI 控制，见第 5 章）跑成可复算、可回归、可审计的工作链，再延伸到托盘水力、数字孪生和 AI 在环控制。所有资产以纯文本沉淀在本仓库，遵循平台层 `platform/` → 模块 `agents/<id>/` 的继承结构。

### 1.2 算例驱动

平台的基本单位是**算例**（case）。一个算例就是一个设计对象在一组设计点下的完整证据包：输入追溯、一维计算、几何、仿真、图纸、试验、孪生、控制。每个算例都按同一套门控（DR0–DR6）推进，复用同一套技能与工具适配器，数字只有一个来源。

| 算例 | 对象 | 当前进度 | 平台中的角色 |
|---|---|---|---|
| CASE-01 | CP-B300-JM-01 B300 冲击微通道冷板 | ①–④ 完成（水口径），⑤ 单元胞 CFD 部分完成；D-001 口径下待重算 | 标杆算例，首个走完 ①–⑨ |
| CASE-02 | CP-GRACE-MC-01 Grace 平行微通道冷板 | ①–④ 一维完成（v1.0 水 / v1.1 PG25） | 第二算例，验证平台对“非射流”构型的通用性 |
| CASE-03 | GB300 计算托盘 4 GPU + 2 Grace 并联回路（含 CDU 二次侧） | 只有分配表与原则 | 系统级算例，是数字孪生与在环控制的被控对象 |

### 1.3 项目目标（可度量）

| 编号 | 目标 | 度量 | 目标值 | 期限 |
|---|---|---|---|---|
| O-1 | 一维工具可复算 | 对 v2.0 §9、`cycle.json`、v2.1/PG25 工作簿的回归偏差 | 关键量 ≤ 0.5% | W3（2026-10-25） |
| O-2 | 设计点单一来源 | 报告、xlsx、CAD、CFD 的数字都从 `designpoints/*.yaml` 派生；D-001 工况矩阵落盘 | 冲突项清零或显式登记 | M0（W2） |
| O-3 | 一维覆盖 D-001 | 1100~1400 W × 6~10 K 全包络的热阻、压降、孔速、HBM 近壁速度 | 1000 点 DOE < 1 min | M1（W7，2026-11-22） |
| O-4 | 几何自动化 | 216 孔 v2 整板与流体域可由参数一键生成 | 生成 + 规则门 + STEP 回读 ≤ 10 min | M2（W10，2026-12-13） |
| O-5 | CFD 可信 | 网格无关、守恒、V4 锚定；PG25 6 工况矩阵完成 | 相邻网格差 < 3%，能量偏差 < 1%，V4 < 15% | M3（W20，2027-02-21） |
| O-6 | V&V 闭环 | 试验与仿真偏差自动计算并触发回路 | 偏差 > 15% 自动开 R2 工单 | M5（W32，2027-05-16） |
| O-7 | 数字孪生 | ROM 对 CFD 留一误差、对试验误差、单次评估时间 | ≤ 5% / ≤ 10% / < 1 s | M6（W34，2027-05-30） |
| O-8 | 孪生在环控制 | SIL 场景零约束违约；泵功较 PID 基线下降 | 0 次违约；≥ 10%（目标值，待 P6b 标定） | M7（W40，2027-07-11） |
| O-9 | 设计周期 | 一次“改孔径 → 出 1D → 出 CAD → 出单胞 CFD 结论”的人工时 | 由约 2 天降到 ≤ 0.5 天 | M7 |
| O-10 | 知识沉淀 | 经用户验证入库的技能与语义记忆 | ≥ 8 个技能、≥ 10 条记忆，字段齐全 | M7 |

### 1.4 范围

范围内：

- B300 冷板（GPU 射流区、HBM 微通道区）与 Grace 冷板的 ①–⑨ 全流程。
- 托盘级水力分配：4 块 GPU 冷板 + 2 块 Grace 冷板并联，孔板配平；CDU 二次侧泵阀的一维、系统模型、孪生与控制（仿真内）。
- 平台工具链：一维（双路线）、CAD、CFD/CAE、FEA、工程图、试验数据、V&V、ROM/数字孪生（双路线）、AI 在环控制（双路线）。
- 知识与记忆沉淀：skills、memories、Dify RAG 回灌。

范围外（本期）：

- CDU 一次侧、冷却塔、设施水系统的详细设计（只作边界条件和孪生接口）。
- 两相冷板、浸没液冷、纳米流体（技术调查 v1.3 §8.3 已判定不作基线）。
- 向真实 CDU / 托盘下发控制参数：只做仿真、回放和台架 HIL（HIL 每次下发经 E4）。
- 采购合同、订单 ICD、FAT 保证书、正式 FTO 法律意见。v2.0 声明本设计是候选，不是订单 ICD。
- 修改平台层宪法：本规划只提建议，由人决定。

### 1.5 证据等级与术语

三版证据等级合并为 E0–E5（C 版分级是 A、B 两版的超集，含义一致）：

| 等级 | 含义 | 例子 | 能写成什么 |
|---|---|---|---|
| E0 假设 / 外推 | 估值、平方律外推、占位尺寸 | PG25 整板压降 14–24 kPa（v2.1 外推）；静压箱 3–5 kPa | 只作风险提示 |
| E1 一维 | 关联式或能量平衡 | v2.0 §9 壳–进液 0.0326–0.0366 °C/W | 方案筛选、区间 |
| E2 单元胞 / 局部 CFD | 周期胞或局部带 | UC-01b m425，R(TIM–in) 0.03134 °C/W | 局部 h、孔口压降、模型标定；不外推整板 |
| E3 整板 / 半板 CFD | 含静压箱、歧管，网格无关 | 尚无 | 设计结论候选 |
| E4 样件实测 | TTV、流阻、红外、氦检，不确定度已评估 | 尚无 | 保证值依据 |
| E5 系统 SAT | 托盘 / 机柜现场 | 尚无 | 运行孪生标定 |

平台所有对外数字都要带证据等级、来源文件和日期。单元胞结果不能写成整板保证值（`agent.md` “不做”第 1 条）。

## 2 现状盘点

### 2.1 本次阅读与核对的文档

- 三版 v1.0 规划：A `docs/plan/AIDC液冷设计平台_项目规划/实施计划_v1.0_20261002.md`；B `planning/项目规划/实施计划_v1.0_20261002.md`、`planning/build_plan.py`；C `plan/项目规划/实施计划_液冷设计平台_v1.0_20261002.md`、`plan/build_plan_html.py`，以及归属不明的中间产物 `plan/项目规划_v1.0.md`、`plan/实施计划_v1.0.md`、`plan/build_html.py`。
- 平台层：`platform/CLAUDE.md`（记忆治理字段、三道人工闸门、发布节奏、A 主 B 备）。
- 模块 `AP/`：`agent.md`、`README.md`、`软件界面方案.md`、`oned.py`、`zones.py`、`mcp/server.py`、`ui/`、`knowledge/`、`memory/`（6 条 semantic、2 条 episodic）、`skills/`（4 个）、`cycle-20260926/`、`references/` 8 份报告、`runs/20260926-140511/params.yaml`。
- 回查核对的原始资料：`design/calc/model.py`（物性）、`design/calc/calc_1d_out.txt`、`design/cfd_HBM/HBM微通道冷板_1D设计报告_v1.0_20260929.html`（DOWFROST 物性、方案 D）、`references/…v2.1_PG25_20260929.html`（物性、3.512 L/min、14–24 kPa 外推口径）、`memory/semantic/b300-design-lock.md`、`design/cfd/uc01b_2.4x3.0lessmesh12cells/`（最新日志时间）、`design/CFD-AI_Agent_能力评估与工作计划_v1.0_20260920.html`。
- 本机只读探测：MATLAB 与 Ansys 安装目录、注册表、PATH、许可文件中的特性名（只读名称，不读密钥，未检出许可）；Python 环境包清单；git 跟踪状态。

### 2.2 已有成果

| 资产 | 位置 | 能力 | 成熟度 |
|---|---|---|---|
| 一维数值源 | `design/calc/model.py` | 物性（WATER40、PG25_40）、几何、Martin / 驻点 / 短槽关联式、`solve()`、孔径扫描、承压、尺寸链 | 高，v2.0 全文由它生成 |
| 一维工具封装 | `AP/oned.py`、`AP/zones.py` | GPU 射流区按 Martin 有效域自动切换低 Re 准则（11 条准则 + MARTIN_ENTRY）；HBM 平槽（v2.0 横流口径）；Grace 平行槽 | 中，只认水 DP-A/DP-B，无自动回归 |
| MCP 工具服务 | `AP/mcp/server.py` | 8 个工具：`kb_catalog`、`memory_list`、`cad_tracks`、`cad_inspect`、`cad_build`、`oned_design`、`hbm_design`、`grace_design`；stdio + HTTP 8765；导出须 `confirm=true`；`--self-test` | 中；README 只列 5 个工具，文档已漂移 |
| 设计台 UI | `AP/ui/` | 9 页：总览、1D、HBM、Grace、CAD 工作台、CAE、知识库、记忆、工具 | 中；无口径切换与闸门看板 |
| 参数化 CAD 内核 | `cad/coldplate/`、`cad/build.py` | yaml → 派生 → 规则门 → 实体 → STEP/DXF/PNG/SolidWorks 宏 | 高，但只能表达 v1.0（128 孔、单一节距） |
| 设计循环 0926 | `AP/cycle-20260926/` | 1D → 3D CAD → 单孔 CFD → 结构工艺装配四页报告；`build_cad.py` 绕过内核出 216 孔整板 STEP（未过规则门） | 中 |
| CFD 算例 | `design/cfd/uc01b_*`、`design/cfd_HBM/` | ICEM 网格 + Fluent 共轭：单胞、12 格带、HBM 七槽、HBM 方案 D | 中，判据未全关 |
| 尺寸链与门控表 | `cad/尺寸链计算/` | DR0–DR3/DR4 门控 xlsx、PG25 热量与流量分配 | 中；DR2 xlsx 公式格无缓存值 |
| 技能 | `AP/skills/` | `design-loop`、`cad-loop`、`cfd-loop`（含 GPU 显存判据）、`fluent-gui-capture`（约 16.5 KB 已验证命令） | 中 |
| 记忆 | `AP/memory/` | 6 条 semantic，均带 `confidence / valid_until / last_verified / expired` | 中；`cfd-uc01b.md` 2026-12-31 到期 |
| 调研 | `references/` 技术调查 v1.3、专利 v1.4 | 路线、关联式窗口、专利方案 A/B/C、FTO 雷区 | 高 |

### 2.3 关键数据与参数

B300 冷板 CP-B300-JM-01（v2.0 水基线，**现仅作回归对照**；来源：v2.0 §0、§5、§9；`cycle.json`）：

| 量 | DP-A（水 1100 W） | DP-B（水 1400 W） | 证据 |
|---|---|---|---|
| 流量 / 进液 | 2.0 L/min（GPU 1.60 / HBM 0.40）· 40 °C | 2.4 L/min · 40 °C | 输入 |
| 几何 | 95×75×8.5 mm；每 die 9×12，共 216 孔；D 0.50，Sx 3.0，Sy 2.4，H 2.0 mm（H/D 4，f 0.0273） | 同左 | 候选 |
| 孔速 / Re_D | 0.629 m/s · 478 | 0.755 m/s · 573 | E1 |
| 壳–进液热阻 | 0.0326–0.0366 °C/W（目标 < 0.028，门槛 ≤ 0.032） | 0.0311–0.0351 °C/W（目标 < 0.025） | E1，不判定 |
| 板内压降 | 3.5–5.5 kPa（上限 20） | 3.7–5.7 kPa | E1；静压箱 3–5 kPa 为 E0 估值 |
| 流体温升 | 7.96 K | 8.44 K | E1 |
| HBM 近壁流速 | 0.463 m/s（帽 0.80） | 0.556 m/s | E1 |
| 结温 | 84.7–93.5 °C | 94.8–106.0 °C | E1 |
| 盖板跨射流阵 | 16.73 MPa，安全系数 4 | — | 解析 |

B300 v2.1 / PG25（**D-001 的出发点**；来源：v2.1 §1、§3、§7）：

- 工况：PG25 40 °C，模组 1400 W，项目温升 6 °C。物性 ρ 1022、cp 3900、μ 1.15×10⁻³、k 0.452、Pr 9.92，与 `model.py` 的 PG25_40 相同。
- 设计流量：模组 3.512 L/min，GPU 核心 910 W 对应 2.283 L/min，HBM 每颗 43.7 W 对应 0.1096 L/min，Grace 0.753 L/min，整柜约 351.2 L/min。0.50 mm 孔在 2.283 L/min 下孔速 0.897 m/s（D0.40 为 1.402 m/s），低于 2.0 m/s 上限。
- 未闭合：壳–进液热阻没有按 PG25 和新流量重算；HBM 中点进液歧管孔位未定；整板压降只有平方律外推（见 §0.2）。

Grace CP-GRACE-MC-01（来源：Grace v1.0 §0、§5；v1.1 §3）：

- 对象：300 W 含内存（CPU 260 W + 内存 40 W），两层铜，48 条 0.40×1.20 mm 沿 Y 交错槽，200×120×8 mm 候选外形，壳–进液目标 < 0.080 °C/W。
- 水力：水 0.55 L/min 时支路约 10 kPa。PG25 0.8 L/min（原分配表）时，现有 4×1.04 mm 孔板加 CPU 通道约 22.9 kPa，高于 20 kPa。
- D-001 估算：设计流量 0.753 L/min（6 K）时，按平方律约 20.3 kPa，仍略超；8 K 档约 0.57 L/min、10 K 档约 0.45 L/min 时，约 11 / 7 kPa（E0）。孔板按 D-001 重配见 S08。

CFD（来源：`cycle-20260926/03_单孔CFD仿真分析.html`、`memory/semantic/cfd-uc01b.md`、12 格契合性报告；全部为水口径、D0.40 网格）：

| 算例 | 网格 | 迭代 | ΔP | T_TIM 底 | R(TIM–in) | 备注 |
|---|---|---|---|---|---|---|
| UC-01b bc216 | 2,115,436 HEXA | 421 收敛 | 1091.51 Pa | 342.096 K | — | D 0.40 |
| UC-01b m425 | 4,259,680 HEXA | 380 收敛 | 1087.09 Pa | 341.385 K | 0.03134 °C/W | R_conv 0.01493；能量闭合 1.0015 |
| UC-01b 12 格带 | 28,005,504 HEXA | 600 二阶 | 1099.99 Pa | 342.049 K | 0.03208 °C/W | 能量比 1.0368（未达 1%）；ΔP 比一维孔口高 27.6% |
| HBM 七槽交错流 0.80×2.00 | — | 200 | — | — | — | 连续性残差 2.6×10⁻⁴ 未达标；温升比一维高 7.96%，标“限制” |
| HBM 方案 D 中缝 | 861 万 | — | 缝压降约 0.30 kPa | — | — | 2026-10-01 核对缝速 0.57 m/s；1223 万汇流槽网格超单卡 GPU，只能 CPU |

### 2.4 已有结论

- 选型：分区杂交（GPU 射流 + 短槽，HBM 无喷嘴 + 限速，隔离肋）加权 4.50，排第一（v2.0 §5.1；`02_DR1_方案权衡.xlsx` 复算差约 0.05，名次不变），对齐专利方案 A。
- 水力余量大，热设计没有余量，正确方向是“用压降换换热”（v2.0 §0.1）。PG25 粘度约为水的 1.76 倍，压降余量被吃掉一部分（v2.1 §3）。
- Re_D < 2000 时不采用 Martin 1977，保证值用短槽层流 + 驻点核（v2.0 §9.4；`oned.py` 自动判定）。PG25 下 Re 更低（6 K 档 0.50 mm 孔约 400），这条纪律不变。
- 最优先的杠杆：TIM2 升级到 ≤ 0.004 °C/W，孔径 0.50 → 0.40 mm（v2.0 §9.12）。
- 单胞 CFD 的 0.0313 °C/W 比一维下限 0.0326 低约 4%（`cycle-20260926/03` 原文写“落在下限与上限之间”，与数字不符）。它是 E2，网格孔径是 D0.40，不是整板保证。
- 工艺：机加 + 真空钎焊，整板增材不作出货基线（v2.0 §6.1；专利 v1.4 §3.7）。
- 门控状态：DR0 有条件（6 项缺失输入）、DR1 完成、DR2 有条件通过（区间跨目标线；**D-001 口径下待重算**）、DR3 未完成、DR4 未开始。

### 2.5 本机环境核实（2026-10-02，只读）

A 版写“MATLAB 未探测到”，C 版写“MATLAB R2025b 带 Simscape Fluids/MPC/RL”。本版按安装目录、注册表、PATH 只读核实，结论是 **MATLAB R2025b 已安装，C 版正确**。A 的误判来自 `MATLAB_ROOT` 未设置、只查了 `C:\Program Files\MATLAB`。全程没有启动 MATLAB，也没有发生许可检出。

| 项 | 核实结果 | 证据 |
|---|---|---|
| MATLAB 安装 | **已安装 R2025b（25.2.0.2998904，2025-08-21）**，位于 `D:\programfiles\MATLAB\R2025b` | `VersionInfo.xml`；`where matlab` → `…\R2025b\bin\matlab.exe`；PATH 含 `…\R2025b\bin`、`…\runtime\win64`；注册表 `HKLM\SOFTWARE\MathWorks\R2025b`、`MATLAB\25.2`；卸载项 “MATLAB R2025b 25.2”；`MATLAB_ROOT` 未设置 |
| MATLAB 工具箱目录 | simulink、physmod/simscape、physmod/fluids、mpc、rl、control、slcontrol、sldo、simulinktest、optim、globaloptim、nnet、rtw、coder、compiler、simulinkcompiler、ident、slrealtime、sldrt、daq 存在；**stats 不存在** | `toolbox\` 目录列表（187 个） |
| MATLAB 许可文件 | `licenses\` 下有 1 个 `.lic`，含 127 个特性名。其中有 SIMULINK、Simscape、**SimHydraulics**（Simscape Fluids 的许可特性名）、MPC_Toolbox、Reinforcement_Learn_Toolbox、Simulink_Test、Real-Time_Workshop（Simulink Coder）、Simulink_Compiler（FMU 导出）、XPC_Target（Simulink Real-Time）、Real-Time_Win_Target、Data_Acq_Toolbox、OPC_Toolbox；Statistics_Toolbox 有特性但未安装 | 只读特性名，未读密钥，未检出。**是否真能检出待 S01 经用户同意后用 `license('test',…)` 验证** |
| Ansys 2026 R1 | `E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261` 存在，含 fluent、meshing、icemcfd、CFX、CFD-Post、aisol（Mechanical）、ansys（MAPDL）、scdm（SpaceClaim）、Discovery、optiSLang、TwinAI、AnsysEM、SystemCoupling、dpf、sherlock、licensingclient；`ANSYSLMD_LICENSE_FILE` 已设置（未读取） | 目录列表；`fluent.exe` 存在；Fluent 已有大量 2026-09-27 至 10-02 运行日志 |
| Python | `cad/.venv`：build123d 0.11.1、ezdxf 1.4.4、numpy、scipy、scikit-learn 1.9.1、pytest、PyYAML；**无** openpyxl、ansys-*、FMPy、pythonfmu、CasADi、torch、gmsh。默认 `python` 为 VeighNa 3.13（含 openpyxl、pandas、torch、markdown），按约定不往里装包 | `pip list` |
| 其他 | AutoCAD 2024 已装；WSL2 Ubuntu-22.04 与 docker-desktop 存在（OpenFOAM 可行）；FreeCAD、OpenModelica、SolidWorks 未发现；node v22、Edge、Chrome 可用于自检 | 目录与命令探测 |
| 算力 | i9-14900KF 24 核、128 GB、RTX 4090 24 GB（同时负责显示，空闲约 21.5 GB） | `memory/semantic/environment.md`、`skills/cfd-loop` |
| git | `AP/` 整个目录为未跟踪（`??`，已跟踪文件数 0） | `git status` |

### 2.6 三版规划与原始资料的矛盾核对

| # | 矛盾 | 三版说法 | 原始资料核对 | v1.1 取值 |
|---|---|---|---|---|
| K-01 | MATLAB 是否可用 | A：未探测到；B、C：已装 R2025b | 见 §2.5 | 已安装；许可检出待 S01 |
| K-02 | PG25 整板压降 14–24 kPa 的流量口径 | A：设计流量下；C：4.0–4.2 L/min 下 | v2.1 §3 原文：水基线按流量平方外推到原分配表 4.0–4.2 L/min | 以 v2.1 原文为准；D-001 各档另做粗估（§0.2） |
| K-03 | PG25 物性 | A：两套差约 37% | `model.py` PG25_40：1022 / 3900 / 1.15e-3 / 0.452；HBM 1D v1.0：DOWFROST LC 25 1022.5 / 3900 / 1.58e-3 / 0.476 | 两套都入库，正式取值待 Q-01；cp 相同，流量不受影响 |
| K-04 | HBM 当前截面 | B：v2.1 7×0.80×2.00 与方案 D 冲突；C：列两种候选 | v2.0 16×0.60×1.50 横流；09-28 修订 7×0.80×2.00 交错；v2.1 每颗中心进液 7×0.80×2.00；HBM 1D v1.0（10-01 修改）与 `b300-design-lock.md`（last_verified 10-01）为方案 D 11×0.45×2.00 + 静压仓 + 中缝，PG25 每颗 0.15 L/min | 注册表登记 HBM-A/B/C/D；时间最新的是 D，“当前采用”由用户确认（Q-03） |
| K-05 | HBM 单颗流量 | v2.1：0.1096 L/min；方案 D：0.15 L/min | 0.1096 是 1400 W · 6 K 按热量分配；0.15 来自原分配表 0.15–0.18 | D-001 下以热量分配为准，方案 D 的 CFD 需按 0.1096（6 K）及缩放档复核 |
| K-06 | 单胞 0.0313 与一维下限 | `cycle-20260926/03` 写“落在区间内” | 0.0313 < 0.0326，低约 4%；网格 D0.40，一维 D0.50 | 标注“低于下限，孔径不同，不可直接比” |
| K-07 | 一维与 CFD 压降偏差 | A：12 格 +27.6%；B：UC-01b +26.1% | 分属 12 格报告与 UC01b 契合性报告（09-25），路径不同（一维只有孔口项） | 两者都保留并注明出处；不是模型误差 |
| K-08 | 旧口径文件 | A：`calc_1d_out.txt` 为 128 孔 | 核实：N=128、f=0.02182 | 标“已取代”，只作反例 |
| K-09 | CFD-AI 评估“本机无 ANSYS” | A：已过时 | 原文 “G0 = NO-GO … 未找到 ICEM / Fluent” | 标“已取代”，以 §2.5 为准 |
| K-10 | 12 格续算状态 | B、C：待读最新日志 | 目录最新 `.trn` 为 2026-09-27 19:35（600 步），之后没有续算记录 | S34 只读收口；如需续算由用户决定 |
| K-11 | 工期 | A：23 周至 2027-03-12；B：40 周至 2027-07-11；C：约 25 周 | — | 取 B 的 40 周：已计入 HPC、外协交期与春节，⑧⑨ 各自成段 |
| K-12 | 步骤编号 | A：S01–S33；B：S0.1–S7.7；C：S01–S46 | — | 取 A 编号，新增 S34–S40（附录 B） |
| K-13 | 证据等级 | A：E1–E4；B：E-1D…E-TEST；C：E0–E5 | — | 取 E0–E5（§1.5） |
| K-14 | 主设计点 | 三版都列为开放问题 | 用户已拍板 | D-001（§0.2），从开放问题删去 |

### 2.7 缺口与不一致清单

| 编号 | 缺口 / 不一致 | 影响 | 处理（实施步骤） |
|---|---|---|---|
| G-01 | OEM 输入缺失：封装图、power map、单板流量与压降窗、UQD、压装力（v2.0 §13 C-01～C-04） | DR0 只能“有条件通过” | 输入追溯矩阵加责任人与日期；先用 TTV 与透明样打通物理可行性（S02、S37、S23） |
| G-02 | 设计点：水 v2.0 与 PG25 v2.1 并存；D-001 已定但工具和设计台只有水 DP-A/DP-B | 热阻、压降结论不在同一基准 | 注册表落盘 D-001 工况矩阵，水只作回归（S02、S05） |
| G-03 | PG25 物性两套（K-03） | Re、ΔP、h 偏移 | 物性库带来源和温度曲线，Q-01 定正式值（S02、S05） |
| G-04 | HBM 截面与流路 4 个版本（K-04） | CAD、CFD、报告各用一版 | 注册表 HBM-A/B/C/D 唯一 `current`（S02、S12） |
| G-05 | 孔径 D0.50（model.py、CAD、v2.1）与 D0.40（CFD 网格）并存 | 1D 与 CFD 不能直接对比 | 两孔径单胞对比后由用户定（S11、S17、Q-04） |
| G-06 | CAD 内核只有单一 `jets.pitch`，建不出 v2 216 孔；无水嘴、UQD、静压箱；Grace 未接规则门，STEP 仍是同向模型 | ⑤ 流体域与 ⑥ 图纸卡住 | S10–S13 |
| G-07 | CFD 判据未关：V1/V4 未做；无关性未做；12 格能量比 1.0368；整板未做；C01–C12 未开；PG25 无任何 CFD | DR3 不能评审 | S14–S19、S34 |
| G-08 | PG25 压降：B300 整板只有外推（K-02）；Grace 支路 22.9 kPa | 托盘配平未闭合 | S08 水力网络、S18 半板 CFD |
| G-09 | 机械只做了解析板条；无 FEA、完整 GD&T、焊接符号；压装力未定 | DR3 闸门不完整 | S20–S22 |
| G-10 | ⑦ 未开始；DR4 门表实测列为空 | 无 E4 锚点 | S23–S26 |
| G-11 | FTO 仅初筛（v2.0 C-10） | 量产风险 | 外部专业服务；AI 只做对照草稿（S37） |
| G-12 | 数据治理：K-06、K-08、K-09；DR2 xlsx 公式格无缓存值；`oned.py`/`zones.py` 无回归测试；记忆索引引用的 `uc01b-lessmesh.md` 中文损坏；README 工具清单落后 | 容易引用旧数 | S02、S04、S35 |
| G-13 | ⑧⑨ 为零：无 ROM、FMU、控制器；双路线未选；FMPy、pythonfmu、CasADi、PyAnsys 未装；`AP/` 未纳入 git | 孪生与控制从头规划 | S38、S27–S30、S40；Q-05、Q-07、Q-09 |
| G-14 | 命名：注册 id 为 `cp-design`，模块目录名为 `practice01_0926`，与“命名零漂移”约定不一致 | 自动发现可用，但偏离约定 | 本期不改，S33 一并评审 |

## 3 需求分析

### 3.1 角色与使用场景

| 角色 | 典型场景 | 平台要提供的 |
|---|---|---|
| 热设计负责人（用户） | 在 D-001 口径下改孔径、改温升后马上看热阻和压降；签 DR 闸门 | 一条指令出 1D 计算书；闸门包；差异对比 |
| 仿真工程师 | 批量跑 PG25 6 工况矩阵、查残差、出合格云图 | journal 模板、作业队列、日志解析、取图技能 |
| 结构 / 工艺工程师 | 尺寸链、公差、承压、出图 | 规则门、FEA 模板、DXF/PDF 草图、BOM |
| 试验工程师 | TTV 台架、流阻曲线、红外、氦检数据入库 | 试验大纲、数据模板、偏差自动计算 |
| 系统 / 控制工程师 | 托盘流量分配、孪生回放、6~10 K 温升调度 | 水力网络、ROM、FMU、MPC/RL 场景库（双路线） |
| OEM / 托盘方 | ICD、power map、流量窗 | 输入索取清单；ICD 到位后的影响分析 |
| 工艺与外协、IP 顾问 | 可制造性、交期；FTO | 询价包草案；专利对照清单 |
| AI 智能体 | 按技能执行、写记忆候选、提醒闸门 | MCP 工具、技能、记忆治理 |

### 3.2 设计工况矩阵（D-001）

| 设计点 ID | 对象 | 工质 / 进液 | 功率 | 流量 | 主要指标 | 身份 |
|---|---|---|---|---|---|---|
| DP-P1400-6K（PC-1） | B300 模组 | PG25 40 °C | 1400 W（910 / 350 / 140） | 约 3.52 L/min | 温升 6 K；孔速 ≤ 2.0 m/s；HBM 近壁 ≤ 0.80 m/s；ΔP ≤ 20 kPa；热阻目标待 Q-02 | **设计基线** |
| DP-P1400-8K / 10K（PC-2/3） | B300 模组 | PG25 40 °C | 1400 W | 约 2.64 / 2.11 L/min | 同上；热阻最不利端在 10 K | 放宽档 |
| DP-P1100-xK（PC-4/5/6） | B300 模组 | PG25 40 °C | 1100 W | 同 PC-1/2/3 | 温升 4.7 / 6.3 / 7.9 K | 校核工况 |
| DP-P1400-6K-45 | B300 模组 | PG25 45 °C | 1400 W | 约 3.52 L/min | 最恶进液 | 补充 |
| HBM-P25 | 单颗 HBM | PG25 40 °C | 43.7 W | 0.1096 L/min（6 K 档） | 近壁 ≤ 0.80 m/s | 分支 |
| GRACE-P25 | Grace 冷板 | PG25 40 °C | 300 W | 0.753 L/min（6 K 档）；8 / 10 K 档约 0.57 / 0.45 | 孔板重配后支路 ≤ 20 kPa（窗 8–12 kPa） | CASE-02 |
| TRAY-P25 | 计算托盘 | PG25 | 4×1400 + 2×300 W | 由网络求解 | 并联分流偏差 ≤ 10%、托盘压降 | CASE-03 |
| DP-A-W / DP-B-W | B300 整板 | 水 40 °C | 1100 / 1400 W | 2.0 / 2.4 L/min | v2.0 全部指标 | **仅回归对照** |

试验与孪生阶段另需瞬态工况：负载阶跃 1100 ↔ 1400 W、斜坡、温升设定值 6 ↔ 10 K 切换、进液温度阶跃 40 → 45 °C、断流 / 泵降级、HBM 支路堵塞 20%（v2.0 C10）。

### 3.3 功能需求

| 编号 | 功能 | 说明 | 优先级 |
|---|---|---|---|
| FR-01 | 设计点注册表 | D-001 工况矩阵与水回归点统一放在 yaml，带来源、日期、置信度、状态；工具调用必须带设计点 id | P0 |
| FR-02 | 输入追溯与冲突检测 | 自动比对报告、xlsx、yaml、CAD 参数，列冲突；ICD 到位后做影响分析 | P0 |
| FR-03 | 一维热–水力计算（路线 A） | GPU 射流、HBM（A/B/C/D）、Grace、能量平衡、热阻链、压降预算；水与 PG25 两套物性；关联式按适用域自动切换 | P0 |
| FR-04 | 敏感性、DOE、UQ、差距闭合 | 1100~1400 W × 6~10 K 全包络，叠加孔径、TIM2、槽深、工质；龙卷风图；所需 h；蒙特卡洛不确定度 | P0 |
| FR-05 | 水力网络 | 板内静压箱 + 托盘 4 GPU + 2 Grace 并联，孔板配平 | P1 |
| FR-06 | 一维对照（路线 B） | Simscape Fluids 搭同一稳态点和托盘网络，与路线 A 对表 | P1 |
| FR-07 | 参数化 CAD v2 | 各向异性节距、HBM 多方案、Grace、水嘴/UQD 占位；规则门；STEP 回读核对 | P0 |
| FR-08 | CFD 前处理 | 流体域抽取、命名面、网格模板（ICEM 单胞 / Fluent Meshing 整板） | P1 |
| FR-09 | CFD 作业与后处理 | journal/PyFluent 批处理、显存与核数检查、残差与监视量解析、结果入账、GCI、契合性报告 | P1 |
| FR-10 | 回路 R1 自动化 | 不达标时 AI 自动参数扫描或优化，提出变体，经人确认后重跑 1D → CAD → CFD | P1 |
| FR-11 | FEA | 3 bar 承压、压装力、热应力、焊后平面度 | P1 |
| FR-12 | 工程图 | 2D 视图、剖面、孔位表、BOM、尺寸链表、GD&T 检查表；候选图与正式图分开 | P1 |
| FR-13 | 试验管理 | 大纲、台架 BOM、传感器不确定度、DAQ 脚本、数据模板、导入校验 | P1 |
| FR-14 | V&V | V1–V5 对比，ASME V&V 20 判读，偏差 > 15% 自动开 R2 回路，参数反标定 | P1 |
| FR-15 | 数字孪生（双路线） | 路线 A：Python ROM / RC 网络 → FMU；路线 B：Simscape Fluids 孪生 → FMU；在线标定与回放（R3） | P2 |
| FR-16 | 孪生在环 AI 控制（双路线） | 路线 A：Python SIL（MPC/RL）；路线 B：Simulink SIL/HIL（MPC/RL Toolbox）；安全监督层；温升 6~10 K 调度；R4 反哺设计指标 | P2 |
| FR-17 | 报告生成 | md 为唯一源，单文件离线 html（左侧可折叠目录、内联 SVG）；闸门包 | P0 |
| FR-18 | 运行清单与追溯 | 每个 run 有 manifest：父级、输入哈希、工具版本、设计点、证据等级 | P0 |
| FR-19 | 知识与记忆 | 技能沉淀、记忆写入与过期、RAG 回灌；候选先登记 | P0 |
| FR-20 | 设计台扩展 | 口径切换、扫描页、CFD 作业页、闸门看板、工件浏览 | P2 |

### 3.4 非功能需求

| 编号 | 要求 | 指标 |
|---|---|---|
| NFR-01 可复算 | 每个数字能追到脚本、输入和版本 | 报告页脚写数值源；重跑结果一致 |
| NFR-02 可回归 | 改代码后一维与规则门全部自测 | pytest 全过；黄金数据偏差 ≤ 0.5% |
| NFR-03 可审计 | 所有运行有 `runs/<时间戳>-<步骤>-<简称>/`，含 manifest、参数副本、日志、产物、哈希 | 100% |
| NFR-04 不覆盖冻结件 | `cad/params/cp_b300_jm01.yaml`、已发 STEP、已发报告只读 | 规则门拒绝写入 |
| NFR-05 离线可用 | 报告单文件、无外部依赖；核心计算不依赖联网 | 100% |
| NFR-06 数据保密 | OEM 资料与几何不出本机或内网；云模型只见脱敏摘要；`on_sensitive_data` 路由 | 按 §10.1 分级 |
| NFR-07 资源安全 | GPU 求解前检查显存（2.2 GB/百万单元），超线只用 CPU；不与运行中的 Fluent 抢核 | 不卡死桌面 |
| NFR-08 可移植 | 路径、版本、许可证服务器都放配置；密钥只读环境变量 | 换机只改配置 |
| NFR-09 性能 | 一维单点 < 1 s；1000 点 DOE < 1 min；CAD 整板 < 10 min；ROM 单次 < 1 s | 达标 |
| NFR-10 可解释 | 关联式写明适用域；越域给警告，不静默外推 | 100% |
| NFR-11 双路线一致 | 路线 A 与路线 B 同一稳态点的 ΔTf、ΔP 偏差 | < 1%（一维）；< 2%（孪生） |

### 3.5 接口需求

| 编号 | 接口 | 形式 | 现状 |
|---|---|---|---|
| IF-01 | 智能体 ↔ 工具 | MCP stdio（`cp-design`、`user-matlab`、`dify-rag`） | 已登记；MATLAB 已安装，MCP 连通性未验证 |
| IF-02 | 人 ↔ 平台 | 设计台 HTTP `127.0.0.1:8765`；Cursor/Claude 对话 | 已有 |
| IF-03 | 1D ↔ CAD | 设计点 yaml → `cad/coldplate` Spec | 部分，缺 v2 字段 |
| IF-04 | CAD ↔ CFD | STEP（AP214/AP242）+ 命名面清单 json | 部分 |
| IF-05 | CFD ↔ 平台 | journal、`.cas.h5/.dat.h5`、transcript、surface report CSV | 部分 |
| IF-06 | FEA ↔ 平台 | PyMechanical/MAPDL 脚本、结果 CSV | 无 |
| IF-07 | 试验 ↔ 平台 | CSV 模板（时间戳、通道、单位、校准号） | 无 |
| IF-08 | 1D / 孪生 ↔ 控制（两路线互通） | FMU（FMI 2.0/3.0 Co-Simulation）+ 统一变量表（§9.8） | 无 |
| IF-09 | 平台 ↔ git | `git-release` 技能，提交信息规范，真实 push 由人执行 | 已有 |
| IF-10 | 平台 ↔ Dify | `librarian` → `rag-query` | 已有 |

### 3.6 验收准则与 KPI

| 编号 | 准则 | 判据 | 对应门 |
|---|---|---|---|
| AC-1 | 一维工具复现既有报告 | v2.0 §9、v2.1 §1–4、Grace v1.1 §3 相对偏差 ≤ 0.5%（Grace 孔板 ≤ 1%） | DR2′ |
| AC-2 | 一维覆盖 D-001 | PC-1…PC-6 及 6~10 K 连续扫描给出热阻区间、ΔP、孔速、HBM 近壁速度与杠杆排序 | DR2′ |
| AC-3 | CAD v2 | 216 孔 / 各向异性节距 / HBM 当前方案可建；规则门 pass；STEP 回读包围盒与体积校核通过 | DR1′ |
| AC-4 | CFD 可信 | 残差（连续 / 动量 < 1e-4，能量 < 1e-6）；能量守恒 < 1%；质量 < 0.1%；GCI < 3%；V4 对 Martin ≤ 15% | DR3 仿真 |
| AC-5 | 性能结论 | Q1–Q8 有单值或可信区间，并在 PC-1…PC-6 下判定是否满足 Q-02 定的目标 | DR3 仿真 |
| AC-6 | 图纸可外协 | 尺寸链闭合；GD&T、表面处理、焊接、检验要求齐全；外协能据此报价 | DR3 闸门 |
| AC-7 | 试验可判 | 热阻测量扩展不确定度 ≤ ±5%（k = 2）；出厂三曲线齐全 | DR4 |
| AC-8 | V&V 闭环 | 偏差绝对值 ≤ 15%，或 R2 修正后复核通过 | DR4 |
| AC-9 | 孪生精度 | 包络内相对 CFD ≤ 5%、相对试验 ≤ 10%；评估 < 1 s；两路线稳态差 < 2% | DR5 |
| AC-10 | 控制安全 | SIL 全场景零约束违约；HIL 下发前人工确认 + 硬件联锁 | DR6 |
| AC-11 | 治理 | 每步有 manifest；入库记忆字段齐全；无冻结件被改写 | 每步 |

关键 KPI（沿用 v2.0 §1.2，在 D-001 下的目标线待 Q-02 确认）：

| 类别 | 指标 | 门槛 | 目标 | 验证方式 |
|---|---|---|---|---|
| 热 | B300 壳–进液 Rθ @ 1400 W 设计基线 | 待 Q-02 | 待 Q-02（v2.0 DP-B 为 < 0.025） | 整板 CFD + TTV |
| 热 | B300 Rθ @ 1100 W 校核 | ≤ 0.032 °C/W | < 0.028 | 同上 |
| 热 | 两 die 中心温差 | ≤ 8 K | ≤ 5 K | CFD + TTV 双加热区 + 红外 |
| 水力 | 板内压降 @ 设计流量 | ≤ 20 kPa | ≤ 18 kPa | 流阻曲线 |
| 水力 | 射流孔速 / HBM 近壁流速 | ≤ 2.0 m/s / ≤ 0.80 m/s | — / ≤ 0.60 m/s | 1D + CFD |
| 水力 | 分区流量 GPU : HBM、216 孔逐孔偏差 | 设计比 ±15% | ±10% | 分区流量计、CFD Q2 |
| 水力 | 冷却液温升 | 6~10 K（D-001） | 设定值跟踪误差 ≤ 0.5 K（控制） | 能量平衡 |
| 机械 | 承压 / 平面度 / Ra | 1.5× 保压；≤ 0.08 mm；≤ 1.6 μm | 3 bar + 100% 氦检；≤ 0.05 mm；≤ 0.8 μm | 氦质谱、三坐标 |
| 孪生 | ROM 对 CFD / 对试验 | ≤ 5% / ≤ 10% | ≤ 3% / — | 留出样本 |
| 平台 | 设计迭代周期 | ≤ 48 h | ≤ 24 h（O-9） | 工件时间戳 |

### 3.7 约束

- 平台约定：先读 `platform/CLAUDE.md`；模块自包含；`.claude/agents/<id>.md` 是薄加载器；派生子智能体限 1 层且只有 `quant-research` 能派生，所以本项目不派生子智能体，新增能力要么是技能，要么是新注册智能体。
- 三道人工闸门（技能安装、记忆继承、实盘/资金动作），每个 DR 闸门由人签字；工程闸门 E1–E4 在模块内试行（§5.12）。
- 冻结口径：v2.0 文字、v1.0 参数化内核、asm_0921 实测、UC-01b、Grace 概念五套数字各自归位（`agent.md` 职责第 2 条）。
- 本机硬件见 §2.5。整板 30–80 M 单元共轭不适合在本机过夜批量跑（CFD-AI 评估 v1.0 §2.1）。
- 信息：NVIDIA/OEM 未公开封装图、功率图，所有几何是候选。
- PowerShell 会吞 `&` 和括号，多步命令写成脚本文件（`memory/semantic/environment.md`）。
- 第三方包只装进 `cad/.venv` 或专用 venv，不装进系统 Python（VeighNa），安装比照第①道闸门。

## 4 总体技术架构

### 4.1 分层架构

```svg:arch
交互层：Cursor / Claude Code 对话 | 冷板设计台 UI :8765 | md + html 报告 | 门控看板（新）
智能体层：orchestrator（薄）→ cp-design（主责）+ ai-matlab（路线 B）+ librarian + thermal-management
技能层：design-loop / cad-loop / cfd-loop / fluent-gui-capture（已有）+ 候选技能（§10.6）
工具适配层（MCP）：cp-design MCP（8 + 规划工具）| user-matlab MCP | Ansys 适配 | DAQ 适配 | FMU 互通
求解层：Python 1D/ROM（路线 A）| MATLAB/Simscape（路线 B）| build123d | SpaceClaim | Fluent/Meshing | Mechanical | optiSLang | AutoCAD
数据层：references | 设计点注册表（D-001）| memory | runs/ + manifest | 大文件索引 | Dify RAG
右侧纵条：平台闸门 ①②③ + 工程闸门 E1–E4（建议）
```

*图 4-1 · 平台分层架构（html 版为内联 SVG）。实线框为已有，虚线框为本规划新增或候选。AI 只通过 MCP 和文件接口驱动求解器。*

| 层 | 职责 | 已有 | 新增（本规划） |
|---|---|---|---|
| 交互层 | 对话、设计台、报告 | Cursor / Claude Code、`ui/`、HTML 报告 | 门控看板、CFD 作业页、本规划的 md + html 生成器 |
| 智能体层 | 拆解、路由、汇总、闸门 | orchestrator、cp-design、ai-matlab、librarian | 算例状态机（DR0–DR6），回路 R1–R4 编排约定 |
| 技能层 | 可复用的操作规程 | 4 个私有技能 | 候选技能 24 个（§10.6），先进 `_staging` |
| 工具适配层 | 把求解器变成可调用、带门的工具 | `cp-design` MCP 8 个工具、`user-matlab` MCP | 一维网络、CFD 批处理、流体域、出图、DAQ、V&V、ROM、FMU 工具 |
| 求解层 | 真正算数 | Python、build123d、Fluent、ICEM、SpaceClaim、MATLAB | Fluent Meshing、Mechanical、optiSLang、Simscape 模型、DAQ |
| 数据层 | 单一来源、版本、审计 | references、memory、runs/ | 设计点注册表、manifest、大文件索引；cas/dat/msh 不入 git，用清单和哈希追踪 |

### 4.2 多智能体分工

平台约定只有 `quant-research` 能派生子智能体，所以本项目前期**不新增注册智能体**，在 `cp-design` 内按角色拆技能。到 S33 再评审是否把 CAE、试验、孪生拆成独立智能体（新增要建模块、薄加载器并登记 `registry.json`，由人确认）。

| 角色 | 承担者 | 主要技能（现有 / 候选） | 调用的工具 |
|---|---|---|---|
| 编排 | `orchestrator` | 拆解、路由、汇总 | Task |
| 冷板设计主责 | `cp-design` | `design-loop`（现有） | MCP cp-design |
| 需求与输入 | `cp-design` + `librarian` | `design-point-registry`、`input-trace` | 设计点注册表、冲突检测、`rag-query` |
| 概念与选型 | `cp-design` + `librarian` + `thermal-management` | `tradeoff-matrix` | Python 矩阵脚本 |
| 一维计算（路线 A） | `cp-design` | `oned-calc`、`oned-uq`、`hydro-network` | `oned_*`、`hydro_network` |
| 一维 / 孪生 / 控制（路线 B） | `ai-matlab`（经 `.claude/agents/ai-matlab.md` 薄加载器） | `simscape-tray`、`control-sim`（B 段） | MCP user-matlab |
| CAD | `cp-design` | `cad-loop`（现有）、`cad-v2-kernel` | `cad_inspect`、`cad_build` |
| CFD | `cp-design` | `cfd-loop`、`fluent-gui-capture`（现有）；`cfd-batch`、`mesh-independence`、`cfd-reconcile`、`r1-loop` | `cfd_*` |
| FEA 与出图 | `cp-design` | `fea-loop`、`tolerance-stack`、`drawing-loop` | `fea_*`、`drawing_*` |
| 试验与 V&V | `cp-design` | `ttv-test`、`vv-loop` | `test_import`、`vv_compare` |
| 孪生与控制（路线 A） | `cp-design`（后期可拆） | `twin-rom`、`control-sim`（A 段） | `rom_*`、FMU |
| 文献与专利 | `librarian` | `rag-query`（共享） | MCP dify-rag |
| 行业与供应链 | `thermal-management` | — | WebSearch |

### 4.3 MCP 与工具接入

现有 `cp-design` MCP 的 8 个工具保留不变，按阶段新增。新增工具都遵循三条：先校验后执行；会写文件、占用求解器、花钱或动实物的工具必须 `confirm=true`；产物只写 `runs/`。

| 工具（规划） | 阶段 | 作用 | 底层 | 门 |
|---|---|---|---|---|
| `dp_list` / `dp_diff` | P0–P1 | 列设计点、比对两套设计点或报告数 | yaml + 解析器 | 无 |
| `oned_report` | P1 | 生成一维计算书 md/html/json | `oned_pkg` | 无 |
| `oned_sweep` / `oned_uq` | P1 | DOE、龙卷风、差距闭合、蒙特卡洛 | numpy / scipy | 样本数上限 |
| `hydro_network` | P1 | 板内 + 托盘水力网络、孔板配平 | scipy | 无 |
| `cad_inspect` / `cad_build`（扩展） | P2 | 支持 `pitch_x/pitch_y`、HBM 方案、Grace | `cad/coldplate` | ERROR 阻断；导出 confirm；E1 |
| `fluid_extract` | P2 | 抽流体域、命名面 | build123d / SpaceClaim 脚本 | 几何轨道校验 |
| `cfd_preflight` | P3 | 网格量、显存、许可、核数、已有 Fluent 进程检查 | 本机探测 | 显存门 |
| `cfd_job_submit` / `cfd_job_status` | P3 | 提交 journal/PyFluent 作业、查状态 | 子进程 / PyFluent | confirm；> 9 M 网格或 > 4 h 走 E2 |
| `cfd_extract` / `cfd_reconcile` | P3 | 解析 transcript、CSV，算 R、ΔP、能量比；一维–CFD 契合性、GCI | 解析器 | 只读 |
| `fea_run` | P4 | 承压、压装、热应力 | PyMechanical / MAPDL | confirm |
| `drawing_build` | P4 | DXF/PDF 候选图、BOM、检验表 | ezdxf | 冻结图纸覆盖需确认 |
| `test_import` / `vv_compare` | P5 | 试验 CSV 校验入库；V1–V5、V&V 20、R2 触发 | pandas / 解析器 | 只读 |
| `rom_build` / `rom_eval` / `fmu_export` | P6a | 代理模型训练、评估、FMU 打包（路线 A） | scikit-learn、pythonfmu | 无 |
| `ctrl_sim` | P6b | SIL 场景运行（路线 A 本地；路线 B 经 ai-matlab） | FMPy / do-mpc；Simulink | 无；HIL 走 E4 |

外部接入：

| 接入 | 方式 | 状态 | 说明 |
|---|---|---|---|
| MATLAB/Simulink | 已登记 `user-matlab`（`@mathworks/mcp-matlab`），由 `ai-matlab` 使用 | MATLAB R2025b 已安装；许可检出与 MCP 连通性待 S01 | 路线 B 主通道 |
| Ansys | 不另起 MCP，在 `cp-design` 内用 journal + PyAnsys 适配器 | Fluent 已在本机运行；PyAnsys 未装 | 安装比照① |
| CAD | build123d（现有）；SpaceClaim `/RunScript`（现有）；SolidWorks 宏（内核已有后端） | FreeCAD、SolidWorks 未装 | 见 §4.4.2 |
| OpenFOAM | WSL2 Ubuntu-22.04 或 Docker | WSL2 已有，OpenFOAM 未装 | 交叉校核，可后装（Q-17） |
| Onshape | REST API | 未接 | 云端，OEM 数据不宜上传，默认不用 |

### 4.4 选型对比与推荐

评分 1–5，5 最好。权重：本机可用性与许可 25%、自动化 / AI 可编程性 25%、工程可信度 20%、成本 15%、数据保密 15%（A 版权重；B、C 版权重排序结果一致）。

#### 4.4.1 一维与系统仿真（双路线）

| 方案 | 可用性 | 自动化 | 可信度 | 成本 | 保密 | 加权 | 适合做什么 |
|---|---|---|---|---|---|---|---|
| 路线 A：Python 自建（model.py + oned + zones + scipy） | 5 | 5 | 4 | 5 | 5 | **4.80** | 关联式、预算、DOE、UQ、水力网络、回归；唯一设计数值源 |
| 路线 B：MATLAB/Simulink + Simscape Fluids（经 `ai-matlab`） | 4 | 4 | 5 | 3 | 5 | **4.15** | 托盘 / CDU 系统级网络、瞬态、控制对象；与路线 A 对照 |
| Modelica（OpenModelica） | 2 | 4 | 4 | 5 | 5 | 3.80 | 开源动态系统，原生 FMU；未安装 |
| Ansys Twin Builder | 3 | 3 | 4 | 3 | 5 | 3.50 | ROM 集成、孪生部署；许可未知 |
| Flownex | 1 | 2 | 4 | 2 | 5 | 2.60 | 未装，不推荐首期 |

说明：A 版给 MATLAB 的可用性打 2 分，前提是“未探测到”。本版按 §2.5 核实结果改为 4 分（已装、许可特性在文件中，但未检出验证），加权由 3.55 升到 4.15。

推荐：**路线 A 为主**，稳态设计计算、规则判据、扫描与差距闭合全部在 Python，作为唯一数值源。**路线 B 并列**，用于托盘 / CDU 系统级、瞬态、控制对象，并对路线 A 做稳态对照：同一稳态点的 ΔTf、ΔP 偏差 < 1%，否则以 Python 为准并查 Simscape 参数。两者都只消费设计点注册表，不另存一套参数。MATLAB 许可检出失败时，路线 B 的系统模型改用 Python（scipy ODE），接口不变。

#### 4.4.2 CAD 概念设计与出图

| 方案 | 可用性 | 自动化 | 可信度 | 成本 | 保密 | 加权 | 备注 |
|---|---|---|---|---|---|---|---|
| build123d（OCC，现有内核） | 5 | 5 | 4 | 5 | 5 | **4.80** | 已有规则门和后端；共面布尔有段错误，需过切 |
| CadQuery | 4 | 5 | 4 | 5 | 5 | 4.55 | 同为 OCC，不必换 |
| SpaceClaim / Discovery 脚本 | 5 | 4 | 4 | 4 | 5 | 4.45 | 已用于上色和托盘示意；适合 CFD 前处理（共享拓扑、流体域） |
| ezdxf + AutoCAD 2024 审图 | 5 | 5 | 3 | 5 | 5 | 4.60 | 评审 / 询价级图纸；GD&T 需块库与模板 |
| FreeCAD（TechDraw） | 2 | 3 | 3 | 5 | 5 | 3.45 | 开源出 2D 图，需安装 |
| SolidWorks API / NX Open | 1 | 4 | 5 | 2 | 5 | 3.20 | 未装；发放级图纸与 GD&T 最完整 |
| Onshape | 4 | 4 | 4 | 3 | 1 | 3.35 | 云端，OEM 数据不宜上传 |

推荐：**build123d 继续做参数化主内核**，先补 `pitch_x/pitch_y`。**SpaceClaim 做 CFD 前处理**。**2D 候选图用 ezdxf 出、AutoCAD 2024 审**。**正式投产图由人在公司 CAD 定稿**，AI 只出 GD&T 草案、尺寸表和宏草稿（Q-12）。

#### 4.4.3 三维 CFD / 传热

| 方案 | 可用性 | 自动化 | 可信度 | 成本 | 保密 | 加权 | 备注 |
|---|---|---|---|---|---|---|---|
| Ansys Fluent（journal + PyFluent） | 5 | 4 | 5 | 3 | 5 | **4.45** | 已在用，有收敛算例与取图技能；原生 GPU 求解器 |
| OpenFOAM（chtMultiRegionFoam，WSL2） | 3 | 5 | 4 | 5 | 5 | 4.30 | 免许可，适合交叉校核和免许可扫描；设置与验证成本高 |
| Ansys CFX | 4 | 3 | 4 | 3 | 5 | 3.65 | 已装，无必要再引入 |
| Ansys Icepak | 3 | 3 | 4 | 3 | 5 | 3.50 | 托盘 / 机柜级；对 0.5 mm 孔常用降阶，会丢驻点（v2.0 §10.2） |
| STAR-CCM+ / COMSOL / FloTHERM | 1 | 3 | 5 | 1 | 5 | 2.80 | 未装 |

推荐：**Fluent 为主力**。它满足 v2.0 §10.2 的全部能力要求：共轭、低 Re/转捩、高纵横比网格、逐孔流量、批处理。自动化以 **journal 为底线、PyFluent 为便利层**，这个优先级 CFD-AI 评估 v1.0 §4 已经定过。**OpenFOAM 作开源校核**（V1 代码验证、单胞交叉对比），不作交付求解器。**Icepak 留给托盘级**。⑤ 工具链的最终选定与 Ansys 许可范围一起列为 Q-04。

#### 4.4.4 网格

| 方案 | 适用 | 推荐 |
|---|---|---|
| ICEM CFD hex（replay） | 单胞、12 格带等规则几何，已有黄金 replay | 单胞与局部带继续用 |
| Fluent Meshing 水密流程（poly-hexcore） | 整板、半板、含静压箱与歧管 | 整板首选，需建立黄金流程 |
| PyPrimeMesh | 网格脚本化 | 视许可，作为 Fluent Meshing 的脚本层 |
| gmsh / snappyHexMesh | OpenFOAM 路线 | 仅备选 |

#### 4.4.5 结构 FEA

推荐 **Ansys Mechanical（PyMechanical / PyMAPDL）**，做 3 bar 承压、300–500 N 压装、焊后热应力与平面度，可映射 Fluent 温度场；**CalculiX** 作开源备选。v2.0 §6.3 的解析板条保留为一维对照：喷嘴板跨 26 mm 时 16.73 MPa、2.65 μm。

#### 4.4.6 优化与 DOE

推荐 **Python（scipy、optuna）+ 一维模型** 做大规模筛选，覆盖 D-001 全包络；**optiSLang**（已装）在 CFD 级 DOE 和稳健性分析时使用。原则：一维筛到 3–5 个候选，再上 CFD；R1 回路的 AI 自动参数扫描与优化也走这条线（S39）。生成式拓扑流道（arXiv 2604.10941 / 2608.22787）列为 P6 之后的研究选项。

#### 4.4.7 数字孪生与控制

两条并列路线，详见第 9 章。简述：路线 A 用 Python ROM / RC 网络 → FMU，控制在 Python SIL；路线 B 用 Simscape Fluids 孪生 + MPC / RL Toolbox，在 Simulink 中做 SIL / HIL。两条路线以一维模型为共同源、FMU 为互通接口，选哪条由用户决定（Q-07）。

### 4.5 分级仿真路线

为避免整板起步，按网格量级分级推进（B 版）：

| 级别 | 对象 | 网格量级 | 本机可行性 | 目的 | 步骤 |
|---|---|---|---|---|---|
| L0 | 代码验证（层流圆管 fRe、平板） | < 1 M | 可 | V1 | S16 |
| L1 | 单元胞（已有）+ Re ≈ 3000 锚定；D0.40 / D0.50 | 2–5 M | 可（`-t1 -gpu` ≤ 9 M） | V4、局部 h、孔口压降、GCI | S16、S17 |
| L2 | 单 die 条带 / 108 孔 | 8–15 M | CPU 可，GPU 不行 | 交叉流、流量一致性趋势 | S18 |
| L3 | 1/2 对称整板共轭（禁止 1/4） | 15–40 M | 需 HPC / 云 | Q1–Q8 正式结论；PC-1…PC-6 | S18、S19 |
| L4 | 全板 + 水嘴 + 歧管 | 30–80 M | 需 HPC | DR3 终版、PG25 压降 | S19 |
| S1 | Mechanical 压装 / 承压 / 热变形 | 1–5 M | 可 | 平面度、HBM 偏载 | S20 |

### 4.6 推荐技术栈总表

| 层 / 环节 | 推荐 | 本机状态（§2.5） | 需确认 |
|---|---|---|---|
| 编排 | Cursor / Claude Code + `cp-design` + `ai-matlab` + `librarian` | 已有 | — |
| 一维 | 路线 A Python 一维包；路线 B Simscape Fluids | Python 已有；MATLAB 已装 | 许可检出（Q-08） |
| CAD | build123d + SpaceClaim 脚本 | 已有 / 已装 | SpaceClaim 许可 |
| CFD | Fluent + Fluent Meshing + PyFluent；OpenFOAM 交叉 | Fluent 已装；PyFluent 未装；WSL2 有 | 许可、HPC、PyFluent 安装（Q-04、Q-09） |
| 结构 | Ansys Mechanical | 已装 | 许可 |
| 优化 / 代理 | optuna / scikit-learn；optiSLang | scikit-learn 已在 `cad/.venv`；optiSLang 已装 | optiSLang 许可；optuna 安装 |
| 图纸 | ezdxf + AutoCAD 2024 | 已有 / 已装 | 是否需要 SolidWorks（Q-12） |
| 试验 | Python DAQ + 自建台；MATLAB Data Acquisition（路线 B） | 无台架 | 自建或外协、预算（Q-13） |
| 孪生 | 路线 A：Python ROM + pythonfmu/FMPy；路线 B：Simscape + Simulink Compiler FMU；可选 TwinAI | FMPy / pythonfmu 未装 | 路线选择（Q-07）；安装（Q-09） |
| 控制 | 路线 A：do-mpc / CasADi；路线 B：MPC / RL Toolbox、Simulink Test、Simulink Real-Time | CasADi 未装；MATLAB 特性在许可文件中 | 同上；HIL 硬件 |

### 4.7 本机算力与授权约束

| 资源 | 现状 | 规划中的用法 |
|---|---|---|
| CPU 24 核 / 128 GB | 已测 | 单胞、12 格带、单 die 阵列；整板需评估 HPC |
| RTX 4090 24 GB | 空闲约 21.5 GB | `-t1 -gpu` 不超过约 900 万单元，`-t4 -gpu` 不超过约 240 万，不用 `-gpgpu`；超线只用 CPU（`skills/cfd-loop`） |
| 整板 L3/L4 | 按 2.2 GB/百万单元估：80 M 约 176 GB 显存，或 128–256 核 CPU、0.5–1 TB 内存 | HPC / 云，预计 20–40 次求解（Q-10） |
| Ansys 2026 R1 | 已装，Fluent 已运行 | 许可模块（Mechanical、optiSLang、TwinAI/Twin Builder、HPC 核数）由 S01 核实 |
| MATLAB R2025b | 已装，许可特性在文件中 | S01 经用户同意后检出验证；路线 B 依赖 |
| SolidWorks / NX / FreeCAD | 未装 | Q-12 |

## 5 设计流程模型（门控 + 回路迭代）

### 5.0 流程总图

```svg:flow
① 需求与输入 → ② 概念与选型 → ③ 性能设计 → ④ 一维计算 → ⑤ 三维仿真 → ⑥ 机械与图纸 → ⑦ 样件与试验 → ⑧ 数字孪生模型 → ⑨ 孪生在环 AI 控制
  DR0 输入冻结   DR1 方案选定   DR2 性能基线   DR2 闸门      DR3 仿真通过   DR3 闸门        DR4 送样放行    DR5 孪生验收      DR6 控制策略放行
R1 ⑤ 仿真不达标 → 回 ③/④ 改几何（孔径、阵列密度、TIM2），AI 自动参数扫描 / 优化
R2 ⑦ 试验与仿真偏差 > 15% → 修正模型回 ③（V&V，ASME V&V 20）
R3 ⑧ 孪生与实测持续比对，超阈值重新标定
R4 ⑨ 控制策略效果反哺设计指标（流量余量、压降预算）→ ③
```

*图 5-1 · 设计流程模型 v1.1（门控 + 回路迭代）。html 版为内联 SVG，每张阶段卡片含内容、“AI 赋能/工具”一行、状态与对应实施 Phase；流程图截图见 `docs/plan/assets/AIDC液冷设计平台_设计流程模型_v1.1_20261002.png`。*

同一模型的文字表达：

| 阶段 | 主要内容 | AI 赋能 / 工具 | 门控 | 状态（2026-10-02） | 实施 Phase / 步骤 |
|---|---|---|---|---|---|
| ① 需求与输入 | 芯片规格 / 热包络、机柜水力表、接口与标准、D-001 工况 | librarian RAG 抽取、追溯矩阵、冲突检测（`dp_diff`） | DR0 输入冻结 | 已完成（有条件：6 项缺失输入） | P0：S01–S03、S34–S36；P1：S37 |
| ② 概念与选型 | 方案权衡矩阵、分区策略、专利 FTO 初筛 | 矩阵复算与权重敏感性、权利要求对照草稿 | DR1 方案选定 | 已完成（分区杂交 4.50） | P1：S37 |
| ③ 性能设计 | 热阻预算分配、射流参数窗、流量 / 压降预算 | 预算倒推、设计窗门、PG25 6~10 K 扫描 | DR2 性能基线 | 已完成（水口径）；**DR2 有条件通过，PG25 口径下待重算** | P1：S05、S07 |
| ④ 一维计算 | 能量平衡、水力与换热关联式、敏感性与差距闭合 | 路线 A Python 1D（主）、路线 B Simulink agent（对照）、DOE/UQ、水力网络 | DR2 闸门 | 同上 | P1：S04–S09、S38 |
| ⑤ 三维仿真 | 共轭 CFD、网格无关性、PG25 6 工况矩阵 | Fluent 批处理、GCI、V&V、R1 自动扫描；**工具待决策（Q-04）** | DR3 仿真通过（+ E2） | 工具待决策；单胞级已有 | P2：S10–S11；P3：S14–S19、S34、S39 |
| ⑥ 机械与图纸 | 层叠与公差、承压 / 变形、2D/3D/爆炸图 | build123d、Mechanical FEA、ezdxf 出图、GD&T 核对 | DR3 闸门（+ E1） | 未开始（仅候选几何与解析校核） | P2：S10–S13；P4：S20–S22 |
| ⑦ 样件与试验 | TTV 热阻、流阻曲线、红外 / 氦检 | DAQ 脚本、不确定度预算、V&V 20 偏差判读 | DR4 送样放行（+ ③/E4） | 未开始 | P5：S23–S26 |
| ⑧ 数字孪生模型 | ROM / 代理模型、动态热–水力网络、FMU、在线标定 | 路线 A Python ROM → FMU；路线 B Simscape Fluids 孪生 | DR5 孪生验收 | 未开始 | P6a：S27、S28、S30；P1：S38 |
| ⑨ 孪生在环 AI 控制 | PID 基线 / MPC / RL、MIL → SIL → HIL、安全屏蔽；温升 6~10 K、负载 1100~1400 W | 路线 A Python MPC/RL SIL；路线 B MPC / RL Toolbox、Simulink SIL/HIL | DR6 控制策略放行（+ E4） | 未开始 | P6b：S29、S40 |

回路一览：

| 回路 | 触发 | 回到 | AI 动作 | 步骤 |
|---|---|---|---|---|
| R1 仿真回路 | CFD 得到的 Rθ 超目标、ΔP > 20 kPa、分区或逐孔偏差 > ±10%、HBM 近壁 > 0.80 m/s | ③ / ④ 改几何（孔径、阵列密度、TIM2） | 自动参数扫描 / 优化，筛出 3–5 个变体 | S07、S19、S39 |
| R2 验证回路 | 试验与仿真偏差 > 15% | ③（修正 ④ 的关联式与系数） | V&V 20 判读、偏差分解、反标定 | S25 |
| R3 孪生标定回路 | 孪生与实测（台架 / 回放）持续比对，残差超阈值 | ⑧ 重新标定 | 卡尔曼 / 滑窗最小二乘标定，模型升版 | S30 |
| R4 控制反哺回路 | 控制策略评估得到所需流量余量、压降预算、温升区间 | ③ 设计指标 | 汇总控制 KPI，提出设计指标修订建议 | S29、S40 |

每一步的写法统一为：输入 → AI 动作 → 工具 → 输出 → 验收 → 现状。

### 5.1 ① 需求与输入（DR0 输入冻结）

| 项 | 内容 |
|---|---|
| 输入 | 芯片规格与热包络（B300 1100/1400 W、Grace 300 W）、机柜水力表（Lenovo LP2357 表 27）、接口与标准（OCP、ASHRAE、UQD）、D-001 工况（PG25、1400 W 基线、6~10 K、1100 W 校核）、限值（孔速 ≤ 2.0 m/s、近壁 ≤ 0.80 m/s、ΔP ≤ 20 kPa） |
| AI 动作 | 经 `librarian` 检索公开资料并抽取数字，每条带来源、日期、置信度；生成输入追溯矩阵（IN-*）与假设登记册（AS-*）；比对报告、xlsx、yaml 找冲突（K-01～K-14）；为缺失项生成索取清单；ICD 到位后做影响分析 |
| 工具 | `rag-query`、`dp_list`、`dp_diff`、设计点注册表 |
| 输出 | `designpoints/*.yaml`（含 D-001 矩阵）、输入追溯矩阵、假设登记册、冲突清单、OEM 索取清单 |
| 验收 | 每个“缺失”项都有责任人和计划日期；冲突清单为零或每项都有处理决议；人签 DR0 |
| 现状 | v2.0 §3 与 `01_DR0_输入追溯.xlsx` 已有矩阵，含 6 项缺失；D-001 已决；G-01、G-03、G-04 未闭合 |

### 5.2 ② 概念与选型（DR1 方案选定）

| 项 | 内容 |
|---|---|
| 输入 | 技术调查 v1.3 五条路线；专利 v1.4 方案 A/B/C 与雷区；DR0 输入 |
| AI 动作 | 复算加权矩阵（4.50 / 3.20 / 2.95 / 2.85）并做权重敏感性（±20% 时名次是否翻转）；把方案 A 的必要技术特征（HBM 无喷嘴、近壁流速上限、隔离肋双重功能、压降窗）映射到几何参数；对照 Intel DLMJ、US12029008B2、US10244654、CN111328245B、CN113871359A、WO2026103052A1，起草差异点对照表 |
| 工具 | `rag-query`；Python 矩阵脚本 |
| 输出 | 方案决策矩阵、敏感性结果、分区策略、FTO 对照草稿（标明“非法律意见”） |
| 验收 | 权重有量化依据；敏感性下第一名稳定；FTO 无红灯或红灯已有规避；人签 DR1 |
| 现状 | 已完成；FTO 只是初筛（G-11） |

### 5.3 ③ 性能设计（DR2 性能基线）

| 项 | 内容 |
|---|---|
| 输入 | DR1 方案；结温包络；Rpkg 0.008–0.012、TIM2 0.004–0.008 °C/W 假设；D-001 工况矩阵；Q-02 目标线 |
| AI 动作 | 从 Tj 倒推热阻预算，分配到 TIM2、铜壁、对流；给流道参数初值（D、Sx、Sy、H/D、槽宽深、HBM 截面）；在 PC-1…PC-6 下做流量与压降预算；每个参数标注所在窗口和越窗风险 |
| 工具 | `oned_design`、`oned_sweep` |
| 输出 | 热阻预算表（PG25 版）、参数初值表、流量 / 压降预算 |
| 验收 | 预算闭合（各段加和等于目标）；每个参数在文献窗内或写明越窗理由；6 K 与 10 K 两端都给结论 |
| 现状 | v2.0 §5 完成（水口径）；PG25 / D-001 下的预算尚未重做 |

### 5.4 ④ 一维计算（DR2 闸门）

| 项 | 内容 |
|---|---|
| 输入 | ③ 的参数；设计点注册表（D-001） |
| AI 动作 | 路线 A：运行一维工具出计算书；三模型上下界；两套 PG25 物性各算一遍；1100~1400 W × 6~10 K 扫描；孔径、TIM2、槽深敏感性；差距闭合矩阵（所需 h）；回归测试；托盘水力网络。路线 B：`ai-matlab` 用 Simscape Fluids 搭同一稳态点与托盘网络做对照 |
| 工具 | `oned_report`、`oned_sweep`、`hydro_network`；`user-matlab` MCP |
| 输出 | 一维计算书（md/html/json）、敏感性图、差距闭合表、回归报告、双路线对照表 |
| 验收 | 回归全过；能量平衡自洽；结论分“通过 / 不判定 / 不通过”三档；给出最优先杠杆；双路线稳态差 < 1%；人签 DR2 |
| 现状 | v2.0 §9 完成，有条件通过（区间跨目标线）；缺自动回归、缺 PG25 热阻、缺托盘水力 |

### 5.5 ⑤ 三维仿真（DR3 仿真通过）

| 项 | 内容 |
|---|---|
| 输入 | 候选几何（STEP + 命名面）；v2.0 §10 需求规格（Q1–Q8、V1–V5）；D-001 6 工况矩阵（PC-1…PC-6）+ v2.0 C01–C12 补充子集 |
| AI 动作 | 写 journal / PyFluent 脚本；预检网格量与显存；提交与监控作业；解析残差、监视量、能量与质量守恒；网格无关性；V1、V4 锚定；整理逐孔流量与压力分段；按 `fluent-gui-capture` 取报告图；与一维对表；不达标时启动 R1 自动参数扫描 |
| 工具 | `cfd_preflight`、`cfd_job_*`、`cfd_extract`、`cfd_reconcile`；Fluent、ICEM、Fluent Meshing；可选 OpenFOAM |
| 输出 | CFD 报告、网格无关性报告、工况矩阵汇总、一维修正建议、几何修改建议 |
| 验收 | AC-4、AC-5；R 与 ΔP 落在 Q-02 目标内，否则触发 R1；大算例经 E2；人签 DR3 仿真通过 |
| 现状 | 单胞与 12 格带已有收敛场（水、D0.40）；V1/V4、无关性、整板、PG25 均未做；**工具最终选定待 Q-04** |

### 5.6 ⑥ 机械与图纸（DR3 闸门）

| 项 | 内容 |
|---|---|
| 输入 | 冻结候选几何（E1）；工艺路线；压装力与 UQD（待 ICD） |
| AI 动作 | 层叠与尺寸链校核（名义 + 统计）；公差分配；承压、压装、热应力 FEA；出 2D/3D/爆炸图候选与 BOM；图纸检查清单（标题栏、剖切、孔位表、GD&T、焊接符号） |
| 工具 | `cad_build`、`fea_run`、`drawing_build`；Mechanical；SpaceClaim；AutoCAD 2024 审图 |
| 输出 | FEA 报告、公差与尺寸链表、候选图纸包（DXF/PDF/STEP）、BOM、询价包草案 |
| 验收 | 尺寸链全部闭合；3 bar 下安全系数 ≥ 2、平面度变化 ≤ 0.02 mm；图纸检查清单全过；人签 DR3 闸门；对外发图比照③ |
| 现状 | v2.0 §6、§8 有候选图与解析校核；无 FEA、无正式 GD&T |

### 5.7 ⑦ 样件与试验（DR4 送样放行）

| 项 | 内容 |
|---|---|
| 输入 | DR3 图纸包；试验大纲 v2.0 §11；D-001 角点工况（PC-1、PC-3、PC-4、PC-6 + PC-2 中心点） |
| AI 动作 | 写试验大纲与台架 BOM；GUM / PTC 19.1 不确定度预算；DAQ 脚本与数据模板；导入校验；V&V 20 对比；偏差 > 15% 时开 R2 工单并给反标定建议 |
| 工具 | `test_import`、`vv_compare` |
| 输出 | 试验报告、V&V 报告、出厂三曲线（流阻、热阻、红外）、DR4 放行包 |
| 验收 | AC-7、AC-8；TTV Rθ 达 Q-02 目标；两 die 中心温差 ≤ 5 K；设计流量下 ΔP ≤ 18 kPa；100% 氦检；人签 DR4；采购、外协、通电比照③ / E4 |
| 现状 | 未开始；DR4 门表实测列为空 |

### 5.8 ⑧ 数字孪生模型（DR5 孪生验收）

| 项 | 内容 |
|---|---|
| 输入 | 一维模型（两路线的共同源）；CFD DOE（S19）；试验数据（S24、S26）；D-001 包络（1100~1400 W、6~10 K、Tin 40~45 °C） |
| AI 动作 | 路线 A：多保真度 ROM（GP / 响应面）+ 3–5 节点 RC 热网络 + 水力网络，Python ODE，pythonfmu 导出 FMU。路线 B：`ai-matlab` 用 Simscape Fluids（Thermal Liquid）搭冷板–托盘–CDU 孪生，嵌入路线 A 的 ROM FMU 或查表，Simulink Compiler 导出 FMU。两路线互相导入对表；在线标定与回放（R3） |
| 工具 | `rom_build`、`rom_eval`、`fmu_export`；FMPy；Simscape Fluids；可选 TwinAI |
| 输出 | ROM、动态孪生（两路线）、FMU、标定记录、孪生 V&V 报告、DR5 验收包 |
| 验收 | AC-9；越域输入返回警告并回退一维；人签 DR5 |
| 现状 | 未开始 |

### 5.9 ⑨ 孪生在环 AI 控制（DR6 控制策略放行）

| 项 | 内容 |
|---|---|
| 输入 | ⑧ 的 FMU；控制需求：温升设定值 6~10 K、负载 1100~1400 W，约束 ΔP ≤ 20 kPa、孔速 ≤ 2.0 m/s、HBM 近壁 ≤ 0.80 m/s、Tj 上限（Q-02） |
| AI 动作 | PID 基线；MPC（显式约束）；RL 只在孪生上训练、带安全屏蔽，作研究项；场景库（负载阶跃 / 斜坡、温升切换、进液 45 °C、堵塞 20%、泵降级）；MIL → SIL → HIL；鲁棒性（ROM 误差 ±10%、传感器噪声）；R4：输出流量余量、压降预算建议 |
| 工具 | 路线 A：FMPy + do-mpc / CasADi（RL 可选 gymnasium + SB3）；路线 B：Simulink + MPC Toolbox / RL Toolbox、Simulink Test、Simulink Real-Time |
| 输出 | 控制需求与约束表、PID / MPC / RL 控制器（两路线）、场景库、SIL 报告、HIL 联调报告、R4 反哺建议、DR6 放行包 |
| 验收 | AC-10；MPC 相对 PID 的泵功、超调、约束违反次数有量化对比；安全层在注入故障时 100% 拦截越限指令；人签 DR6 |
| 现状 | 未开始 |

### 5.10 DR 门控汇总

| 闸门 | 放行条件（摘要） | AI 准备的闸门包 | 签字 | 现状 |
|---|---|---|---|---|
| DR0 输入冻结 | 缺失项有责任人和日期；冲突清零；D-001 落盘 | 追溯矩阵、假设登记册、冲突清单 | 用户 | 有条件（6 项缺失） |
| DR1 方案选定 | 权衡矩阵有量化权重；FTO 无红灯 | 矩阵 + 敏感性 + FTO 对照 | 用户 | 已完成 |
| DR2 性能基线 / DR2 闸门 | 预算闭合；一维可复算；有杠杆；D-001 全包络有结论 | 计算书 + 回归报告 + 差距闭合 + 双路线对照 | 用户 | 有条件（区间跨线；PG25 待重算） |
| DR3 仿真通过 | 网格无关、守恒、V4、PC-1…PC-6 下 R 与 ΔP 达标 | CFD 报告 + 无关性 + V&V(V1–V4) | 用户 + 仿真负责人 | 未完成 |
| DR3 闸门 | 尺寸链闭合；FEA 通过；图纸清单过 | FEA + 图纸包 + BOM | 用户 + 结构/工艺 | 未完成 |
| DR4 送样放行 | TTV、氦检、流阻曲线达标；V5 ≤ 15% 或 R2 闭环 | 试验报告 + V5 + 三曲线 | 用户 | 未开始 |
| DR5 孪生验收 | ROM 对 CFD ≤ 5%、对试验 ≤ 10%；两路线稳态差 < 2%；越域检测可用 | 孪生 V&V 报告 + FMU + 标定记录 | 用户 | 未开始 |
| DR6 控制策略放行 | SIL 零约束违约；相对 PID 有量化收益；HIL 联锁有效 | 控制报告 + 场景库结果 + R4 建议 | 用户 | 未开始 |

### 5.11 四条迭代回路

| 回路 | 触发条件 | 回到 | 杠杆 / 方法 | AI 的动作 | 收敛控制 |
|---|---|---|---|---|---|
| R1 仿真回路 | CFD 的 Rθ 超目标；ΔP > 20 kPa；分区流量或逐孔偏差 > ±10%；HBM 近壁 > 0.80 m/s | ③ / ④ | 按 v2.0 §4.2 优先级：孔径 0.50 → 0.40/0.35（PG25 下孔速 2.0 m/s 对应下限约 0.36 mm）；TIM2 ≤ 0.004；温升 6 K 档或提流量；阵列加密；槽深 1.5 → 0.8–1.0 | 用 CFD 标定一维 h（`h_scale`），在可行域内自动扫描或优化（optuna / optiSLang），给 3–5 个候选 overlay 并过规则门，人选后再上 CFD | 达标；或连续两轮改善 < 5%；或 3 轮仍不达标，升级为方案评审回 ② |
| R2 验证回路 | TTV 实测与 CFD 偏差 > 15%（且 u_val < 15%，可判） | ③（修正 ④ 的关联式与系数） | ASME V&V 20：E = S − D，u_val = √(u_num² + u_input² + u_D²) | 偏差分解（测量 → 装配 → 样件 → 模型）、反标定（h 倍率、TIM2、K、接触热阻）、模型升版并保留旧版 | 修正后复核 ≤ 15%；口径变化经 E3 |
| R3 孪生标定回路 | 孪生与实测残差（出水温度、ΔP、Tcase）持续超阈值（如出水温度 > 0.5 K 或热阻漂移 > 5%） | ⑧ | 卡尔曼滤波或滑动窗口最小二乘；参数：TIM2 等效热阻、分区流量系数、K | 自动标定、生成标定记录、触发孪生升版；漂移持续可能是堵塞，发预警 | 标定后残差回到阈值内；连续失败上报 |
| R4 控制反哺回路 | 控制评估显示流量余量不足、压降预算紧、温升区间需收窄或可放宽 | ③ 设计指标 | 控制 KPI → 设计指标：最大所需流量（含瞬态）、对应 ΔP、泵功、可用温升区间 | 汇总 SIL/HIL 结果，写设计指标修订建议，经人确认后更新注册表 | 指标修订进入下一轮 ③ / ④ |

每触发一次回路，都留一条 episodic 记忆（触发量、杠杆、结果）。这些记录是后面训练 ROM 和总结设计规律的原始数据。

### 5.12 人工闸门与工程闸门

平台三道闸门保持不变。下面四道工程闸门来自 B 版建议，本版建议**先在模块内试行**；写进平台宪法属于平台层变更，需用户决定（Q-06）。

| 闸门 | 触发 | AI 能做到 | 人确认后 | 涉及步骤 |
|---|---|---|---|---|
| 平台 ① 技能安装 | 新技能入库；第三方 Python 包、开源求解器安装（比照） | 起草 SKILL.md 放 `_staging`；列包名、版本、来源 | 登记 registry / 安装 | S04、S14、S20、S27、S32、S38 |
| 平台 ② 记忆继承 | 采纳祖先记忆 | 筛选 ≥ 0.6、未过期、近期复核 | 采纳 | S02、S15、S32、S34 |
| 平台 ③ 资金 / 实物（比照） | 外协下单、采购、付费算力、对外发图、试验台通电、向真实设备下发设定值 | 询价包、采购清单、安全检查表草案 | 下单 / 付费 / 上电 | S18、S22、S23、S26、S40 |
| E1 几何冻结变更 | 改冻结 yaml、覆盖已发 STEP、内核升版 | 候选几何进 `runs/` | 升版并冻结 | S10、S12、S13、S22 |
| E2 大算例启动 | 网格 > 9 M、预计 > 4 h、占用 HPC | 估算网格 / 显存 / 时长 / 费用 | 提交 | S16–S19、S39 |
| E3 门控放行 | DR0–DR6 放行；模型修正替代旧模型 | 证据包与判读 | 放行或退回 | S03、S09、S19、S22、S25、S26、S30、S40 |
| E4 实物动作 | 测试台加热、泵阀控制、HIL 下发 | 模拟、草案、安全检查表 | 上电 / 下发（硬件联锁在先） | S26、S40 |

### 5.13 AI 的能力边界

| AI 可以主责 | AI 辅助、人主责 | 只能人做 |
|---|---|---|
| 写参数、跑规则门、生成 STEP、写 journal、解析日志、对表、出候选图和报告、生成变体、检索摘要、起草试验大纲、估算网格 / 显存 / 时长 / 费用、在规则门内生成候选、起草技能与记忆候选 | 网格拓扑设计（黄金 replay）、发散时的局部修复、FEA 边界合理性、图纸 GD&T、控制器权重整定 | 签 DR 闸门、冻结几何与设计点、改规则本身、对外发图、下采购和外协订单、实物上电和试验操作、HIL 下发、许可证管理、批准技能与记忆入库 |

AI 在每阶段明确不做的事：不把单元胞热阻写成整板保证值，不把一维区间写成保证值；不把概念图加粗肋、Grace 槽宽、asm_0921 的 12.5 mm 写进 B300 参数；不覆盖冻结 yaml 与已发 STEP；内核认识 `pitch_x` 之前不声称建出 216 孔 v2；不替托盘 ICD 冻结流量、串并联与水嘴；不对真实泵、阀、加热台发闭环指令。

## 6 一维计算工具设计

### 6.1 定位与原则

- **唯一数值源**：设计数值只来自路线 A（`design/calc/model.py` 及其扩展）。报告、xlsx、UI、MCP 都调用它，不另抄数字（v2.0 §4.3 原则推广到全平台）。路线 B 只作对照与系统级扩展，不另存参数。
- **D-001 为默认口径**：工具缺省设计点改为 DP-P1400-6K，水 DP-A/DP-B 保留为回归用例，旧接口不带设计点时行为不变。
- **适用域门控**：每个关联式带适用域，越域时自动降级并给出警告（`oned.py` 已有 Martin 门控）。
- **证据等级标注**：输出里每个结论带 E 等级和“保证值 / 对照值”身份。
- **不改冻结件**：先用回归测试锁住 `oned.py`、`zones.py`、`model.py`，再逐步重构，重构期间旧接口保持兼容。

### 6.2 路线 A 模块划分（AI 自研 Python）

| 模块 | 内容 | 现有来源 |
|---|---|---|
| `props` | 物性库：水、PG25（`pg25_model` = model.py PG25_40；`pg25_dowfrost` = DOWFROST LC 25；供应商表待 Q-01）、铜；温度曲线 | `model.py`；HBM 1D v1.0 |
| `correlations` | Martin 1977、驻点、Shah & London、层流发展段、肋效率、孔口 K；每式带适用域与来源 | `model.py` |
| `zones.gpu_jet` | 射流区热阻、压降、Martin 门控、孔径杠杆、孔速上限 `JET_V_CAP` | `oned.py` |
| `zones.hbm` | HBM 多方案（A 横流 16×0.60×1.50 / B 交错 7×0.80×2.00 / C 中心进液 7×0.80×2.00 / D 11×0.45×2.00 + 静压仓） | `zones.py`、HBM 1D v1.0 |
| `zones.grace` | 平行交错槽、孔板配平 | `zones.py`、`CP-GRACE-MC-01_calc.py` |
| `chain` | 热阻链、温度语义（Tf/Tw/Tj）、预算闭合 | `model.py` r_chain |
| `network` | 水力网络：节点–支路，孔板、UQD、歧管、冷板曲线；Newton 迭代 | 新建 |
| `sweep` / `uq` | DOE（D-001 全包络）、龙卷风、差距闭合、Pareto、蒙特卡洛 | `model.py` orifice_sweep |
| `calib` | 用 CFD / 试验反标定 K 与 Nu 系数（R1/R2 共用） | 新建 |
| `fmu` | 把稳态一维与 RC 网络包成 FMU（pythonfmu），供路线 B 与孪生使用 | 新建（S38） |
| `report` / `cli` | 计算书 md/html/json；`python -m oned_pkg run --dp DP-P1400-6K` | `make_cycle.py` 模式 |

### 6.3 路线 B（MATLAB/Simulink agent）

| 项 | 内容 |
|---|---|
| 承担者 | `ai-matlab`，经薄加载器 `.claude/agents/ai-matlab.md` 引导，加载模块正文；通过 `user-matlab` MCP 运行脚本与测试 |
| 模型 | Simscape Fluids（Thermal Liquid）：冷板用一维压降–流量曲线与热阻集总参数（来自路线 A 计算书或 FMU）；托盘 4 GPU + 2 Grace 并联、孔板、UQD 4–8 kPa/对、泵与阀 |
| 参数 | 从 `designpoints/*.yaml` 读（先由 Python 转 json，MATLAB `jsondecode`），不在 slx 里手填数字 |
| 产物 | `AP/twin/simscape/*.slx`（二进制难 diff，同时导出参数 json 与结果 CSV）；对照表 |
| 对照判据 | 同一稳态点与路线 A 的 ΔTf、ΔP 偏差 < 1%（单板）/ < 5%（托盘分配，含 UQD 模型差），否则以 Python 为准并查 Simscape 参数 |
| 前提 | MATLAB 许可检出验证通过（S01，Q-08）；不通过则路线 B 暂停，不阻塞主线 |

### 6.4 设计点数据模型

设计点放在 `AP/designpoints/`，一个文件一个设计点，字段示例：

```yaml
id: DP-P1400-6K       # D-001 设计基线（PC-1）
status: baseline      # baseline / check / regression / superseded
decision: D-001
source: references/NVIDIA_B300_微通道冲击换热冷板设计报告_v2.1_PG25_20260929.html#1
date: 2026-10-02
confidence: 0.7       # 物性待 Q-01
fluid: {name: PG25, T_in_C: 40, props_ref: props/pg25_model}   # 正式物性待 Q-01
power: {total_W: 1400, gpu_core_W: 910, hbm_W: 43.7, hbm_n: 8, other_W: 140}
dT_target_K: 6        # 可调范围 6~10
flow: {total_lpm: 3.512, gpu_core_lpm: 2.283, hbm_each_lpm: 0.1096}   # 由 P/(rho*cp*dT) 派生
geometry_ref: geo/b300_v20_216.yaml
targets: {R_c_in_max: TBD-Q02, dP_max_kPa: 20, V_hbm_max: 0.80, V_jet_max: 2.0}
```

初始建：`DP-P1400-6K/8K/10K`（PC-1/2/3）、`DP-P1100-6K/8K/10K`（PC-4/5/6，同流量校核）、`DP-P1400-6K-45`、`GRACE-P25-6K/8K/10K`，以及回归点 `DP-A-W`、`DP-B-W`（水）。HBM 截面用 `geo/hbm_A…D.yaml` 登记，`current: true` 只能有一个。流量字段由脚本按 ΔT 派生，不手填。

### 6.5 关联式库与适用域

| 关联式 | 适用域 | 越域处理 | 来源 |
|---|---|---|---|
| Martin 1977 阵列面平均 | 2000 ≤ Re ≤ 1e5；0.004 ≤ f ≤ 0.04；2 ≤ H/D ≤ 12 | 只作外推对照，不进保证值 | v2.0 §9.4 |
| 驻点核 Nu0 = 0.5 Re^0.5 Pr^0.4 | 孔正下方约 2D 范围 | 不代表整胞平均 | v2.0 §9.4 |
| 层流发展段 Nu = max(4, 1.86 Gz^1/3) | Re < 2000，矩形槽 | Re > 2000 警告 | `oned.py` |
| Shah & London f·Re | 层流矩形槽 | 同上 | v2.0 §9.5 |
| Grace Nu = 4.8 | 三面受热矩形槽假设 | 标“假设，不是关联式” | Grace v1.0 §5 |
| 孔口 K = 1.8 | 锐边孔 | 由 CFD 反标定（12 格带 +27.6%，路径不同） | v2.0 §9.3 |

关联式升级候选（经 `librarian` 检索后再定）：低 Re 液体阵列射流关联式（覆盖 Re 300–2000，PG25 下尤其需要）、带短槽回流的复合模型。新关联式入库前要有 CFD 或试验对照，并在记忆里写适用域。

### 6.6 水力网络

节点–支路模型：供液歧管 → UQD → 冷板入口 → 静压箱 → 孔口（216 并联）→ 槽 → 回液缝 → 出口 → UQD → 回液歧管。托盘层是 4 块 GPU 冷板与 2 块 Grace 冷板并联，Grace 入口孔板配平。每条支路的压降 ΔP = R·Q + K·ρV²/2，CFD 或试验得到的曲线可以替换解析支路。输出：各支路流量、压降、孔板孔径建议。验证用例：Grace PG25 0.8 L/min 下 4×1.04 mm 孔板 22.9 kPa（Grace v1.1 §3）。D-001 下另给 6/8/10 K 三档的孔板孔径与 ΔP。

### 6.7 输出与计算书

每次运行写 `runs/<时间戳>-oned-<dp>/`：`manifest.json`、`inputs.yaml`（参数副本）、`result.json`（全部数字）、`report.md` 与 `report.html`（计算书：公式、代入值、结果、判据、证据等级）、`log.txt`。json 结构与现有 `oned_design` 返回值兼容，设计台和 MCP 直接读取。

### 6.8 回归与验证

| 层次 | 黄金数据 | 容差 |
|---|---|---|
| 单元 | 关联式手算点（Shah & London 表值、Martin 原文例） | 0.1% |
| 回归 A | v2.0 §9 表：孔速、Re、孔口 ΔP、R_conv、R 区间、ΔTf、HBM 速度、压降分段、孔径扫描 5 档、差距闭合 8 行、承压 3 工况、尺寸链 11 项 | 0.5% |
| 回归 B | `cycle-20260926/out/cycle.json` 全部字段 | 0.5% |
| 回归 C | v2.1 与 PG25 工作簿：3.512 L/min、0.897 / 1.402 m/s、2.6 L/min 下 1.022 m/s、0.1096 L/min、0.753 L/min | 0.5% |
| 回归 D | Grace v1.1：0.502 m/s、2.44 kPa、20.5 kPa、22.9 kPa | 1% |
| D-001 自洽 | PC-1…PC-6 流量与温升按能量平衡闭合（§0.2 表） | 0.1% |
| 交叉 | 与 CFD E2 结果对表；与路线 B 稳态对表 | 记录 / < 1% |

注意：DR2 工作簿 `03_DR2_一维性能核算.xlsx` 的公式格没有缓存值，要先用 Excel 或 LibreOffice 重算保存，或在 Python 里按公式重算，才能当黄金数据。

### 6.9 双路线协同

- 分工：路线 A 管稳态一维与网络，是唯一数值源；路线 B 管动态（启停、负载阶跃、失冷）、托盘 / CDU 系统级和控制设计。
- 接口：两路线只通过设计点注册表（json）和 FMU 交换，变量名用 §9.8 的统一变量表。
- 对照：每个 DR2′ 包都附双路线稳态对照表；差异 > 1% 时以路线 A 为准，查路线 B 参数。
- 授权不可用时，路线 B 的动态模型改用 Python ODE 实现，接口不变。

## 7 CAD / CFD / 工程图自动化链路

### 7.1 链路总图

```svg:chain
设计点 yaml（D-001）→ 一维 oned → 规则门 rules.py →［E1 人确认］→ build123d 实体 → STEP + 命名面
→ 网格（ICEM 单胞 / Fluent Meshing 整板）→ 预检（显存 / 许可）→［E2 人确认］→ Fluent journal / PyFluent → 解析入账 → 与 1D 对表 → R1 判定
分支：STEP → Mechanical FEA（承压 / 压装）；STEP → 工程图 DXF/PDF + BOM →［人审 / 对外发图比照 ③］
```

*图 7-1 · CAD → CFD → FEA → 出图自动化链路（html 版为内联 SVG）。方括号是人工确认点。*

### 7.2 几何轨道与内核升级

- 四条轨道继续分开（`knowledge/cad-tracks.json`）：`parametric-v1`、`measured-asm0921`、`grace-concept`、`tray-schematic`。新增第五条 `parametric-v2` 作为 v2 216 孔的参数化轨道，**不覆盖** v1 冻结 yaml。
- v2 内核改动：`jets.pitch` 拆成 `pitch_x`、`pitch_y`（保留 `pitch` 向后兼容）；`rules.REPORT_REFERENCE` 按轨道指向 v1 / v2 数字；HBM 方案参数化（槽数、宽、深、进液方式）；水嘴、UQD、静压箱先做占位特征，ICD 到后替换。
- 每次建模做 STEP 回读核对：包围盒、体积、孔数、孔径（圆柱面取包围盒中点，`environment.md`）。
- 已知坑：OCC 共面布尔会段错误，切除要过切，失败先重试；build123d 放进 Compound 时用 `Pos(0,0,0) * part` 复制。

### 7.3 CFD 前处理

- 流体域：由固体实体布尔反求，或在 SpaceClaim 里 `Volume Extract`。命名面规范：`inlet_*`、`outlet_*`、`wall_heat`、`heat_die_a/b`、`heat_hbm_*`、`interface_*`、`periodic_*`、`sym_*`，清单写 json，网格脚本按名字取面。
- 简化规则遵循 v2.0 §10.3：入口 / 出口延长段 ≥ 10 Dh；允许沿 X 中线取 1/2；不允许 1/4；喷嘴不能当多孔介质；必须共轭。
- 网格路线：单胞与局部带用 ICEM hex（已有黄金 replay，人录、AI 改参）；整板用 Fluent Meshing 水密流程。网格判据见 v2.0 §10.4（驻点首层 ≤ 3 μm、y⁺ < 1 等）。

### 7.4 求解与作业管理

- 控制面：Fluent journal（批处理 `-g -i`）为底线；PyFluent 封装为便利层；GUI 只用于 `fluent-gui-capture` 取报告图。
- 预检：网格量 × 2.2 GB/百万单元与空闲显存比较；CPU 核数与许可核数比较；同机已有 Fluent 进程时不再启动。
- 作业目录：`runs/<时间戳>-cfd-<case>/`，含 journal 副本、transcript、监视量 CSV、`manifest.json`。网格、边界、迭代数必须来自同一次运行（`cfd-loop` 第 1 条）。大文件 `.cas.h5/.dat.h5/.msh` 留在算例目录，不入 git，清单记录路径、大小和 SHA-256。
- 工况矩阵：PC-1…PC-6（D-001）为主，用一个参数表驱动；v2.0 C01–C12 中的热点 2.5×、HBM 堵塞 20%、45 °C、孔径 / 槽深变体（C11、C12）作补充子集；失败自动重试一次，再失败就停下报告。

### 7.5 后处理与结果入账

- 自动提取：Rθ,c-in、ΔP 分段、ΔTf、能量比、质量比、逐孔流量（216 行）及偏差、HBM 近壁最大速度、两 die 中心温差、残差末值。
- 判据自动核：v2.0 §10.8 六条；不满足的标“不可引用”，不写结论句。
- 报告图：走 `fluent-gui-capture`（期刊驱动 GUI、Auto Range、壁面面值、不切在 `z=-2.00 mm` 交界面上）。
- 入账：结果 json 写回算例目录和设计点的 `evidence` 列表，证据等级 E2/E3。

### 7.6 FEA

模板三类：① 3 bar 均布内压（盖板跨射流阵、跨 HBM 区）；② 300–500 N 四角压装 + TIM2 等效弹簧，看接触面平面度；③ 钎焊冷却热应力（可选）。材料用退火 C11000（屈服 70 MPa，E 110 GPa）。结果与 v2.0 §6.3 解析值对表，解析 16.73 MPa 应与 FEA 最大值同一量级。

### 7.7 工程图

- 候选图（AI 自动）：外形三视图、底板流道、A-A/B-B 剖面、射流单元、孔位表、爆炸图、BOM，DXF + PDF，图号沿用 JM01-A0～A6；AutoCAD 2024 审图。
- GD&T 检查表草案（来自 v2.0 §6.5）：平面度 0.05、Ra ≤ 0.8 μm、孔径 ⌀0.50 +0.03/0、喷嘴阵位置度 ⌀0.4 MMC、射流间隙 2.0 ± 0.10。
- 正式图（人定稿）：GD&T 体系、表面处理、焊接符号、检验要求表。AI 提供尺寸表、公差建议和 SolidWorks 宏草稿。
- 图纸检查清单：标题栏、比例、单位、剖切符号、尺寸链闭合、孔数与孔径、公差、材料、版本号；每项自动核或人工勾选。

## 8 试验验证与 V&V

### 8.1 试验层级

| 层级 | 内容 | 来源 |
|---|---|---|
| 出厂检验（100%） | 外形、平面度与粗糙度、氦检 3 bar、流阻、喷嘴通畅 | v2.0 §11.1 |
| 型式试验（首件） | T1 热阻、T2 均温、T3 驻点对位、T4 分区流量、T5 包络、T6 PG25、T7 耐久堵塞、T8 压装影响 | v2.0 §11.2 |
| 系统验收（SAT） | 托盘分流后的实际工作点与壳温 | v2.0 §11.3 |
| 先行验证 | 1:1 铜样 + PMMA 透明流道样 + 双 die / 八 HBM 加热块；PIV 或染色法看 cell/bank 拓扑 | v2.0 §11.3 注 |

### 8.2 TTV 台架

- 加热：两块 25×25 mm 加热块模拟双 die，八块小加热块模拟 HBM；功率分路可调，覆盖 1100~1400 W，独立测量。
- 回路：恒温循环机（40 / 45 °C，PG25 为主，水作回归）、变频泵与旁通阀（支撑 ⑨ 的 HIL）、25 μm 过滤、科氏或电磁流量计、差压变送器（0–50 kPa）。
- 测量：进出口温度（4 线 Pt100，±0.05 K）、差压（±0.1 kPa）、流量（±0.5%）、加热块嵌入热电偶、红外热像（PMMA 样件或去盖测量）。
- 采集：NI cDAQ 或 Keysight DAQ970A 等；路线 A 用 Python `nidaqmx` / `pyvisa`，路线 B 用 MATLAB Data Acquisition。脚本由 AI 写，人审接线与安全。
- 不确定度：按 GUM / ASME PTC 19.1 合成，目标热阻测量扩展不确定度 ≤ ±5%（k = 2）。超过 5% 时，15% 的 V&V 判据就失去分辨力。
- 工况：D-001 角点 PC-1、PC-3、PC-4、PC-6 + 中心点 PC-2，与 CFD 一一对应；重复 ≥ 3 次。
- 安全：硬件联锁（过温断加热、低流量断加热、漏液检测、急停）先于软件；每次通电经 E4。

### 8.3 V&V 层级

| 层级 | 对比对象 | 可接受偏差 | 不达标怎么办 | 现状 |
|---|---|---|---|---|
| V1 代码验证 | 解析解（层流平板、圆管 f·Re） | < 2% | 换求解器或修正设置 | 未做 |
| V2 能量平衡 | 一维 ΔTf | < 2%（硬约束；DR3 判据为 1%） | 查边界与热源加载 | 单胞 1.0015；12 格 1.0368 |
| V3 压降分段 | 一维孔口与槽 | 孔口 < 20%；歧管以 CFD 为准 | 复核 K | 12 格 +27.6%、UC-01b +26.1%（路径不同） |
| V4 文献锚定 | Martin（Re ≈ 3000 有效域内） | < 15% | 先锚定再外推 | 未做 |
| V5 试验确认 | TTV 实测 Rθ,c-in | < 15% | 触发 R2 回路 | 未开始 |

已有一维–CFD 对照的再判读：UC-01b 压降 +26.1% 与 12 格 +27.6% 是路径差（一维只有孔口项），不是模型误差，处理办法是一维网络加槽与回液缝元件；UC-01b 质量加权温升 +0.15%，V2 通过；HBM 七槽温升 +7.96% 时残差未达标，结论受限；HBM 七槽压降 +571% 不可比（含延长段与发展段）。这些都不是 V5，不触发 R2，但它们是 P1 一维网络校准的第一批数据。

### 8.4 ASME V&V 20 框架与偏差 > 15% 回路

- 对比误差 E = S − D（S 仿真值，D 试验值）；验证不确定度 u_val = √(u_num² + u_input² + u_D²)。
- u_num：三套网格，加密比 r ≥ 1.3（v2.0 要求 1 : 1.5 : 2.25），Roache GCI 折算；迭代误差为监测量 500 步漂移 < 0.5%。
- u_input：用一维网络或代理模型做灵敏度系数，再蒙特卡洛传播（TIM2 面积热阻 0.1–0.2 °C·cm²/W、功率分区、流量 ±2%、进液温度 ±0.2 K、孔径公差 +0.03/0、PG25 浓度 ±2%）。
- 判读：偏差绝对值 ≤ 15% 且 E 与 u_val 同量级时，模型可用；偏差 > 15% 触发 R2；u_val > 15% 时结论为“不可判”，先降不确定度。

```svg:vv
模型预测（1D / CFD / 孪生，带版本）→ 试验测量（TTV，带 u_D）→ 偏差 ε 与 u_val →（ε ≤ 15%）V5 通过 → DR4 闸门包
                                                                         └（ε > 15%）开 R2 工单 → 偏差分解（测量 / 装配 / 样件 / 模型）→ 反标定 → 回 ③
```

*图 8-1 · V&V 闭环（html 版为内联 SVG）。*

偏差分解顺序：先排除测量（不确定度、传感器位置、热损失），再排除装配（TIM2 厚度与压力、平面度），再排除样件（孔径一致性、钎料堵塞，用流阻曲线和 X-ray/CT 判断），最后才改模型。模型修正只改有物理意义的参数（h 倍率、TIM2 面积热阻、孔口 K、接触热阻），用最小二乘或贝叶斯反标定，并记录参数的置信区间。修正后模型升小版本号，旧版本保留，并起草 semantic 记忆候选（含适用域与 `valid_until`）。

### 8.5 试验数据格式

每次试验一个目录 `vv/tests/<日期>-<样件号>-<工况>/`：`meta.yaml`（样件号、图纸版本、台架版本、传感器与校准证书号、操作者、D-001 工况 id）、`raw.csv`（时间戳、通道、值、单位）、`steady.csv`（稳态窗口均值与标准差）、`photos/`、`ir/`。`test_import` 校验单位、量程、校准有效期、稳态判据（如 10 min 内温度漂移 < 0.1 K），不过就拒收。通道名与 §9.8 统一变量表一致。

## 9 数字孪生与孪生在环 AI 控制

### 9.1 孪生分级

| 级别 | 内容 | 数据来源 | 用途 | 阶段 |
|---|---|---|---|---|
| L0 静态孪生 | 一维模型 + 设计点（D-001） | model.py / oned | 设计计算 | 已有（水），P1 补 PG25 |
| L1 代理模型 | ROM：R(Q, P, Tin, ΔT, D, TIM2)、ΔP(Q)、Tmax | CFD DOE + 1D 大样本（多保真度） | 快速评估、托盘优化 | P6a |
| L2 动态孪生 | 热 RC 网络 + 水力网络，冷板–托盘–CDU | L1 + 质量热容（铜约 440 g） | 启停、负载阶跃、温升切换、失冷窗口、堵塞 | P6a |
| L3 运行孪生 | 在线标定：进出口温度、流量、ΔP、GPU 遥测（如 DCGM） | 试验台或机柜数据（D3，需脱敏） | 状态估计、堵塞预警、控制 | P6a 后期 |

### 9.2 两条并列路线总览

```svg:routes
共同源：设计点注册表（D-001）+ 一维模型（路线 A Python 为数值源）
路线 A（AI 自研）：Python ROM / RC 网络 → pythonfmu 导出 FMU → Python SIL（FMPy + do-mpc / CasADi；RL 研究项）→ 评估报告
路线 B（MATLAB/Simulink agent，经 ai-matlab 薄加载器）：Simscape Fluids 孪生 → MPC Toolbox / RL Toolbox → Simulink SIL（Simulink Test）→ HIL（Simulink Real-Time）
互通接口：FMU（FMI 2.0/3.0 Co-Simulation）+ 统一变量表；A 的 FMU 可导入 Simulink，B 的孪生可导出 FMU 给 FMPy
出口：DR5 孪生验收 / DR6 控制策略放行；R3 再标定、R4 反哺设计指标
```

*图 9-1 · 数字孪生与孪生在环控制的两条并列路线（html 版为内联 SVG）。一维模型是共同源，FMU 是互通接口。*

### 9.3 路线对比

| 维度 | 路线 A：AI 自研（Python） | 路线 B：MATLAB/Simulink agent |
|---|---|---|
| 承担者 | `cp-design` | `ai-matlab`（经 `.claude/agents/ai-matlab.md` 薄加载器，`user-matlab` MCP） |
| 一维 | `oned_pkg` 稳态 + 网络（唯一数值源） | Simscape Fluids 稳态 / 瞬态对照与托盘系统级 |
| 孪生建模 | GP / 响应面 ROM + 3–5 节点 RC 网络（scipy ODE），pythonfmu 导出 FMU | Simscape Fluids（Thermal Liquid）物理网络，泵阀管路库齐全；Simulink Compiler 导出 FMU |
| 控制设计 | do-mpc / CasADi MPC；RL 用 gymnasium + Stable-Baselines3（研究项） | MPC Toolbox（显式约束、自适应）；RL Toolbox（安全屏蔽）；Simulink Control Design |
| 验证梯度 | MIL / SIL（Python 内联仿真，FMPy 联仿）；HIL 需自写实时层，较弱 | MIL → SIL（Simulink Test 场景库、Simulink Coder）→ HIL（Simulink Real-Time / Desktop Real-Time） |
| 与 CFD / ROM 衔接 | 直接读 CFD DOE CSV，与一维同语言 | 经 FMU 或查表嵌入路线 A 的 ROM |
| 可审计 / diff | 纯文本，git diff 友好，AI 易读易改 | slx 二进制难 diff，需同时导出参数 json 与结果 CSV |
| AI 可编程性 | 高（与平台主体同语言） | 中高（MATLAB 脚本可生成模型，`ai-matlab` 有现成能力） |
| 许可与安装 | 免许可；需装 FMPy、pythonfmu、CasADi（比照①） | MATLAB R2025b 已装，特性在许可文件中，检出待验证（Q-08） |
| 本机已有资产 | `oned.py`、`zones.py`、`model.py`、scikit-learn | `ai-matlab` 智能体、`user-matlab` MCP 已登记；无现成模型 |
| 主要风险 | 系统级泵阀库要自写；HIL 实时性弱 | 许可依赖；模型与 Python 数值漂移；slx 版本管理 |
| 适合 | 冷板级孪生、ROM、快速 SIL、批量 DOE、R3 标定 | 托盘 / CDU 系统孪生、控制器工程化、HIL、对外交付 Simulink 模型 |

### 9.4 推荐与用户决策项

**推荐（置信度 0.7）：A 主 B 并行的双轨。**

- 一维与 ROM 以路线 A 为唯一数值源，因为它免许可、可 diff，且与平台同语言。
- 托盘 / CDU 系统孪生、控制器工程化和 HIL 以路线 B 为主，因为泵阀库、MPC/RL 工具箱、Simulink Test 与 Real-Time 都已安装，许可特性也在文件中。
- 两路线用 FMU 互导，在 DR5、DR6 上对表。
- 若 S01 验证 MATLAB 许可不可检出，退化为路线 A 单轨：HIL 降级为台架慢速闭环，或推迟。

**选哪条列为用户决策 Q-07**，选项：

1. 双轨（推荐）；
2. 只走路线 A；
3. 只走路线 B（一维数值源仍是 Python）。

S38 在 P1 做两路线 PoC（一维 → FMU → Simulink 导入、Simscape 单板稳态对照），为 Q-07 提供证据。在 PoC 和 Q-07 之前，S27–S30、S40 的步骤卡按两条路线都写交付物，决策后裁剪。

### 9.5 数字孪生模型（两路线交付物）

| 交付物 | 路线 A | 路线 B | 共同判据 |
|---|---|---|---|
| ROM（S27） | `AP/twin/rom/`：GP / 响应面，R(Q,P,Tin,ΔT,D,TIM2)、ΔP(Q)、Tmax；pickle + FMU | 可选：Simulink 内查表或导入 A 的 ROM FMU；有许可时 TwinAI / Fluent ROM 对比 | 留一误差 < 5%；越域警告并回退一维 |
| 动态孪生（S28） | `AP/twin/dynamic/`：RC 网络 + 水力网络，scipy ODE，pythonfmu FMU | `AP/twin/simscape/tray_twin.slx` + 参数 json + 结果 CSV；Simulink Compiler FMU | 稳态与 S06/S08 一致 < 1%；能量守恒；两路线稳态差 < 2% |
| 在线标定与回放（S30，R3） | `AP/twin/calib/`：卡尔曼 / 滑窗最小二乘，Python | Simulink Design Optimization 参数估计（可选） | 回放出水温度误差 < 0.5 K；堵塞预警在合成数据上有效 |
| DR5 验收包 | 孪生 V&V 报告（对 1D、CFD、试验） | 同左，附 Simulink 对照 | AC-9 |

### 9.6 孪生在环 AI 控制（两路线交付物）

| 交付物 | 路线 A | 路线 B | 共同判据 |
|---|---|---|---|
| 控制需求（S29） | `AP/twin/control/requirements.yaml`：被控量、约束、场景（两路线共用） | 同一文件 | 用户确认 |
| PID 基线（S29） | Python PID（FMU 联仿） | Simulink PID（Control System Toolbox） | 零约束违约 |
| MPC（S29） | do-mpc / CasADi，预测模型用 ROM / RC | MPC Toolbox，预测模型用 Simscape 线性化或 ROM | 泵功、超调、违约次数相对 PID 有量化对比 |
| RL（研究项，S29） | gymnasium + SB3，只在孪生上训练，安全屏蔽（约束投影 / MPC 安全滤波） | RL Toolbox，同样只在孪生上训练 | 零违约；不作首选 |
| SIL（S29） | Python 场景库回归 | Simulink Test 场景库、Simulink Coder 生成代码 | 与 MIL 一致 |
| HIL（S40） | 台架慢速闭环（降级方案） | Simulink Real-Time / Desktop Real-Time + 台架泵阀（Modbus / OPC UA） | 硬件联锁有效；每次下发经 E4 |
| R4 反哺（S29、S40） | 设计指标修订建议（两路线共用格式） | 同左 | 经人确认后写注册表 |

### 9.7 控制用例与调节范围（D-001）

| 用例 | 被控量 / 约束 | 控制量 | 控制器 | 验收 |
|---|---|---|---|---|
| C-1 负载阶跃与斜坡（1100 ↔ 1400 W） | Tcase / Tj 超调、恢复时间；ΔP ≤ 20 kPa | 泵速 / 阀开度（模组流量约 1.7~3.5 L/min） | PID 对照、MPC | 超调与能耗相对 PID 改善 |
| C-2 温升设定值调度（6~10 K） | 冷却液温升跟踪误差 ≤ 0.5 K；Tj ≤ 上限 | 流量设定 | MPC | 同 Tj 下温升尽量高（省泵功） |
| C-3 进液温度优化（40 → 45 °C） | Tj 包络 | Tin 设定、流量 | MPC | 暖水节能且不违约 |
| C-4 堵塞检测与降级（对应专利方案 B 的压差阈值思路） | ΔP 漂移、Tcase 上升 | 告警、流量补偿、反洗建议 | 规则 + 估计器 + RL 研究 | 漏报率 / 误报率 |
| C-5 托盘四板并联均流（需 ICD） | 各板流量偏差 ≤ 10% | 孔板 / 阀 | MPC | 偏差与压降 |
| C-6 失冷窗口评估 | 断流后温升速率 | 无（开环评估） | 孪生开环 | 给出区间，不作保证（v2.0 §6.7） |

### 9.8 FMU 与统一变量表

从 P1 起统一变量命名与单位（SI，温度同时给 K 与 °C，流量 kg/s 与 L/min 并列），FMU 端口、Simscape 模型、DAQ 通道名和一维网络都用同一套名称，对照表放 `knowledge/`（S38 起草）：

| 类别 | 变量 |
|---|---|
| 输入 | `P_die_W[2]`、`P_hbm_W[8]`、`P_other_W`、`Q_lpm`、`T_in_C`、`fluid`（PG25 / water）、`pump_speed`、`valve_pos[j]`、`clog_frac` |
| 设定值 | `dT_set_K`（6~10）、`T_in_set_C` |
| 状态 / 输出 | `T_case_die_C[2]`、`T_hbm_max_C`、`T_out_C`、`dP_kPa`、`V_jet_max`、`V_hbm_max`、`m_dot_branch[k]`、`R_c_in`、`W_pump` |
| 参数（可标定） | `D_jet_mm`、`R_tim2_area`、`K_orifice`、`Nu_scale_gpu`、`Nu_scale_hbm`、`K_branch[k]` |
| 规范 | FMI 2.0 Co-Simulation 优先（3.0 视工具支持），步长 0.1–1 s；带版本号与标定数据集 id |

### 9.9 安全边界

```svg:twin
实体对象（试验台 / 托盘 / CDU）→ 传感器（T / P / Q / 红外）→ 状态估计与标定（R3）→ 数字孪生（A：Python ROM FMU / B：Simscape）
控制器（A：Python MPC/RL / B：MPC/RL Toolbox）→ 安全屏蔽（硬限值、速率限制、看门狗、回退 PID）+ E4 / ③ → 执行器（仿真执行器默认；真实执行器需人工确认）
阶段：MIL → SIL → HIL；调节范围：温升 6~10 K，负载 1100~1400 W
```

*图 9-2 · 孪生在环控制的安全架构（html 版为内联 SVG）。*

规则：AI 控制器默认**只驱动仿真执行器**。任何向真实泵、阀、CDU 下发设定值的动作，以及试验台通电加热，都比照平台第③道闸门并经 E4 由人确认，这一映射需要用户批准（Q-06）。硬件联锁（过温、低流量、漏液）先于软件；RL 动作必须经约束投影或 MPC 安全滤波；孪生越训练包络时控制器回退 PID。

### 9.10 孪生 V&V

| 对比 | 判据 |
|---|---|
| L1/L2 对 L0（稳态） | 温升与压降 < 2% |
| L1/L2 对单胞与整板 CFD | 留出验证集 ≤ 5% |
| 孪生对试验 | Rθ ≤ 15%（与 V5 一致），目标 ≤ 10%；瞬态时间常数 ≤ 20% |
| 路线 A 对路线 B | 同一稳态点 < 2%；同一阶跃响应时间常数 < 10% |
| 控制器 | 场景库全部通过约束；与 PID 对照给出改善量 |

## 10 数据与知识管理

### 10.1 数据分级与存放

| 级别 | 例子 | 存放 | 能否给云端模型看 |
|---|---|---|---|
| D1 公开 | NVIDIA/Lenovo 公开规格、论文、专利 | git + Dify | 可以 |
| D2 内部设计 | 设计点、几何参数、计算书、报告 | git | 可以（项目默认），由用户确认 |
| D3 敏感 | OEM 封装图、功率图、订单 ICD、供应商报价、运行遥测 | 本机或内网，不入公开仓库 | 只给脱敏摘要；触发 `on_sensitive_data` 降级路由 |
| D4 大文件 | cas/dat/msh、原始试验数据、红外视频、slx 大模型 | 算例目录或 NAS，不入 git | 只给提取后的 CSV/json |

远程仓库 `origin/main` 是公开还是私有要由用户确认；D2 能否推送取决于它。`AP/` 目前未纳入 git 跟踪，首次纳入的范围也由用户决定（Q-05）。

### 10.2 单一数据源与版本

- 设计点、物性、关联式、几何参数：yaml/py 是唯一源；xlsx 是视图，由脚本生成或只读对照。
- 报告：由脚本生成，页脚写数值源与版本；旧报告不删，加“已取代”标签（如 CFD-AI 评估 v1.0、`calc_1d_out.txt`）。
- 命名：`<名称>_v<主>.<次>_<YYYYMMDD>.<ext>`，与现有报告一致；设计点、几何轨道、技能、记忆的 id 用英文短横线。
- 发布：关键步骤后按 `git-release` 生成提交信息，真实 commit 与 push 由人执行。

### 10.3 run 目录与 manifest

```text
runs/<YYYYMMDD-HHMMSS>-<步骤>-<简称>/
  manifest.json   # id、stage/gate、design_point（D-001 id）、track、parents、inputs+sha256、tool+版本+命令、evidence(E0–E5)、status、metrics、confirm 记录、notes
  inputs/         # 参数副本（冻结件只拷贝）
  outputs/        # STEP / DXF / PNG / CSV / FMU（大文件只记路径与哈希）
  logs/
  report.md|html
  candidates/     # 本步产生的 skill / memory 候选草稿（只列不入库）
```

`runs/` 已在 `.gitignore` 中整体忽略。需要长期保存的结论性结果，经用户确认后把摘要与小文件提升到 `knowledge/` 或报告。

### 10.4 skills 沉淀机制

```svg:govern
步骤产出 → 用户验证（通过 / 修改）→ 候选登记 candidate → 人工闸门（① 技能 / ② 记忆）→ 入库（semantic / skill）→ 继承筛选（≥0.6 未过期）→ GC 标记 expired
                    └ 不通过 → 只留 episodic 或丢弃
```

*图 10-1 · 技能与记忆沉淀流程（html 版为内联 SVG）。*

1. 每完成一个实施步骤，在实施计划的沉淀台账登记候选技能（名称、触发场景、步骤、已验证的命令、坑）。
2. 只沉淀经验证或经用户认可的条目。同一类操作成功两次以上才写技能草稿：共享技能放 `platform/shared/skills/_staging/<name>/SKILL.md`，私有技能先放 `runs/<ts>/candidates/`。
3. 人工确认（第①道闸门）后：私有技能落 `AP/skills/<name>/SKILL.md`；共享技能落 `platform/shared/skills/<name>/` 并登记 `_meta/skill-registry.json`（`went_through_staging: true`、`human_approved: true`）。
4. 技能 frontmatter：`name`、`description`、`version`、`status: staging | active`、`scope: private | platform`、`verified_by`（哪次步骤、哪天由用户认可）。
5. 报错与修正要回写到技能（`fluent-gui-capture` 的做法），同一个坑不踩两次。

### 10.5 memories 沉淀机制

- episodic：每个步骤一条 `memory/episodic/<日期>-<任务>.json`，字段沿用现有格式（`date`、`task`、`confidence`、`valid_until`、`last_verified`、`expired`、`done`、`open`）。
- semantic：只有锁定口径变化时才写或更新。frontmatter 必须含 `confidence / valid_until / last_verified / expired`，并加 `evidence`（E0–E5）、`source`、`status: candidate → active`。
- 置信度：E1 0.6–0.75；E2 0.7–0.8；E3 0.8–0.85；E4 ≥ 0.9；含假设或占位尺寸的 ≤ 0.6；用户认可的流程类 0.85。
- 有效期：CFD 与试验结论 3 个月，或到下一次网格 / 几何变更为止；设计锁定 6 个月；环境与工具 6 个月或到软件升级为止；ICD 到达即过期的写 ICD 预计日期。
- 继承（第②道闸门）：只采纳 `confidence ≥ 0.6`、未过期、近期复核过的祖先记忆；`memory/index.json` 的 `inherit_from` 每次继承前核对。中文损坏的文件只取数字，不整篇继承。
- 过期：不物理删除，由 `platform/hooks/memory_gc.py` 打 `expired` 标记。
- 回灌：高价值 semantic（如“Re < 2000 不用 Martin”“GPU 显存线”）经人确认后回灌 Dify 蒸馏记忆库。

### 10.6 候选 skills 清单（全部 candidate，未创建）

| 编号 | 名称 | 作用 | 来源阶段 / 步骤 | 建议范围 | 三版来源 | 状态 |
|---|---|---|---|---|---|---|
| K-01 | `design-point-registry` | 设计点注册、D-001 工况矩阵派生、口径冲突检查 | P0 · S02 | 私有 | B；C `design-basis` | candidate |
| K-02 | `input-trace` | ICD / 规格抽取、追溯矩阵与假设登记册维护、影响分析 | P0–P1 · S02、S37 | 私有 | A、B；C `requirements-trace` | candidate |
| K-03 | `env-probe` | 只读环境与许可探测（不检出） | P0 · S01 | 可升共享 | A | candidate |
| K-04 | `tradeoff-matrix` | 权衡矩阵、权重敏感性、FTO 对照草稿 | P1 · S37 | 私有 | B、C | candidate |
| K-05 | `oned-calc` | 一维计算书、回归、CLI（路线 A） | P1 · S04–S06 | 私有 | A；B `oned-network`；C `oned-sweep` | candidate |
| K-06 | `oned-uq` | DOE、敏感性、蒙特卡洛（D-001 全包络） | P1 · S07 | 可升共享 | B | candidate |
| K-07 | `hydro-network` | 托盘配平、孔板选型 | P1 · S08 | 私有 | A | candidate |
| K-08 | `simscape-tray` | 路线 B：托盘 / CDU Simscape 模型搭建与对照（与 ai-matlab 协作） | P1 · S09、S38；P6a · S28 | 私有 | B | candidate |
| K-09 | `cad-v2-kernel` | 各向异性节距、HBM 方案、接口特征（并入 `cad-loop` 升版） | P2 · S10–S12 | 私有 | A、B、C | candidate |
| K-10 | `fluid-extract` | 流体域抽取与命名选择 | P2 · S11 | 私有 | A；B `fluid-domain`；C `mesh-loop` 前半 | candidate |
| K-11 | `cfd-batch` | journal / PyFluent 生成、提交、监控、显存门、入账（扩 `cfd-loop`） | P3 · S14、S15 | 私有 | A、B；C `cfd-matrix` | candidate |
| K-12 | `cfd-vv-anchor` | V1 代码验证与 V4 Martin 锚定 | P3 · S16 | 私有 | A | candidate |
| K-13 | `mesh-independence` | 三套网格 GCI 与迭代误差 | P3 · S17 | 可升共享 | A；B `mesh-gci` | candidate |
| K-14 | `cfd-reconcile` | 一维–CFD 契合性报告（契合 / 限制 / 不可比） | P3 · S15、S19 | 私有 | B | candidate |
| K-15 | `r1-loop` | R1 回路：AI 自动参数扫描 / 优化编排 | P3 · S39 | 私有 | B；C 回路 1 | candidate |
| K-16 | `fea-loop` | 承压、压装、热变形工况与判据 | P4 · S20 | 私有 | A、C；B `fea-press` | candidate |
| K-17 | `tolerance-stack` | 名义 + 统计尺寸链、蒙特卡洛公差 | P4 · S21 | 私有 | A | candidate |
| K-18 | `drawing-loop` | DXF 出图、GD&T 检查表、BOM、检验表 | P4 · S22 | 私有 | A、C；B `drawing-gdt` | candidate |
| K-19 | `ttv-test` | 试验大纲、DOE、DAQ 采集、数据清洗 | P5 · S23、S24 | 私有 | A；B `test-doe`/`daq-ingest`；C `test-plan` | candidate |
| K-20 | `vv-loop` | V&V 20 对比、R2 判读、反标定 | P5 · S25 | 可升共享 | A、C；B `vv20` | candidate |
| K-21 | `twin-rom` | ROM、FMU 打包、R3 在线标定（路线 A） | P6a · S27、S28、S30 | 私有 | A；B `rom-fmu`；C `rom-twin` | candidate |
| K-22 | `control-sim` | 场景库、安全屏蔽、MPC / RL 流程，A/B 两段 | P6b · S29、S40 | 私有 | A；B `ctrl-mil`；C `ail-control` | candidate |
| K-23 | `gate-review` | DR0–DR6 闸门包模板、判据、未关闭项 | 每个 DR | 私有 | C | candidate |
| K-24 | `artifact-manifest` | run manifest 字段与追溯 | P0 · S36 | 可升共享 | C | candidate |
| K-25 | `html-report-toc` | md + html 双格式、左侧折叠目录、内联 SVG 报告生成（以本目录 `build_plan.py` 为原型） | 本规划 | 可升共享 | B | candidate |

### 10.7 候选 memories 清单（全部 candidate，未写入）

| 编号 | 主题 | 内容要点 | 证据 | 建议置信度 | 状态 |
|---|---|---|---|---|---|
| M-01 | `design-points` | D-001 工况口径（PG25、1400 W 基线、6~10 K、1100 W 校核、水仅回归）与选用规则 | 用户决策 | 0.9 | candidate（待用户确认写入） |
| M-02 | `pg25-properties` | 两套 PG25 物性来源、差异（μ +37%）、正式选用 | E1 | 0.8 | candidate（待 Q-01） |
| M-03 | `oned-regression` | 黄金数据来源与容差 | E1 | 0.8 | candidate（S04 后） |
| M-04 | `tool-license-inventory` | MATLAB R2025b 已装、许可特性清单；Ansys v261 模块；Python 包；检出验证结果 | 实测 | 0.9 | candidate（S01 后） |
| M-05 | `hbm-current-scheme` | HBM 当前截面与流路（Q-03 后） | E1 / E2 | 0.7 | candidate |
| M-06 | `oned-cfd-offsets` | 一维–CFD 系统偏差：UC-01b 压降 +26.1%、12 格 +27.6%（路径差），温升闭合 1.0015 | E2 | 0.75 | candidate |
| M-07 | `compute-thresholds` | 网格规模与本机 / HPC 阈值（2.2 GB / 百万单元等，已在 `cfd-loop`） | 手册 + 实测 | 0.85 | candidate |
| M-08 | `vv-thresholds` | 15% 闸门、u_val 可判性规则、GCI 判据 | 标准 + 用户认可 | 0.85 | candidate |
| M-09 | `levers` | D-001 下的杠杆排序（S07） | E1 | 0.7 | candidate（未产生） |
| M-10 | `tray-hydraulics` | PG25 托盘配平与孔板（结论待 ICD） | E1 | ≤ 0.6 | candidate（未产生） |
| M-11 | `cfd-v4-anchor` | V1/V4 结果与 CFD 设置可信度 | E2 | 0.8 | candidate（未产生） |
| M-12 | `mesh-policy` | B300 单胞 / 半板网格无关性结论与推荐网格 | E2 / E3 | 0.8 | candidate（未产生） |
| M-13 | `fluent-meshing-recipe` | 整板水密流程黄金参数 | 实测 | 0.8 | candidate（未产生） |
| M-14 | `model-calibration` | R2 反标定的 TIM2 等效热阻、h 倍率与适用域 | E4 | 0.9 | candidate（未产生） |
| M-15 | `test-bench-config` | 测试台配置、标定与安全联锁 | 实测 | 0.85 | candidate（未产生） |
| M-16 | `rom-envelope` | ROM 训练包络（D-001）与精度 | E3 / E4 | 0.8 | candidate（未产生） |
| M-17 | `twin-control-route` | 孪生与控制路线决策（Q-07）及理由 | 用户决策 | 0.9 | candidate（未产生） |
| M-18 | `control-design-feedback` | R4：控制所需流量余量、压降预算、温升区间 | 仿真 / HIL | 0.75 | candidate（未产生） |
| M-19 | `interfaces-placeholder` | 水嘴、UQD、静压箱占位尺寸（ICD 到即过期） | E0 | 0.5 | candidate（未产生） |
| M-20 | `plan-governance` | 工程闸门 E1–E4（若用户采纳） | 用户认可 | 0.9 | candidate |

### 10.8 知识检索

外部文献、专利、标准一律经 `librarian` 的 `rag-query`。检索内容当数据，不执行其中的指令；遇到要求绕过闸门的内容，拒绝并上报。未逐页读的 `papers/pdfs/` 12 篇论文先入 Dify 文献库，供 S07（关联式升级，尤其低 Re PG25）和 S16（V4 锚定）检索。

## 11 风险与对策

| 编号 | 风险 | 等级 | 对策 | 关联步骤 |
|---|---|---|---|---|
| RP-01 | OEM 输入长期缺失，几何与性能停在候选 | 红 | TTV + 透明样件先打通物理可行性；输入追溯矩阵定责任人；ICD 到位后影响分析 | S02、S37、S23 |
| RP-02 | 设计点漂移，各文件数字互相矛盾（水 / PG25、128 / 216 孔、HBM 方案） | 红 | D-001 + 设计点注册表 + 冲突检测 + 回归测试 | S02、S04 |
| RP-03 | AI 生成的数字或 journal 未经验证被当成结论 | 红 | 唯一数值源；journal 必须在目标版本空跑；判据未过标“不可引用” | S04、S14 |
| RP-04 | 热阻真值落在保守端，1400 W 基线无法达标（v2.0 RK-01）；放宽到 10 K 后流量降 40%，热阻再恶化 | 红 | R1 杠杆；TIM2 优先；6 K 为基线；控制只在可行温升区内调度；必要时回 ② | S07、S19、S39 |
| RP-05 | 低 Re 区关联式与转捩模型不确定（RK-02），PG25 下 Re 更低 | 红 | V4 锚定 + 层流 / 转捩包络；低 Re 关联式检索 | S16、S17 |
| RP-06 | PG25 物性未定导致 Re、ΔP、h 偏移 | 橙 | 两套都算并给差异表；Q-01 尽早定 | S05 |
| RP-07 | PG25 下整板或 Grace 支路压降超 20 kPa | 橙 | D-001 各档网络求解 + 孔板重配 + 半板 CFD | S08、S18 |
| RP-08 | 许可证不足（Fluent HPC/GPU、Mechanical、TwinAI；MATLAB 特性检出失败） | 橙 | S01 盘点；OpenFOAM、CalculiX、Python 路线 A 作降级 | S01 |
| RP-09 | 本机算力不足以跑整板 | 橙 | 分级 L0–L4；1/2 对称；HPC 或云（受保密约束，E2 / ③） | S18 |
| RP-10 | GPU 求解占满显存卡死桌面 | 橙 | `cfd_preflight` 硬检查 | S14 |
| RP-11 | 数据外泄（OEM 资料进入云模型或公开仓库） | 红 | 数据分级；D3 只给脱敏摘要；确认仓库可见性 | S01、§10.1 |
| RP-12 | PyAnsys 版本与 Fluent 2026 R1 不匹配；GUI 自动化脆 | 黄 | journal 作底线，PyFluent 版本锁定，失败回退 | S14 |
| RP-13 | OCC 段错误导致 CAD 批处理不稳定 | 黄 | 过切、重试、子进程隔离 | S10 |
| RP-14 | 覆盖冻结 yaml 或已发 STEP | 橙 | 规则门拒写；产物只进 `runs/`；E1 | 全程 |
| RP-15 | 试验不确定度过大，15% 判据失去意义 | 橙 | 不确定度预算 ≤ 5%；传感器校准 | S23 |
| RP-16 | 样件外协交期与春节（2027-02-06 前后）冲突 | 橙 | W16 前发询价，节后下单；交期留 2 周缓冲 | S22、S23 |
| RP-17 | 测试台安全（1400 W 加热、PG25 泄漏、电气） | 红 | 硬件联锁、漏液检测、E4、安全检查表 | S23、S26、S40 |
| RP-18 | 孪生外推出训练包络，控制器依赖错误预测 | 橙 | 包络检测 + 不确定度输出；超包络回退 PID；R3 标定 | S27、S30 |
| RP-19 | 动态孪生或 AI 控制误下发到真实设备；RL 出现不安全动作 | 红 | 默认只驱动仿真；安全屏蔽；HIL 每次经 E4 | S29、S40 |
| RP-20 | 双路线数值漂移、维护成本翻倍 | 黄 | 一维唯一数值源在路线 A；FMU 互导与稳态对表；Q-07 后可裁剪 | S38、S28 |
| RP-21 | 喷嘴堵塞、钎料溢流 | 橙 | 过滤 ≤ 25 μm；钎料空心框；CT 抽检；孪生堵塞场景 C-4 | S23、S29 |
| RP-22 | FTO 风险（Intel DLMJ、WO2026103052A1 等） | 橙 | 外部专业检索；AI 只做对照草稿 | S37、外部 |
| RP-23 | 技能与记忆膨胀、过期或损坏内容被继承 | 黄 | 台账 + 闸门 + memory_gc；S35 体检 | S32、S35 |
| RP-24 | 平台功能膨胀拖慢设计主线；用户可投入时间不足 | 黄 | 每个阶段以闸门交付物为准；UI 改动排在工具之后；步骤颗粒度小 | 全程 |

## 12 里程碑与甘特

```svg:gantt
P0|P0 准备与基线|1|2|phase
P0|S01–S03 · S34–S36 环境 / 注册表 / 决策 / 收口|1|2|task
M0|M0 规划评审 · D-001 落盘|1|0|milestone
P1|P1 一维（双路线）|2|6|phase
P1|S04–S06 回归 · PG25 复算 · 计算书|2|3|task
P1|S07–S08 6~10 K 扫描 · 水力网络|4|3|task
P1|S37 DR0/DR1 复核 · S38 双路线 PoC|5|3|task
P1|S09 DR2′ 复审包|7|1|task
M1|DR2′ 一维再基线（PG25）|7|0|milestone
P2|P2 CAD v2|5|6|phase
P2|S10 内核 v2 · S12 接口占位|5|4|task
P2|S11 流体域 · S13 Grace|8|3|task
M2|DR1′ 几何再选定|10|0|milestone
P3|P3 三维 CFD|8|13|phase
P3|S14–S15 作业骨架 · 结果入账|8|2|task
P3|S16–S17 V1/V4 · GCI · 孔径对比|10|4|task
P3|S18 单 die / 半板（HPC）|12|5|task
P3|S19 PG25 6 工况矩阵 · S39 R1 自动化|16|5|task
M3|DR3 仿真通过|20|0|milestone
P4|P4 机械与图纸|15|8|phase
P4|S20 FEA · S21 公差|15|4|task
P4|S22 候选图纸包 · 询价草案|18|5|task
M4|DR3 闸门|22|0|milestone
P5|P5 样件与试验|19|14|phase
P5|S23 大纲与台架（采购走 ③）|19|8|task
P5|样件外协（春节后下单）|21|6|task
P5|S24–S25 数据导入 · V&V 20 · R2|25|7|task
P5|S26 首件试验与放行包|28|5|task
M5|DR4 送样放行|32|0|milestone
P6a|P6a 数字孪生（A/B 双路线）|24|11|phase
P6a|S27 ROM · S28 动态孪生 + FMU|24|7|task
P6a|S30 在线标定 · 回放（R3）|30|5|task
M6|DR5 孪生验收|34|0|milestone
P6b|P6b 孪生在环 AI 控制（A/B）|30|11|phase
P6b|S29 PID / MPC / RL SIL（6~10 K）|30|7|task
P6b|S40 HIL 联调（E4 / ③）|36|5|task
M7|DR6 控制策略放行|40|0|milestone
P7|P7 平台化（持续）|1|40|phase
P7|S31 MCP / 设计台 · S32 入库 · S33 发布|34|7|task
```

*图 12-1 · 里程碑甘特图（html 版为内联 SVG；W1 = 2026-10-05 周一，W40 结束于 2027-07-11）。条形为阶段，浅色为子任务，菱形为门控，红色虚线为春节。*

| 里程碑 | 周次 / 日期 | 交付物 | 闸门 | 对应实施步骤 |
|---|---|---|---|---|
| M0 规划评审 | W1 · 2026-10-11 | 本规划与实施计划评审意见；D-001 写入注册表；§13 决策记录 | 用户确认 | S01–S03、S34–S36 |
| M1 一维再基线 | W7 · 2026-11-22 | 设计点注册表、一维工具、回归报告、D-001 扫描、水力网络、双路线 PoC、DR2′ 复审包 | DR2′ | S04–S09、S37、S38 |
| M2 几何再选定 | W10 · 2026-12-13 | `parametric-v2` 内核、216 孔整板与流体域、接口占位、Grace 接入规则门 | DR1′ + E1 | S10–S13 |
| M3 仿真通过 | W20 · 2027-02-21 | 作业工具、V1/V4、GCI、半板、PG25 6 工况矩阵、R1 自动化、DR3 仿真包 | DR3 仿真通过 | S14–S19、S39 |
| M4 图纸闸门 | W22 · 2027-03-07 | FEA 报告、公差、候选图纸包、询价草案 | DR3 闸门 | S20–S22 |
| M5 送样放行 | W32 · 2027-05-16 | 试验大纲、台架、首件数据、V&V 报告 | DR4 | S23–S26 |
| M6 孪生验收 | W34 · 2027-05-30 | ROM、动态孪生（A/B）、FMU、在线标定 | DR5 | S27、S28、S30 |
| M7 控制放行与平台 v1.0 | W40 · 2027-07-11 | SIL / HIL 报告、R4 建议、MCP 工具扩展、技能与记忆入库、拆分评审 | DR6 + ①② | S29、S40、S31–S33 |

## 13 开放问题与需用户决策（按优先级）

### 13.1 已决策

| 编号 | 决策 | 日期 | 影响 |
|---|---|---|---|
| D-001 | 设计工况：PG25；1400 W 为设计基线；冷却液温升 6~10 K 可调；1100 W 为校核工况；水口径仅作回归对照（§0.2） | 2026-10-02（用户拍板） | 全部阶段；取代三版 v1.0 的“主设计点选哪套”（A Q1、B D-01、C Q-01） |

### 13.2 开放问题

优先级：P0 阻塞第一批（P0–P1 前段）；P1 阻塞 P1–P3；P2 阻塞 P4 以后；P3 不阻塞主线。

| 编号 | 优先级 | 问题 | 选项 / 建议 | 阻塞步骤 | 三版来源 |
|---|---|---|---|---|---|
| Q-01 | P0 | PG25 正式物性 | `model.py` PG25_40 / DOWFROST LC 25 / 供应商实测表；建议用实际采购工质的供应商表，两套现值都入库并标来源 | S05、S07、S08 的正式数字（S04 不阻塞） | A Q2 |
| Q-02 | P0 | D-001 下的放行判据：1400 W 基线 Rθ 目标（沿用 DP-B < 0.025 或按 Tj 倒推）、1100 W 校核目标（< 0.028）、20 kPa 是否计入 UQD、Tj 上限 | 建议 1400 W 按 Tj 倒推并给门槛 / 目标两档；UQD 单列 | S07、S09、S19、S26、S29 | 新增（由 D-001 引出；C Q-01 的 KPI 部分） |
| Q-03 | P0 | HBM 当前截面与流路 | v2.1 中心进液 7×0.80×2.00 / 方案 D 11×0.45×2.00 + 静压仓；建议读 S34 日志后确认 D | S02（`current`）、S10、S12、S18 | A Q3、B D-08、C |
| Q-04 | P0 | GPU 孔径（D0.50 / D0.40）与 ⑤ 三维仿真工具链选定（Fluent 主 + OpenFOAM 交叉？）及 Ansys 许可范围（Fluent 求解器 / HPC / GPU、Meshing、Mechanical、SpaceClaim、optiSLang、TwinAI） | 孔径由 S17 两孔径对比后定；工具推荐 Fluent 主；许可由 S01 盘点 | S10 终版、S14、S16–S20、S27 | A Q3/Q6、B D-02/D-09、C Q-04 |
| Q-05 | P0 | 数据保密与仓库可见性；`AP/` 纳入 git 跟踪的范围 | `origin` 公开或私有；D3 不出本机；确认私有后再推送 D2 | 首次提交；S01 结论 | A Q7 |
| Q-06 | P0 | 工程闸门 E1–E4 是否采纳；外协、采购、对外发图、实物上电、HIL 下发是否比照③ | 建议先在模块内试行，比照③，AI 只到草案 | S10 起的写入步骤；S18、S22–S26、S40 | A Q8、B D-15 |
| Q-07 | P1 | 孪生与控制路线：双轨 / 只 A / 只 B | 推荐双轨（A 主 B 并行，§9.4）；S38 PoC 后定 | S27–S30、S40 的交付物裁剪 | 新增（用户要求） |
| Q-08 | P1 | MATLAB 许可实测：允许 S01 用 `license('test', …)` / `ver` 做一次检出验证吗？ | 文件含 SimHydraulics、MPC、RL、Simulink Test/Coder/Compiler、Real-Time 特性；检出会占用许可 | S09 对照、S38、路线 B 全部 | A Q4、B D-03、C Q-03 |
| Q-09 | P1 | 第三方 Python 包安装授权与 venv 位置（PyFluent、PyMAPDL、FMPy、pythonfmu、CasADi / do-mpc、optuna、openpyxl 进 `cad/.venv` 或新建 `cae/.venv`） | 建议新建 `cae/.venv`，不动系统 Python；逐包确认 | S14、S20、S27、S38；S04 可用默认 python 读 xlsx | B D-04、C Q-06 |
| Q-10 | P1 | 整板 CFD 的 HPC / 云算力预算与渠道（保密约束下） | W10 前定 | S18、S19（关键路径） | A Q9、B D-05 |
| Q-11 | P1 | 授权内核升 v2（`pitch_x/pitch_y`）并给冻结 yaml 升版 | 建议授权，旧版保留 | S10 | B D-10 |
| Q-12 | P2 | 正式工程图用哪种 CAD | 公司标准 CAD 定稿；首期 DXF + AutoCAD 2024 | S22 | A Q5、B D-06、C Q-05 |
| Q-13 | P2 | 试验资源：自建台 / 外协；预算上限；PG25 能否上台；是否同时做 PMMA 透明样 | 建议自建（可支撑 HIL）+ 透明样 | S23、S26、S40 | A Q10、B D-11/D-12、C Q-07 |
| Q-14 | P1 | OEM 封装图、power map、单板流量窗、UQD、压装力何时能拿到；NDA 存放规则 | 维持假设登记册 | DR0 冻结、S12 替换、S26 | B D-07、C Q-08 |
| Q-15 | P1 | 结温限值与 TIM2 选型（C-08）由谁负责 | 列为输入项 | S07 结论、S19 判据 | B D-17 |
| Q-16 | P1 | 在算算例去留：UC-01b 12 格是否续算、HBM 方案 D 汇流槽（1223 万，只能 CPU）是否继续 | S34 读日志后定 | S15、S17、S18 | B D-18 |
| Q-17 | P3 | OpenFOAM 交叉验证是否启用（WSL2 已有） | 建议 S16 起可选 | S16（可选） | A Q12 |
| Q-18 | P2 | 孪生 / 控制对象范围：只做单板台架，还是有真实托盘 / CDU 可接 | 先台架，后托盘 | S28–S30、S40 | B D-13、C Q-09 |
| Q-19 | P2 | Grace（CASE-02）是否同步推进及优先级 | P2 起作第二算例 | S13 排期 | B D-14、C Q-02 |
| Q-20 | P2 | 正式 FTO 由谁做、何时完成 | DR3 闸门前完成，外部专业服务 | S37、S22 前 | A G-11、C R-13 |
| Q-21 | P2 | 用户每周可投入时长 | 工期按 10–15 h / 周估 | 全局工期 | B D-19 |
| Q-22 | P3 | 智能体拆分：维持 `cp-design` 单体，还是拆 `cp-cae`、`cp-test`、`cp-twin`；`practice01_0926` 命名零漂移 | 前期单体，S33 评审 | S33 | A Q11、B D-16、G-14 |
| Q-23 | P3 | 三版 v1.0 旧规划文件的清理（建议删除清单由最终回复给出） | 用户确认后再删 | 无 | 本次合并 |

## 附录 A 来源文件索引

| 简称 | 路径 | 日期 |
|---|---|---|
| v2.0 | `AP/references/NVIDIA_B300_微通道冲击换热冷板设计报告_v2.0_20260914new.html` | 2026-09-14（含 09-28 修订节） |
| v2.1 | `AP/references/NVIDIA_B300_微通道冲击换热冷板设计报告_v2.1_PG25_20260929.html` | 2026-09-29 |
| Grace v1.0 / v1.1 | `AP/references/NVIDIA_Grace_GB300_冷板详细设计报告_v1.0_20260926.html`、`…_v1.1_PG25_20260929.html` | 2026-09-26 / 09-29 |
| 技术调查 v1.3 / 专利 v1.4 | `AP/references/AI算力芯片液冷冷板技术调查分析报告_v1.3_20260907.html`、`…专利分析报告_v1.4_20260907.html` | 2026-09-07 |
| UC01 说明 / Grace 边界 | `AP/references/UC01_…说明.html`、`AP/references/参考_GB300_Grace_CPU…_20260926.html` | 2026-09-20 / 09-26 |
| 循环 0926 | `AP/cycle-20260926/` | 2026-09-26 |
| model.py | `design/calc/model.py`（WATER40、PG25_40） | — |
| HBM 1D v1.0 | `design/cfd_HBM/HBM微通道冷板_1D设计报告_v1.0_20260929.html`（DOWFROST LC 25、方案 D） | 2026-09-29（10-01 修改） |
| CFD-AI 评估 | `design/CFD-AI_Agent_能力评估与工作计划_v1.0_20260920.html` | 2026-09-20（部分已取代） |
| 12 格契合性 | `design/cfd/uc01b_2.4x3.0lessmesh12cells/UC01b_lessmesh_ICEM_Fluent_…_12cells_600step.html` | 2026-09-27 |
| DR 门表 / PG25 分配表 | `cad/尺寸链计算/汇总报告/01–04_*.xlsx`、`cad/尺寸链计算/GB300_冷板液冷热量与流量分配表_PG25_20260929.xlsx` | 2026-09-29 / 09-30 |
| 记忆 | `AP/memory/semantic/b300-design-lock.md`（last_verified 2026-10-01）等 6 条 | — |
| 三版 v1.0 规划 | A `AP/docs/plan/`；B `AP/planning/`；C `AP/plan/` | 2026-10-02 |

## 附录 B 变更记录（v1.0 三版 → v1.1）

| 版本 | 日期 | 内容 |
|---|---|---|
| v1.0-A | 2026-10-02 | `docs/plan/` 项目规划与实施计划：现状盘点、缺口 G-01～G-14、需求、架构与选型、①–⑦ AI 结合、一维工具设计、自动化链路、V&V、孪生与控制、风险、里程碑（23 周）、决策 Q1–Q12；实施计划 P0–P7、S01–S33 |
| v1.0-B | 2026-10-02 | `planning/` 项目规划与实施计划 + `build_plan.py`：算例驱动、推荐技术栈表、分级仿真 L0–L4、四道工程闸门、V&V 20、17 个候选 skills 与 12 条候选 memories、40 周甘特、开放问题 D-01～D-19；步骤 S0.1–S7.7 |
| v1.0-C | 2026-10-02 | `plan/` 项目规划与实施计划 + `build_plan_html.py`：本机环境探测（MATLAB R2025b 工具箱、Ansys v261 模块）、KPI 表、证据等级 E0–E5、manifest 规范、HBM / Grace 参数表、PG25 压降风险；步骤 S01–S46（含可并行的 S19 只读收口） |
| **v1.1** | **2026-10-02** | **合并为唯一一套**，放在 `docs/plan/`，md 为唯一正文源，`docs/plan/build_plan.py` 一键生成 html |

v1.1 合并内容：

1. **主体结构**：沿用 A 的章节与 S01–S33 编号。新增 S34–S40，编号连续：
   - S34：已有 CFD 日志只读收口，来自 C S19 / B S0.3；
   - S35：记忆与文档体检，来自 C S04；
   - S36：manifest 规范与工具，来自 B S0.5 / C S06；
   - S37：DR0/DR1 复核与 FTO 对照草稿，来自 C S07–S08；
   - S38：孪生 / 控制双路线 PoC 与 FMU 接口，新增；
   - S39：R1 回路 AI 自动扫描 / 优化，来自 B §7.4 / C S27；
   - S40：HIL 联调与 DR6 放行包，来自 B S7.6–S7.7。

   另有几处并入：V1 代码验证并入 S16，孔径 D0.40/D0.50 对比与层流/SST 敏感性并入 S17（来自 C S22–S23），DR5 验收包并入 S30。
2. **新增用户要求**：
   - D-001 设计工况写为已决策，给工况矩阵与粗估流量，并说明与 3.512 L/min 及两套物性的关系（§0.2、§3.2），各阶段引用；从开放问题中删去“主设计点选哪套”。
   - 数字孪生与孪生在环 AI 控制写成路线 A / 路线 B 两条并列路线，给对比表与推荐，选择列为 Q-07（§9.2–§9.6）。
   - 设计流程模型扩展为 ①–⑨ 九阶段、DR0–DR6 七道门控、R1–R4 四条回路，每张卡片有 AI 赋能 / 工具行、状态和实施 Phase，用内联 SVG 重绘（§5.0）。
3. **吸收 B**：推荐技术栈表（§0.3、§4.6），40 周甘特与工期（§0.4、§12；P6 拆为 P6a/P6b），算例驱动（§1.2），分级仿真 L0–L4（§4.5），四道工程闸门（§5.12），V&V 20 框架（§8.4），候选 skills / memories（§10.6–§10.7），FMU 变量约定（§9.8），开放问题，以及 `build_plan.py` 作为生成器原型。
4. **吸收 C**：本机环境探测（经本版核实，§2.5），证据等级 E0–E5（§1.5），KPI 表（§3.6），manifest 字段（§10.3），PG25 压降与 Grace 22.9 kPa 风险（§0.2、§2.3），可并行步（S34–S36），控制用例 C-1～C-6（§9.7）。
5. **核对与更正**（§2.6 K-01～K-14）：
   - MATLAB 已安装，A 的说法有误；
   - 14–24 kPa 的流量口径以 v2.1 原文为准，A 有误；
   - 两套 PG25 物性的具体数值；
   - HBM 四个版本与时间顺序；
   - 12 格续算无新记录；
   - `calc_1d_out.txt`、CFD-AI 评估两份文件已取代；
   - `AP/` 未纳入 git 跟踪。
6. **去重**：三版的重复缺口、需求、风险、候选清单合并，标注三版来源；开放问题合并为 Q-01～Q-23，按 P0–P3 优先级排序并标明阻塞步骤。
7. **未改动**：A、B、C 的任何旧文件均未删除或修改；建议删除清单只在交付说明中列出，由用户确认后再删。

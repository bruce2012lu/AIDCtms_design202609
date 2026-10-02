# AIDC 液冷系统 AI 设计平台 · 实施计划 v1.0

> 文档编号 AIDC-PLAT-IMPL-001 · 版本 v1.0 · 日期 2026-10-02 · 状态：计划草案，待用户评审，**尚未开始执行任何步骤**
>
> 配套：《AIDC 液冷设计平台 · 项目规划 v1.0》（同目录，下称“规划”）。路径都相对 `agents/AIDCtms/coolingplate/`，下文 `AP/` 代表 `agent/practice01_0926/`。

## 0 使用说明

### 0.1 怎么按指令执行

每个步骤有唯一编号 S01、S02…。用户在对话里发一句指令即可启动一步，例如：

- `执行 S04`：按步骤卡完整执行。
- `执行 S04，只做到产出物，不写记忆`：裁剪执行范围。
- `S04 验收`：AI 按验收标准逐条自检并给出通过 / 不通过清单。
- `S04 回滚`：删除该步骤在 `runs/` 和新目录下的产物（不动已有文件）。

AI 每执行一步，都按以下顺序：读规划相关章节和步骤卡 → 检查依赖步骤是否已验收 → 列出将要写入的文件并等待确认（涉及闸门时）→ 执行 → 自检验收 → 写 episodic 记忆草稿 → 更新本计划的状态表与沉淀台账 → 给出 `git-release` 提交信息建议（真实 commit 与 push 由人执行）。

### 0.2 步骤卡字段

| 字段 | 含义 |
|---|---|
| 目标 | 这一步要解决的问题，一句话 |
| 输入 | 依赖的文件、数据、前置步骤 |
| AI / 工具动作 | AI 要做的具体动作和用到的工具 |
| 产出物 | 文件路径（新文件为主，不改已有文档） |
| 验收标准 | 可检查的判据 |
| 人工闸门 | 平台三道闸门（①技能安装、②记忆继承、③实盘/资金动作）与 DR 签字、项目约定的人确认点 |
| 沉淀候选 | 完成后应登记到 §6 台账的 skill / memory 候选 |
| 依赖与工期 | 前置步骤与预估人·天（AI 执行 + 人审） |

### 0.3 状态标记

`待开始` → `进行中` → `待验收` → `已验收`；受阻时标 `受阻（原因）`。本版所有步骤都是 `待开始`。

### 0.4 全局规则

- 不改动已有文档和冻结件：`cad/params/cp_b300_jm01.yaml`、`cad/out/` 已发 STEP、`references/` 与 `cycle-20260926/` 报告只读。需要改代码时（例如 `cad/coldplate`），先在步骤卡里列出改动范围，人确认后再改，并保持旧接口兼容。
- 运行产物统一写 `AP/runs/<YYYYMMDD-HHMMSS>-<步骤>-<简称>/`。
- 大文件（cas/dat/msh、原始试验数据）不入 git，用 `manifest.json` 记录路径、大小、SHA-256。
- 多步 PowerShell 命令写成脚本文件再运行（`memory/semantic/environment.md`）。
- 安装任何第三方包（PyFluent、openpyxl、gmsh 等）比照第①道闸门，先列包名、版本、来源，人确认后再装，且只装进 `cad/.venv` 或专用 venv，不装进系统 Python（VeighNa）。

## 1 总体节奏

<!-- fig:gantt-impl -->
```text
周次             W1  W3  W5  W7  W9  W11 W13 W15 W17 W19 W21 W23
P0 准备 S01–S03   ■
P1 一维 S04–S09   ■■■
P2 CAD  S10–S13       ■■■
P3 CFD  S14–S19         ■■■■■■■■
P4 机械 S20–S22                 ■■■■
P5 试验 S23–S26                   ■■■■■■■■
P6 孪生 S27–S30                       ■■■■■■■■■■
P7 平台 S31–S33                                 ■■■■■■
```

图 1-1 · 阶段甘特图（W1 = 2026-10-05 当周）。

| 阶段 | 冲刺 | 周次 | 步骤 | 里程碑 | 主题 |
|---|---|---|---|---|---|
| P0 准备 | SP0 | W1 | S01–S03 | M0 2026-10-09 | 环境、事实底账、决策 |
| P1 一维 | SP1 | W1–W3 | S04–S09 | M1 2026-10-23 | **桌面可验证**：回归、计算书、敏感性、水力网络 |
| P2 CAD | SP2 | W3–W5 | S10–S13 | M2 2026-11-06 | v2 内核、流体域、接口、Grace |
| P3 CFD | SP3、SP4 | W4–W11 | S14–S19 | M3 2026-12-04 | 作业自动化、V4、无关性、半板、工况矩阵 |
| P4 机械 | SP5 | W8–W11 | S20–S22 | M4 2026-12-18 | FEA、公差、图纸，DR3 |
| P5 试验 | SP6、SP7 | W10–W17 | S23–S26 | M5 2027-01-29 | 台架、数据、V&V，DR4 |
| P6 孪生 | SP8 | W12–W21 | S27–S30 | M6 2027-02-26 | ROM、动态孪生、AI 控制 |
| P7 平台 | SP9 | W18–W23 | S31–S33 | M7 2027-03-12 | MCP 扩展、技能记忆入库、拆分评审 |

### 1.1 步骤总表

| 编号 | 步骤 | 阶段 | 门槛 | 状态 |
|---|---|---|---|---|
| S01 | 环境、授权与数据分级盘点 | P0 | 低 | 待开始 |
| S02 | 设计点注册表与冲突清单 | P0 | 低 | 待开始 |
| S03 | 决策会：基准、物性、孔径、HBM、工具 | P0 | 低（人） | 待开始 |
| S04 | 一维回归基线（黄金数据 + pytest） | P1 | **低，桌面可验证** | 待开始 |
| S05 | PG25 / v2.1 / Grace v1.1 复算核对 | P1 | **低，桌面可验证** | 待开始 |
| S06 | 一维 CLI 与计算书生成 | P1 | 低 | 待开始 |
| S07 | 敏感性、DOE 与差距闭合 | P1 | 低 | 待开始 |
| S08 | 板内与托盘水力网络、孔板配平 | P1 | 中 | 待开始 |
| S09 | DR2 复审包（可选 MATLAB 对照） | P1 | 中 | 待开始 |
| S10 | CAD 内核增加 pitch_x / pitch_y（parametric-v2） | P2 | 中 | 待开始 |
| S11 | v2 整板实体与流体域、命名面 | P2 | 中 | 待开始 |
| S12 | 接口占位：水嘴、UQD、静压箱、HBM 方案 | P2 | 中 | 待开始 |
| S13 | Grace 接入规则门并重导交错 STEP | P2 | 中 | 待开始 |
| S14 | CFD 作业自动化骨架（预检、提交、解析） | P3 | 中 | 待开始 |
| S15 | 已有 CFD 结果入账与能量平衡复核 | P3 | 低 | 待开始 |
| S16 | V4 Martin 锚定（Re≈3000） | P3 | 中 | 待开始 |
| S17 | 单胞网格无关性（三套网格） | P3 | 中 | 待开始 |
| S18 | 单 die / 半板模型（Q2、Q4） | P3 | 高 | 待开始 |
| S19 | 工况矩阵 C01–C12 与 DR3 仿真评审包 | P3 | 高 | 待开始 |
| S20 | 结构 FEA（承压、压装、热应力） | P4 | 中 | 待开始 |
| S21 | 公差与统计尺寸链 | P4 | 低 | 待开始 |
| S22 | 候选工程图包与 DR3 闸门 | P4 | 中 | 待开始 |
| S23 | 试验大纲与 TTV 台架设计 | P5 | 中 | 待开始 |
| S24 | 试验数据模板与导入工具 | P5 | 低 | 待开始 |
| S25 | V&V 对比与 R2 回路自动化 | P5 | 中 | 待开始 |
| S26 | DR4 送样放行包 | P5 | 高（实物） | 待开始 |
| S27 | ROM 代理模型 | P6 | 中 | 待开始 |
| S28 | 托盘级动态热–水力孪生与 FMU | P6 | 中 | 待开始 |
| S29 | AI 在环控制仿真（PID / MPC） | P6 | 中 | 待开始 |
| S30 | 孪生在线校准与回放 | P6 | 高 | 待开始 |
| S31 | MCP 工具扩展与设计台新页 | P7 | 中 | 待开始 |
| S32 | skills / memories 正式入库 | P7 | 低（人） | 待开始 |
| S33 | 智能体拆分评审与平台发布 | P7 | 低（人） | 待开始 |

## 2 前置条件与闸门映射

### 2.1 前置条件

| 条件 | 需要它的步骤 | 现状 |
|---|---|---|
| `cad/.venv` 可用（build123d、numpy、scipy、pytest、pyyaml） | S04–S13 | 已有 |
| openpyxl（读 xlsx 黄金数据） | S04、S05 | 系统 Python 有，`cad/.venv` 没有 |
| Fluent 2026 R1 可批处理 | S14–S19 | 已在运行 |
| PyFluent / PyMechanical | S14、S20 | 未装 |
| Mechanical 许可 | S20 | 待核 |
| MATLAB | S09（可选）、S28、S29 | 未探测到 |
| 样件加工与台架资金 | S23、S26 | 待决策 |

### 2.2 闸门映射

| 闸门 | 本项目中的含义 | 涉及步骤 |
|---|---|---|
| ① 技能安装 | 新技能入库；第三方 Python 包、开源求解器安装（比照） | S14、S16、S20、S27、S32 |
| ② 记忆继承 | 采纳 `design/memory`、`cad/memory`、CFD 目录 semantic 前核对置信度与有效期 | S02、S15、S32 |
| ③ 实盘 / 资金动作 | 采购、外协加工、对外发图、试验台通电、向真实设备下发设定值（比照，待用户批准映射） | S22、S23、S26、S29、S30 |
| DR 签字 | DR0–DR4 由用户签字 | S03、S09、S19、S22、S26 |
| 项目确认点 | 改 CAD 内核代码；覆盖任何非 `runs/` 文件；启动长时 CFD 作业 | S10、S14、S18、S19 |

## 3 步骤卡

### 3.1 P0 准备

#### S01 环境、授权与数据分级盘点

| 项 | 内容 |
|---|---|
| 目标 | 弄清本机能用哪些软件、许可和算力，确定数据能放在哪里 |
| 输入 | 规划 §4.5、§10.1；`memory/semantic/environment.md`；`design/CFD-AI_Agent_能力评估与工作计划_v1.0_20260920.html` 附录 A 的探测方法 |
| AI / 工具动作 | 写只读探测脚本：Ansys 各模块与 `ansysli` 许可特性、Fluent 版本、HPC 核数、GPU 显存、MATLAB/SolidWorks/FreeCAD/NX/OpenFOAM/WSL、Python 环境包清单、`git remote -v` 与仓库可见性提示；汇总成表 |
| 产出物 | `AP/runs/<ts>-S01-env/probe.ps1`、`env_report.md`、`env.json` |
| 验收标准 | 每个工具都有“可用 / 不可用 / 待人确认”结论和证据（路径或命令输出）；数据分级表已列出 D1–D4 的实际存放位置 |
| 人工闸门 | 无写入动作；结果由人确认（许可特性需人补充） |
| 沉淀候选 | memory：更新 `semantic/environment.md` 的软件与许可段；skill：`env-probe` |
| 依赖与工期 | 无依赖；0.5 天 |

#### S02 设计点注册表与冲突清单

| 项 | 内容 |
|---|---|
| 目标 | 把散在报告、xlsx、py、yaml 中的设计数字收成单一来源，列出全部冲突 |
| 输入 | v2.0、v2.1、Grace v1.0/v1.1、HBM 1D v1.0、`cycle.json`、`design/calc/model.py`、`cad/params/cp_b300_jm01.yaml`（只读）、`cad/尺寸链计算/*.xlsx`、`memory/semantic/*.md` |
| AI / 工具动作 | 抽取数字建 `designpoints/DP-A-W.yaml`、`DP-B-W.yaml`、`DP-P-1400.yaml`；物性 `props/water40_v20.yaml`、`props/pg25_model.yaml`、`props/pg25_dowfrost.yaml`；几何 `geo/b300_v20_216.yaml`、`geo/hbm_A…D.yaml`、`geo/grace_mc01.yaml`；每个字段带 `source`、`date`、`confidence`；写冲突检测脚本，输出冲突清单（对应规划 G-02～G-05、G-12） |
| 产出物 | `AP/designpoints/`、`AP/designpoints/props/`、`AP/designpoints/geo/`、`AP/designpoints/README.md`、`AP/runs/<ts>-S02-dp/conflicts.md` |
| 验收标准 | 三个设计点能被脚本加载；每个数字都能追到来源文件和章节；冲突清单至少覆盖 PG25 物性、HBM 截面、孔径、设计基准四类 |
| 人工闸门 | ② 记忆继承：引用 `design/memory`、`cad/memory` 时核对 `confidence ≥ 0.6` 且未过期 |
| 沉淀候选 | skill：`input-trace`；memory：semantic `design-point-registry.md`（注册表结构与当前主基准） |
| 依赖与工期 | S01 可并行；1.5 天 |

#### S03 决策会：基准、物性、孔径、HBM、工具

| 项 | 内容 |
|---|---|
| 目标 | 关闭规划 §13 中阻塞主线的决策 |
| 输入 | S01 环境报告；S02 冲突清单；规划 §4.4 选型、§13 |
| AI / 工具动作 | 为 Q1–Q12 各写一页决策卡（选项、证据、影响步骤、推荐），汇总成决策表；会后把决议写回注册表的 `status` 和 `current` 字段（只改本步新建的文件） |
| 产出物 | `AP/docs/plan/决策记录_v1.0_<日期>.md` |
| 验收标准 | Q1、Q2、Q3、Q6、Q7、Q8 有明确决议或明确的待定日期；注册表只有一个 `current` HBM 方案和一个主设计点 |
| 人工闸门 | 用户签字；DR0 有条件放行确认 |
| 沉淀候选 | memory：semantic `b300-design-lock.md` 更新（主基准、孔径、HBM 方案），episodic 决策记录 |
| 依赖与工期 | S01、S02；0.5 天（人） |

### 3.2 P1 一维（第一批，低门槛、桌面可验证）

#### S04 一维回归基线（黄金数据 + pytest）

| 项 | 内容 |
|---|---|
| 目标 | 把现有 `oned.py`、`zones.py`、`design/calc/model.py` 锁成可回归的工具，证明它们能复现 v2.0 报告和 0926 循环的数 |
| 输入 | v2.0 §9.2–§9.11 表格；`cycle-20260926/out/cycle.json`；`design/calc/validate_out.txt`；S02 注册表 |
| AI / 工具动作 | 从 v2.0 HTML 和 `cycle.json` 抽黄金值写成 `tests/golden/*.json`（每个值带来源章节）；写 pytest：DP-A/DP-B 的孔速、Re、孔口 ΔP、R_conv、R 区间、ΔTf、HBM 速度、压降分段、孔径扫描 5 档、差距闭合 8 行、承压 3 工况、尺寸链 11 项；`oned_design`、`hbm_design`、`grace_design` 的 MCP 返回值结构测试；在 `cad/.venv` 运行 |
| 产出物 | `AP/tests/golden/v20_dpa.json`、`v20_dpb.json`、`cycle0926.json`；`AP/tests/test_oned_regression.py`、`test_zones_regression.py`、`test_mcp_tools.py`；`AP/runs/<ts>-S04-regress/report.md` |
| 验收标准 | 全部测试通过，关键量相对偏差 ≤ 0.5%；不通过的列出差值和原因（例如 `calc_1d_out.txt` 128 孔旧口径只作反例记录）；一条命令可重跑：`cad\.venv\Scripts\python.exe -m pytest agent\practice01_0926\tests -q` |
| 人工闸门 | 无（只新增测试文件）；若需装 openpyxl 进 `cad/.venv`，比照①确认 |
| 沉淀候选 | skill：`oned-calc`（回归部分）；memory：episodic 回归结果，semantic `oned-regression.md`（黄金数据来源与容差） |
| 依赖与工期 | S02（可先用报告值直接建，不阻塞）；1 天 |

建议指令：`执行 S04`。这是第一步可以马上在桌面验证的工作，不依赖任何新软件。

#### S05 PG25 / v2.1 / Grace v1.1 复算核对

| 项 | 内容 |
|---|---|
| 目标 | 用 Python 复现 v2.1 与 PG25 工作簿的关键数，并量化两套 PG25 物性的差别 |
| 输入 | v2.1 §1、§3、§4；Grace v1.1 §3；`GB300_冷板液冷热量与流量分配表_PG25_20260929.xlsx`；HBM 1D v1.0；S02 物性文件 |
| AI / 工具动作 | 按公式重算：比流量 2.509 L/(min·kW)、模组 3.512 L/min、GPU 核心 2.283 L/min、孔速 0.897/1.402 m/s、HBM 单颗 0.1096 L/min 与腿内流速 0.082 m/s、Grace 0.753 L/min、Grace 0.8 L/min 下 CPU 槽速 0.502 m/s、通道 2.44 kPa、孔板 20.5 kPa、合计 22.9 kPa；分别用 `pg25_model` 与 `pg25_dowfrost` 物性跑一遍，给出 Re、ΔP、h 的差异表；补黄金数据与测试 |
| 产出物 | `AP/tests/golden/v21_pg25.json`、`grace_v11.json`；`AP/tests/test_pg25_regression.py`；`AP/runs/<ts>-S05-pg25/report.md` |
| 验收标准 | 与报告值偏差 ≤ 0.5%（Grace 孔板 ≤ 1%）；两套物性差异表完整；xlsx 公式格无缓存值的问题有处理说明 |
| 人工闸门 | 无 |
| 沉淀候选 | memory：semantic `pg25-properties.md`（两套来源、选用结论待 S03）；skill：`oned-calc`（工质部分） |
| 依赖与工期 | S04；0.5 天 |

#### S06 一维 CLI 与计算书生成

| 项 | 内容 |
|---|---|
| 目标 | 一条命令对任一设计点出完整一维计算书（md/html/json），设计台和 MCP 共用 |
| 输入 | S02 注册表；S04、S05 测试；`cycle-20260926/make_cycle.py` 的报告写法 |
| AI / 工具动作 | 新建 `AP/oned_pkg/`（包装现有 `oned.py`、`zones.py`，不改其接口）：`cli.py` 支持 `run --dp <id> [--overlay k=v]`；计算书含公式、代入值、结果、判据、证据等级、适用域警告；单文件 HTML 无外部依赖；MCP 新增 `oned_report` 工具（`server.py` 改动先列清单再改） |
| 产出物 | `AP/oned_pkg/__init__.py`、`cli.py`、`report.py`、`templates/`；`AP/runs/<ts>-S06-oned-DP-A-W/{inputs.yaml,result.json,report.md,report.html}` |
| 验收标准 | 三个设计点都能出计算书；result.json 与 S04 黄金数据一致；HTML 离线可开；S04/S05 测试仍全过 |
| 人工闸门 | 改 `mcp/server.py` 前人确认改动范围 |
| 沉淀候选 | skill：`oned-calc`（CLI 与报告）；memory：episodic |
| 依赖与工期 | S04、S05；1 天 |

#### S07 敏感性、DOE 与差距闭合

| 项 | 内容 |
|---|---|
| 目标 | 量化每个杠杆对热阻和压降的影响，给 R1 回路和 CFD 选点 |
| 输入 | S06 工具；v2.0 §9.10、§9.11；规划 §5.9 杠杆清单 |
| AI / 工具动作 | 单因素扫描（D 0.30–0.50、Q、TIM2 0.002–0.008、槽深 0.8–1.5、工质）；龙卷风图；拉丁超立方 DOE（≥ 1000 点）；所需 h 与差距闭合矩阵；Pareto（R vs ΔP）；从 Pareto 前沿挑 3–5 个 CFD 候选；越 Martin 域的点标警告；经 `librarian` 检索低 Re 液体阵列射流关联式作为升级候选（只登记，不替换） |
| 产出物 | `AP/runs/<ts>-S07-sweep/{doe.csv,tornado.png,pareto.png,gap.md,candidates.yaml}` |
| 验收标准 | 基线点结果与 S04 一致；龙卷风给出前三大杠杆；候选清单每项写明预测 R、ΔP、证据等级 E1 |
| 人工闸门 | 无 |
| 沉淀候选 | skill：`oned-calc`（DOE 部分）；memory：semantic `levers.md`（杠杆排序，`valid_until` 3 个月） |
| 依赖与工期 | S06；1 天 |

#### S08 板内与托盘水力网络、孔板配平

| 项 | 内容 |
|---|---|
| 目标 | 回答 PG25 下整板和 Grace 支路是否超 20 kPa，给孔板孔径建议 |
| 输入 | S02 注册表；v2.1 §3（14–24 kPa 外推）；Grace v1.1 §3（22.9 kPa）；Grace v1.0 §3（孔板配平原理）；UQD 参考 4–8 kPa/对 |
| AI / 工具动作 | 写节点–支路求解器（scipy，Newton）：静压箱、216 孔并联、槽、回液、UQD、歧管；托盘 4 GPU + 2 Grace 并联；孔板孔径反算到 8–12 kPa 窗；未知项（静压箱）参数化并给区间；对 Grace v1.1 的 22.9 kPa 做验证用例 |
| 产出物 | `AP/oned_pkg/network.py`；`AP/tests/test_network.py`；`AP/runs/<ts>-S08-hydro/{network.yaml,result.json,report.html}` |
| 验收标准 | Grace 验证用例偏差 ≤ 2%；质量守恒误差 < 1e-6；给出 PG25 主基准下各支路流量与压降、孔板孔径建议及其敏感性 |
| 人工闸门 | 无 |
| 沉淀候选 | skill：`hydro-network`；memory：semantic `tray-hydraulics.md`（结论待 ICD 确认，置信度 ≤ 0.6） |
| 依赖与工期 | S05、S06；1.5 天 |

#### S09 DR2 复审包（可选 MATLAB 对照）

| 项 | 内容 |
|---|---|
| 目标 | 在主基准下重出 DR2 性能基线闸门包，供用户签字 |
| 输入 | S04–S08 产出；v2.0 §4.1 DR2 条件 |
| AI / 工具动作 | 汇总计算书、回归报告、敏感性、水力网络成闸门包；如果 S01 确认 MATLAB 可用，交 `ai-matlab` 用 Simscape 搭同一稳态点做对照（ΔTf、ΔP 偏差 < 1%）；不可用则跳过并注明 |
| 产出物 | `AP/docs/reports/DR2_性能基线复审包_v1.0_<日期>.html`；可选 `AP/runs/<ts>-S09-simscape/` |
| 验收标准 | 闸门包逐条对照 DR2 放行条件；结论分“通过 / 有条件 / 不通过” |
| 人工闸门 | DR2 签字 |
| 沉淀候选 | memory：episodic DR2 复审；semantic `b300-design-lock.md` 若结论变化则更新 |
| 依赖与工期 | S04–S08；0.5 天 + 人审 |

### 3.3 P2 CAD

#### S10 CAD 内核增加 pitch_x / pitch_y（parametric-v2）

| 项 | 内容 |
|---|---|
| 目标 | 让参数化内核能表达 v2 的 216 孔各向异性阵列，同时不破坏 v1 |
| 输入 | `knowledge/cad-kernel-gap.md`；`cad/coldplate/{model,rules,geometry}.py`；`cad/tests/`；S02 `geo/b300_v20_216.yaml` |
| AI / 工具动作 | 列出改动清单（字段、规则、几何、`REPORT_REFERENCE`），人确认后实现：`jets.pitch_x/pitch_y`（缺省回落 `pitch`）、`count_x/count_y` 按 die 校核阵面不越 die、v2 对账表单独存放；新增候选参数集 `AP/designpoints/geo/cp_b300_jm01_v2.yaml`（不碰冻结 yaml）；`cad_inspect` 接受新字段；补测试 |
| 产出物 | `cad/coldplate/` 改动（经确认）；`cad/tests/test_rules_v2.py`；`AP/runs/<ts>-S10-cadv2/` |
| 验收标准 | v1 原有测试全过（向后兼容）；v2 参数 `cad_inspect` 给 `pass` 或明确 WARN；故意越界的参数被拒；`cad-tracks.json` 规划新增 `parametric-v2` 轨道（文件改动经确认） |
| 人工闸门 | 改内核代码前人确认；`cad_build` 必须 `confirm=true` |
| 沉淀候选 | skill：`cad-v2-kernel`（并入 `cad-loop` 的升级）；memory：semantic `cad-tracks.md` 更新（新增轨道） |
| 依赖与工期 | S03（孔径与 HBM 决议）、S04；2 天 |

#### S11 v2 整板实体与流体域、命名面

| 项 | 内容 |
|---|---|
| 目标 | 一键生成 v2 整板固体、流体域和命名面清单，供 CFD 与 FEA 使用 |
| 输入 | S10 内核；`cycle-20260926/build_cad.py`（已有 216 孔整板生成法）；规划 §7.3 命名规范 |
| AI / 工具动作 | 由固体布尔反求流体域，或写 SpaceClaim `/RunScript` 做 Volume Extract；按 `inlet_*`、`outlet_*`、`wall_heat`、`interface_*` 命名；STEP 回读核对（包围盒 95×75×8.5、孔数 216、孔径、体积差与孔体积一致）；导出单胞（D0.40 与 D0.50 两版）和 1/2 板 |
| 产出物 | `AP/runs/<ts>-S11-fluid/{solid.step,fluid.step,cell_d040.step,cell_d050.step,half.step,named_faces.json,check.md}` |
| 验收标准 | 回读核对全部通过；命名面清单与 STEP 面一一对应；全流程 ≤ 10 min |
| 人工闸门 | `cad_build confirm=true` |
| 沉淀候选 | skill：`fluid-extract`；memory：episodic |
| 依赖与工期 | S10；1.5 天 |

#### S12 接口占位：水嘴、UQD、静压箱、HBM 方案

| 项 | 内容 |
|---|---|
| 目标 | 补上 CFD 和图纸都需要的接口特征（先占位，ICD 到后替换） |
| 输入 | v2.0 §6.6、§7.1、§8.11；asm_0921 结构记忆（只读解释）；S03 HBM 决议 |
| AI / 工具动作 | 参数化水嘴（内径、方向、位置）、UQD 等效段、静压箱腔；HBM 方案按 `current` 生成；所有占位尺寸标 `placeholder: true` |
| 产出物 | `AP/designpoints/geo/interfaces.yaml`；`AP/runs/<ts>-S12-ifc/` |
| 验收标准 | 占位特征在规则门中有专门规则（不与芯片区干涉、密封边 ≥ 规定值）；图纸和 CFD 能识别占位标记 |
| 人工闸门 | 无（只在 `runs/`）；替换为 ICD 尺寸时人确认 |
| 沉淀候选 | memory：semantic `interfaces-placeholder.md`（置信度 0.5，ICD 到即过期） |
| 依赖与工期 | S10、S11；1 天 |

#### S13 Grace 接入规则门并重导交错 STEP

| 项 | 内容 |
|---|---|
| 目标 | 让 Grace 冷板也走同一套“先规则后建模”的门，并修正 STEP 仍是同向模型的问题 |
| 输入 | `design/make_grace_concept.py`；Grace v1.0 §4、§8；`knowledge/cad-tracks.json` grace-concept |
| AI / 工具动作 | 为 Grace 写规则集（肋 ≥ 0.30、槽宽 ≥ 0.40、深宽比 ≤ 5、端墙 0.8、口带位置）；以子进程调用概念脚本重导交错 STEP 到 `runs/`；回读核对 48 槽奇偶方向 |
| 产出物 | `AP/designpoints/geo/grace_rules.py` 或内核新模块（经确认）；`AP/runs/<ts>-S13-grace/` |
| 验收标准 | 规则门对 v1.0 参数 `pass`；交错 STEP 回读确认奇偶口位置；不覆盖 `design/out/grace/step/` 原文件 |
| 人工闸门 | `confirm=true` |
| 沉淀候选 | memory：semantic `grace-and-tray.md` 更新；skill：`cad-loop` 增补 Grace 段 |
| 依赖与工期 | S10；1 天 |

### 3.4 P3 CFD

#### S14 CFD 作业自动化骨架（预检、提交、解析）

| 项 | 内容 |
|---|---|
| 目标 | 把“写 journal → 预检 → 提交 → 监控 → 解析”做成可调用工具 |
| 输入 | `skills/cfd-loop`、`skills/fluent-gui-capture`；已有算例目录的 journal 与日志；CFD-AI 评估 v1.0 附录 B、C；S01 许可与 GPU 结论 |
| AI / 工具动作 | journal 模板（参数化孔径、流量、热流、模型）；`cfd_preflight`（网格量 × 2.2 GB/百万单元 vs 空闲显存、许可核数、已有 Fluent 进程）；`cfd_job_submit` / `cfd_job_status`（子进程，日志落 `runs/`）；transcript 与 surface report 解析器；PyFluent 作为可选层（安装比照①） |
| 产出物 | `AP/cfd/templates/*.jou`、`AP/cfd/preflight.py`、`AP/cfd/jobs.py`、`AP/cfd/parse.py`；`AP/tests/test_cfd_parse.py`（用已有日志做测试样本） |
| 验收标准 | 解析器对已有 m425、bc216、12 格日志的提取值与报告一致；预检对 1223 万单元网格判“不开 GPU”（`cfd-loop` 示例）；一次短算（≤ 20 步）在目标版本空跑通过 |
| 人工闸门 | ① 安装 PyFluent 前确认；启动求解器前人确认（本机有其他 Fluent 作业时禁止启动） |
| 沉淀候选 | skill：`cfd-batch`；memory：semantic `cfd-automation.md`（命令行参数与已知坑） |
| 依赖与工期 | S01；2 天 |

#### S15 已有 CFD 结果入账与能量平衡复核

| 项 | 内容 |
|---|---|
| 目标 | 把单胞、12 格带、HBM 的已有结果按统一格式入账，查清 12 格能量比 1.0368 的原因 |
| 输入 | `design/cfd/uc01b_*` 日志与报告；`design/cfd_HBM/`；`memory/semantic/cfd-uc01b.md`；12 格契合性报告 §3（出口回流约 2.3%） |
| AI / 工具动作 | 用 S14 解析器生成 `evidence/*.json`（网格、边界、迭代、判据状态、可否引用）；复核 12 格能量比：按回流修正后的焓平衡重算，并给出复算方案（延长出口或改回流温度）；更新设计点的 evidence 列表 |
| 产出物 | `AP/cfd/evidence/uc01b_bc216.json`、`uc01b_m425.json`、`uc01b_12y_i600.json`、`hbm_cf_w08h20_i200.json`；`AP/runs/<ts>-S15-evidence/report.md` |
| 验收标准 | 每条证据有“可引用 / 不可引用”判定和理由；能量比问题有结论或复算方案 |
| 人工闸门 | ② 继承 CFD 目录 semantic 前核对有效期 |
| 沉淀候选 | memory：semantic `cfd-uc01b.md` 更新（`last_verified`）；skill：`cfd-batch`（入账部分） |
| 依赖与工期 | S14；1 天 |

#### S16 V4 Martin 锚定（Re≈3000）

| 项 | 内容 |
|---|---|
| 目标 | 证明 CFD 设置能在 Martin 有效域内复现关联式，给设计点结果一个可信度锚点 |
| 输入 | v2.0 §10.9；CFD-AI 评估 v1.0 §7.3；S11 单胞几何；S14 作业工具 |
| AI / 工具动作 | 同一单胞网格把流量放大到 Re≈3000（D0.40 与 D0.50 各一），层流与 SST 各跑一次；提取面平均 Nu，与同 f、H/D 的 Martin 值比较；可选 OpenFOAM 交叉对比（安装比照①） |
| 产出物 | `AP/runs/<ts>-S16-v4/`；`AP/cfd/evidence/v4_*.json`；`AP/docs/reports/V4_Martin锚定报告_v1.0_<日期>.html` |
| 验收标准 | Re=3000 时 Nu 与 Martin 偏差 < 15%；收敛判据满足 v2.0 §10.8；层流与 SST 差异写明 |
| 人工闸门 | 启动长时作业前确认 |
| 沉淀候选 | skill：`cfd-vv-anchor`；memory：semantic `cfd-v4-anchor.md` |
| 依赖与工期 | S11、S14；2 天（含计算） |

#### S17 单胞网格无关性（三套网格）

| 项 | 内容 |
|---|---|
| 目标 | 关闭单胞层面的网格无关性判据 |
| 输入 | 已有 bc216（2.1 M）与 m425（4.3 M）网格；ICEM 黄金 replay；v2.0 §10.4 |
| AI / 工具动作 | 补第三套网格（比例 1 : 1.5 : 2.25），改 replay 尺寸参数重放；三套同边界求解；Richardson 外推与 GCI |
| 产出物 | `AP/runs/<ts>-S17-gci/`；`AP/docs/reports/单胞网格无关性报告_v1.0_<日期>.html` |
| 验收标准 | 相邻网格 R 与 ΔP 差 < 3%，或给出 GCI 与推荐网格 |
| 人工闸门 | 启动作业前确认 |
| 沉淀候选 | skill：`mesh-independence`；memory：semantic `mesh-policy.md` |
| 依赖与工期 | S14、S15；2 天 |

#### S18 单 die / 半板模型（Q2、Q4）

| 项 | 内容 |
|---|---|
| 目标 | 回答单胞答不了的问题：216 孔流量一致性（Q2）、静压箱与隔墙压降（Q4）、两 die 温差（Q3） |
| 输入 | S11 半板几何、S12 接口占位；S16、S17 结论；S01 算力结论 |
| AI / 工具动作 | 先单 die 108 孔，再 1/2 板（沿 X 中线，禁止 1/4）；Fluent Meshing 水密流程；`cfd_preflight` 估网格量与内存，超本机能力时出 HPC 评估书；提取逐孔流量、压力分段、两 die 温差 |
| 产出物 | `AP/runs/<ts>-S18-halfplate/`；`AP/cfd/evidence/halfplate_*.json`；HPC 评估书（如需要） |
| 验收标准 | 逐孔流量偏差统计（目标 ≤ ±10%）；静压箱压降替换一维 3–5 kPa 估值；结果标 E3 |
| 人工闸门 | 启动作业前确认；使用外部 HPC 或云前由人确认数据保密 |
| 沉淀候选 | memory：semantic `plate-cfd.md`；skill：`cfd-batch` 增补整板段 |
| 依赖与工期 | S16、S17；4 天（含计算） |

#### S19 工况矩阵 C01–C12 与 DR3 仿真评审包

| 项 | 内容 |
|---|---|
| 目标 | 跑完 v2.0 §10.7 最小工况集，给出 DR3 仿真评审结论和 R1 回路判断 |
| 输入 | S18 模型；S07 候选；v2.0 §10.1、§10.7、§10.8、§10.10 |
| AI / 工具动作 | 参数表驱动批量求解（主基准对应的工况先跑）；失败重试一次；自动核六条收敛判据；汇总全工况 R、ΔP、ΔTf；对照目标，不达标则按 S07 杠杆生成 R1 候选并请人选；同时把结果整理成 ROM 训练数据 |
| 产出物 | `AP/runs/<ts>-S19-matrix/`；`AP/docs/reports/DR3_仿真评审包_v1.0_<日期>.html`；`AP/twin/data/cfd_doe.csv` |
| 验收标准 | v2.0 §10.10 交付物清单逐条对照；R1 是否触发有明确结论 |
| 人工闸门 | DR3 仿真评审签字；R1 回路选杠杆由人决定 |
| 沉淀候选 | memory：semantic `b300-design-lock.md` 更新（E3 结论）；episodic 每次 R1 回路 |
| 依赖与工期 | S18；5 天（含计算，取决于算力） |

### 3.5 P4 机械与图纸

#### S20 结构 FEA（承压、压装、热应力）

| 项 | 内容 |
|---|---|
| 目标 | 用 FEA 替换或确认解析板条结论，补压装平面度 |
| 输入 | S11 固体 STEP；v2.0 §6.3、§6.4；S01 Mechanical 许可结论 |
| AI / 工具动作 | 写 PyMechanical/MAPDL 脚本（无许可则 CalculiX）：3 bar 内压、300–500 N 四角压装 + TIM2 等效弹簧、可选钎焊冷却；网格收敛检查；与解析 16.73 MPa 对表 |
| 产出物 | `AP/fea/templates/`；`AP/runs/<ts>-S20-fea/`；`AP/docs/reports/结构FEA报告_v1.0_<日期>.html` |
| 验收标准 | 3 bar 下安全系数 ≥ 2；压装后接触面平面度变化 ≤ 0.02 mm；与解析值量级一致 |
| 人工闸门 | ① 安装 PyMechanical 或 CalculiX 前确认 |
| 沉淀候选 | skill：`fea-loop`；memory：semantic `structure.md` |
| 依赖与工期 | S11、S01；2 天 |

#### S21 公差与统计尺寸链

| 项 | 内容 |
|---|---|
| 目标 | 从名义尺寸链升级到统计尺寸链，给公差分配建议 |
| 输入 | v2.0 §6.5、§8.1；`cad/尺寸链计算/*尺寸核实2*.xlsx`（只读）；`04_DR3` 尺寸链页 |
| AI / 工具动作 | 名义链复核；RSS 与蒙特卡洛（10⁵ 样本）；关键链：射流间隙 H、喷嘴阵与 die 对位、总厚、HBM 列宽；输出 GD&T 建议表 |
| 产出物 | `AP/runs/<ts>-S21-tol/{chains.yaml,mc.csv,report.html}` |
| 验收标准 | 名义链全部闭合；H = 2.0 ± 0.10 的统计合格率 ≥ 99.73%，否则给出收紧建议 |
| 人工闸门 | 无 |
| 沉淀候选 | skill：`tolerance-stack`；memory：episodic |
| 依赖与工期 | S10；1 天 |

#### S22 候选工程图包与 DR3 闸门

| 项 | 内容 |
|---|---|
| 目标 | 出可评审、可询价的候选图纸包，并组织 DR3 闸门 |
| 输入 | S11、S12、S20、S21；v2.0 §8.2 图纸清单；S03 CAD 决议 |
| AI / 工具动作 | ezdxf 出 JM01-A0～A6 的 DXF 与 PDF（三视图、流道、剖面、单元、孔位表、爆炸图）、BOM；图纸检查清单自动核；按 S03 决议生成 SolidWorks 宏或 FreeCAD 脚本草稿；汇总 DR3 闸门包 |
| 产出物 | `AP/drawings/<版本>/`（DXF、PDF、BOM.csv、checklist.md）；`AP/docs/reports/DR3_图纸闸门包_v1.0_<日期>.html` |
| 验收标准 | 检查清单全过；尺寸与注册表一致；图纸标“候选，非投产” |
| 人工闸门 | DR3 闸门签字；**对外发图询价比照闸门③，由人执行** |
| 沉淀候选 | skill：`drawing-loop`；memory：semantic `drawing-release.md`（图号、版本、状态） |
| 依赖与工期 | S20、S21；2 天 |

### 3.6 P5 试验与 V&V

#### S23 试验大纲与 TTV 台架设计

| 项 | 内容 |
|---|---|
| 目标 | 定出能支撑 15% V&V 判据的试验方案和台架 |
| 输入 | v2.0 §11；规划 §8.2；S19 工况 |
| AI / 工具动作 | 写试验大纲（T1–T8、出厂检验）；台架原理图与 BOM（加热块、传感器、泵、过滤、数采）；GUM 不确定度预算；先行验证方案（PMMA 透明样 + 染色/PIV） |
| 产出物 | `AP/vv/plan/试验大纲_v1.0_<日期>.md`、`台架BOM.csv`、`不确定度预算.xlsx 或 .csv` |
| 验收标准 | 热阻测量不确定度 ≤ 5%；每个试验项对应设计目标和 CFD 工况 |
| 人工闸门 | **采购台架与加工样件比照闸门③**，AI 只出清单与询价草稿 |
| 沉淀候选 | skill：`ttv-test`；memory：semantic `test-rig.md` |
| 依赖与工期 | S19 可并行开始；2 天 |

#### S24 试验数据模板与导入工具

| 项 | 内容 |
|---|---|
| 目标 | 试验数据进平台前先过格式和稳态校验 |
| 输入 | 规划 §8.5；S23 通道表 |
| AI / 工具动作 | 写 `meta.yaml` 与 CSV 模板；`test_import`：单位、量程、校准有效期、稳态判据（10 min 漂移 < 0.1 K）；用合成数据做测试 |
| 产出物 | `AP/vv/templates/`、`AP/vv/importer.py`、`AP/tests/test_vv_import.py` |
| 验收标准 | 合成的好数据通过、坏数据（单位错、未稳态、校准过期）被拒并给出原因 |
| 人工闸门 | 无 |
| 沉淀候选 | skill：`vv-loop`（导入部分） |
| 依赖与工期 | S23；1 天 |

#### S25 V&V 对比与 R2 回路自动化

| 项 | 内容 |
|---|---|
| 目标 | 自动算偏差，偏差 > 15% 时自动开 R2 工单并给反标定建议 |
| 输入 | S24 数据；S06 一维、S19 CFD 结果；规划 §8.3、§8.4 |
| AI / 工具动作 | `vv_compare`：V2–V5 偏差表；偏差分解（测量、装配、样件、模型）；参数反标定（h 倍率、TIM2、K、接触热阻；最小二乘或贝叶斯）；模型升版并保留旧版；工单模板 |
| 产出物 | `AP/vv/compare.py`、`AP/vv/calibrate.py`；`AP/runs/<ts>-S25-vv/`；`AP/vv/tickets/R2-<编号>.md` |
| 验收标准 | 用合成数据验证：偏差 20% 能触发 R2、反标定能找回设定参数（误差 < 5%） |
| 人工闸门 | 模型修正后的口径变化由人确认再写 semantic |
| 沉淀候选 | skill：`vv-loop`；memory：semantic `model-calibration.md`（每次修正带适用域与 `valid_until`） |
| 依赖与工期 | S24；1.5 天 |

#### S26 DR4 送样放行包

| 项 | 内容 |
|---|---|
| 目标 | 首件试验完成后组织 DR4 放行 |
| 输入 | 样件与试验数据；S25 结论；v2.0 §4.1 DR4 条件 |
| AI / 工具动作 | 汇总 T1–T4 结果、氦检、流阻曲线、红外、V5 偏差；出厂三曲线；DR4 闸门包 |
| 产出物 | `AP/docs/reports/DR4_送样放行包_v1.0_<日期>.html` |
| 验收标准 | TTV Rθ,c-in < 0.028 °C/W（DP-A，或主基准对应目标）；两 die 温差 ≤ 5 K；ΔP ≤ 18 kPa；100% 氦检 |
| 人工闸门 | DR4 签字；**送样、对外交付比照闸门③** |
| 沉淀候选 | memory：semantic `b300-design-lock.md` 更新（E4 结论） |
| 依赖与工期 | S25 与实物；取决于加工周期 |

### 3.7 P6 数字孪生与 AI 在环控制

#### S27 ROM 代理模型

| 项 | 内容 |
|---|---|
| 目标 | 用 CFD DOE 和一维大样本训练可快速调用的代理模型 |
| 输入 | `AP/twin/data/cfd_doe.csv`（S19）；S07 一维 DOE |
| AI / 工具动作 | 多保真度高斯过程或响应面：R(Q, P, Tin, D, TIM2)、ΔP(Q)、Tmax；留一交叉验证；越域检测；导出 pickle 与 FMU（FMPy 或 Twin Builder，视许可） |
| 产出物 | `AP/twin/rom/`、`AP/runs/<ts>-S27-rom/report.html` |
| 验收标准 | 留一误差 < 5%；越域输入返回警告并回退一维 |
| 人工闸门 | ① 安装 scikit-learn、FMPy 等包前确认 |
| 沉淀候选 | skill：`twin-rom`；memory：semantic `rom.md`（训练域、误差、版本） |
| 依赖与工期 | S19；2 天 |

#### S28 托盘级动态热–水力孪生与 FMU

| 项 | 内容 |
|---|---|
| 目标 | 建 4 GPU + 2 Grace 托盘的动态模型，回答阶跃、启停、失冷、堵塞问题 |
| 输入 | S08 水力网络；S27 ROM；材料热容 |
| AI / 工具动作 | 3–5 节点热 RC 网络 + 水力网络；Python ODE 实现（MATLAB 可用时交 `ai-matlab` 做 Simscape 对照）；导出 FMU；场景：负载阶跃、泵降速、失冷、单板堵塞 20% |
| 产出物 | `AP/twin/dynamic/`、`AP/runs/<ts>-S28-dyn/` |
| 验收标准 | 稳态与 S06/S08 一致（< 1%）；能量守恒；场景结果给区间而不是单点 |
| 人工闸门 | 无 |
| 沉淀候选 | skill：`twin-rom`（动态部分）；memory：semantic `tray-dynamics.md` |
| 依赖与工期 | S08、S27；3 天 |

#### S29 AI 在环控制仿真（PID / MPC）

| 项 | 内容 |
|---|---|
| 目标 | 在仿真里比较 PID 与 MPC 的控制效果，验证安全监督层 |
| 输入 | S28 动态孪生；规划 §9.4、§9.5 |
| AI / 工具动作 | 基线 PID；MPC（CasADi 或 MATLAB MPC 工具箱）；安全监督层（硬限值、速率限制、看门狗、回退 PID）；鲁棒性测试（ROM 误差 ±10%、传感器噪声）；RL 只作研究项 |
| 产出物 | `AP/twin/control/`、`AP/runs/<ts>-S29-ctrl/report.html` |
| 验收标准 | MPC 相对 PID 的泵功、超调、约束违反次数有量化对比；安全层在注入故障时 100% 拦截越限指令 |
| 人工闸门 | **只驱动仿真执行器；任何接到真实设备的接口比照闸门③，本步不实现** |
| 沉淀候选 | skill：`control-sim`；memory：semantic `control.md` |
| 依赖与工期 | S28；3 天 |

#### S30 孪生在线校准与回放

| 项 | 内容 |
|---|---|
| 目标 | 用试验台或机柜数据回放校准孪生，为运行期状态估计和堵塞预警做准备 |
| 输入 | S24 试验数据；S28 孪生；可获得的 CDU 或 GPU 遥测（D3 数据，需脱敏） |
| AI / 工具动作 | 离线回放；卡尔曼滤波或滑动窗口最小二乘校准；堵塞预警指标（ΔP 上升率、热阻漂移）；数据接口规范 |
| 产出物 | `AP/twin/calib/`、`AP/runs/<ts>-S30-replay/` |
| 验收标准 | 回放误差（出水温度）< 0.5 K；预警指标在注入堵塞的合成数据上有效 |
| 人工闸门 | 使用 D3 数据前人确认；不接实时控制 |
| 沉淀候选 | memory：semantic `twin-calibration.md` |
| 依赖与工期 | S24、S28；2 天 |

### 3.8 P7 平台化

#### S31 MCP 工具扩展与设计台新页

| 项 | 内容 |
|---|---|
| 目标 | 把 P1–P6 的脚本收成 MCP 工具和设计台页面 |
| 输入 | 规划 §4.3 工具清单；`mcp/server.py`；`ui/`；`软件界面方案.md` |
| AI / 工具动作 | 新增工具：`dp_list`、`dp_diff`、`oned_report`、`oned_sweep`、`hydro_network`、`cfd_preflight`、`cfd_job_*`、`cfd_extract`、`fea_run`、`drawing_build`、`test_import`、`vv_compare`、`rom_eval`；设计台新增“设计点 / 水力 / CFD 作业 / V&V / 孪生”页；每个工具补测试 |
| 产出物 | `AP/mcp/` 与 `AP/ui/` 改动（经确认）；`AP/tests/test_mcp_tools.py` 扩展 |
| 验收标准 | 所有工具在 stdio 与 HTTP 两种入口可用；会写文件的工具缺 `confirm=true` 时拒绝；原 8 个工具行为不变 |
| 人工闸门 | 改 server 与 UI 前确认 |
| 沉淀候选 | memory：semantic `mcp-tools.md` |
| 依赖与工期 | P1–P6 相关步骤；3 天 |

#### S32 skills / memories 正式入库

| 项 | 内容 |
|---|---|
| 目标 | 把台账里的候选按闸门流程正式入库 |
| 输入 | §6 台账；`platform/shared/skills/_staging/README.md`；`_meta/skill-registry.json` |
| AI / 工具动作 | 候选技能去重合并、写 SKILL.md（frontmatter：name、description）；共享技能放 `_staging/` 等人确认；私有技能放 `AP/skills/`；记忆：按治理字段补齐、更新 `memory/index.json`；标记过期项 |
| 产出物 | `platform/shared/skills/_staging/<name>/SKILL.md`；`AP/skills/<name>/SKILL.md`；`AP/memory/` 更新 |
| 验收标准 | 每个入库技能至少被成功使用两次；每条 semantic 都有 `confidence / valid_until / last_verified / expired` |
| 人工闸门 | ① 技能入库确认；② 记忆继承核对 |
| 沉淀候选 | — |
| 依赖与工期 | S31；1 天 |

#### S33 智能体拆分评审与平台发布

| 项 | 内容 |
|---|---|
| 目标 | 决定是否拆出独立智能体，并完成平台 v1.0 发布 |
| 输入 | 运行统计（token 用量、上下文长度、技能数）；规划 §4.2；`platform/registry.json`；规划 G-14 |
| AI / 工具动作 | 写拆分评审（维持单体 / 拆 `cp-cae`、`cp-twin`）；若拆：建模块目录、薄加载器 `.claude/agents/<id>.md`、registry 与 router 条目草稿；处理 `cp-design` 与 `practice01_0926` 命名不一致的方案；发布说明与 `git-release` 提交信息 |
| 产出物 | `AP/docs/plan/智能体拆分评审_v1.0_<日期>.md`；（若批准）新模块草稿 |
| 验收标准 | 命名零漂移检查通过；registry JSON 合法 |
| 人工闸门 | 新增智能体与平台层变更由人确认；真实 commit 与 push 由人执行 |
| 沉淀候选 | memory：episodic 发布记录 |
| 依赖与工期 | S31、S32；1 天 |

## 4 依赖关系与关键路径

| 步骤 | 前置 |
|---|---|
| S04 | S02（可先行） |
| S05 | S04 |
| S06 | S04、S05 |
| S07 | S06 |
| S08 | S05、S06 |
| S09 | S04–S08 |
| S10 | S03、S04 |
| S11 | S10 |
| S12、S13 | S10（S12 另依赖 S11） |
| S14 | S01 |
| S15 | S14 |
| S16 | S11、S14 |
| S17 | S14、S15 |
| S18 | S16、S17 |
| S19 | S18 |
| S20 | S11、S01 |
| S21 | S10 |
| S22 | S20、S21 |
| S23 | S19（可并行） |
| S24 | S23 |
| S25 | S24 |
| S26 | S25 + 实物 |
| S27 | S19 |
| S28 | S08、S27 |
| S29 | S28 |
| S30 | S24、S28 |
| S31 | P1–P6 |
| S32 | S31 |
| S33 | S31、S32 |

关键路径：S01 → S03 → S10 → S11 → S16 → S18 → S19 → S22 → S23 → S26。外协加工周期和算力是两个最大的进度变量。P1（S04–S09）不在关键路径上，但它是之后所有步骤的数值底座，建议最先做。

## 5 每步完成后的通用收尾

1. 按验收标准逐条自检，结果写进该步骤的 `runs/<ts>-Sxx-*/acceptance.md`。
2. 写 episodic 记忆草稿 `AP/memory/episodic/<日期>-Sxx-<任务>.json`（字段：`date`、`task`、`confidence`、`valid_until`、`last_verified`、`expired`、`done`、`open`）。本轮规划阶段不写。
3. 口径变化时起草 semantic 更新，由人确认再落盘。
4. 在 §6 台账登记 skill / memory 候选。
5. 更新 §1.1 状态表。
6. 给出 `git-release` 提交信息建议，例如 `feat(cp-design): S04 一维回归基线与黄金数据`；真实 commit 与 push 由人通过 GitKraken 执行。

## 6 skills / memories 沉淀台账（模板）

本轮只建模板，不写入任何 skill 或 memory。每完成一步，追加一行；“状态”从 `候选` 经 `草稿` 到 `已入库` 或 `已否决`。

### 6.1 skill 台账

| 编号 | 技能名 | 作用域 | 来源步骤 | 触发场景 | 已验证次数 | 草稿路径 | 闸门① | 状态 | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| K-01 | `input-trace` | 私有 | S02 | 新输入到达、报告升版 | 0 | — | 待 | 候选 | — |
| K-02 | `oned-calc` | 私有 | S04–S07 | 改参数后出一维计算书 | 0 | — | 待 | 候选 | — |
| K-03 | `hydro-network` | 私有 | S08 | 托盘配平、孔板选型 | 0 | — | 待 | 候选 | — |
| K-04 | `cfd-batch` | 私有 | S14、S15 | 批量提交与解析 Fluent | 0 | — | 待 | 候选 | — |
| K-xx | （填写） | 私有 / 共享 | Sxx | （填写） | 0 | — | 待 | 候选 | — |

字段说明：作用域为“共享”时草稿放 `platform/shared/skills/_staging/<name>/`，人确认后登记 `_meta/skill-registry.json`；为“私有”时落 `AP/skills/<name>/`。

### 6.2 memory 台账

| 编号 | 类型 | 文件 | 来源步骤 | 摘要 | confidence | valid_until | last_verified | 闸门② | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| M-01 | semantic | `AP/memory/semantic/design-point-registry.md` | S02 | 注册表结构与当前主基准 | — | — | — | 待 | 候选 |
| M-02 | semantic | `AP/memory/semantic/oned-regression.md` | S04 | 黄金数据来源与容差 | — | — | — | 待 | 候选 |
| M-03 | semantic | `AP/memory/semantic/pg25-properties.md` | S05 | 两套 PG25 物性与选用 | — | — | — | 待 | 候选 |
| M-04 | episodic | `AP/memory/episodic/<日期>-S04-oned-regression.json` | S04 | 回归结果 | — | — | — | — | 候选 |
| M-xx | （填写） | （填写） | Sxx | （填写） | — | — | — | 待 | 候选 |

填写规则：

- `confidence`：E1 结论 ≤ 0.8；E2 ≤ 0.85；E3 ≤ 0.9；含假设或占位尺寸的 ≤ 0.6。
- `valid_until`：CFD 与试验结论 3 个月；设计锁定 6 个月；环境与工具 6 个月；ICD 到达即过期的写 ICD 预计日期。
- `last_verified`：最近一次重新核对的日期，不是写入日期。
- 记忆只记结论、数字、来源和适用域，不复制大段报告正文。

## 7 变更记录

| 版本 | 日期 | 内容 |
|---|---|---|
| v1.0 | 2026-10-02 | 首版：8 个阶段、33 个步骤卡、闸门映射、依赖与关键路径、沉淀台账模板 |

# AIDC 液冷系统 AI 设计平台 · 项目规划 v1.0

> 文档编号 AIDC-PLAT-PLAN-001 · 版本 v1.0 · 日期 2026-10-02 · 状态：规划草案，待用户评审
>
> 编写：`cp-design` 规划工程师（AI）。适用对象：GB300 计算托盘上的 B300 GPU 冷板（CP-B300-JM-01）与 Grace CPU 冷板（CP-GRACE-MC-01），并为托盘、机柜级液冷预留扩展口。
>
> 路径约定：除特别说明，路径都相对 `agents/AIDCtms/coolingplate/`，例如 `agent/practice01_0926/oned.py`。配套文件：《AIDC 液冷设计平台 · 实施计划 v1.0》（同目录）。

## 0 摘要

**结论先行（置信度 0.75）**：这个平台不用从零搭。冷板设计链的一维模型、参数化 CAD 规则门、Fluent 单元胞 CFD、MCP 工具服务和设计台界面都已经有了，缺的是三样：一套**单一来源的设计点数据**、一条**可批处理、能回归的 CAD→CFD→FEA→出图自动链**，以及流程 ⑦ 试验、V&V 回路和数字孪生。建议按“先桌面可验证、后重资产”的顺序推进：

- 第一步做 Python 一维工具的回归基线。用 v2.0 报告 §9、`cycle-20260926/out/cycle.json` 和 v2.1/PG25 工作簿做黄金数据，把现有 `oned.py` / `zones.py` / `design/calc/model.py` 锁成可测试的工具。
- CFD 主力定为本机已装的 Ansys 2026 R1 Fluent，自动化层用 journal 打底、PyFluent 做便利层，OpenFOAM 作开源校核备选。CAD 主力是已有的 build123d 内核，先补上 `pitch_x/pitch_y`。工程图先走 DXF/FreeCAD 自动草图，正式图纸由人在公司 CAD 里定稿。
- 平台继续以 `cp-design` 为主责智能体，MATLAB/Simulink 交给已登记的 `ai-matlab`，文献交给 `librarian`。前期不新增注册智能体，角色先用技能（skill）拆分；到第 7 阶段再评审要不要拆成独立智能体。
- 真实资金、外协加工、实物设备通电这类动作，建议比照平台第③道闸门做人工确认。所有新 skill 先进 `_staging/`，新记忆遵循 `confidence / valid_until / last_verified`。

主要不确定性：OEM 输入（封装图、功率图、单板 ICD 流量）缺失；设计点在“水 / 1100 W”和“PG25 / 1400 W / 6 °C”之间漂移；MATLAB、SolidWorks 在本机未探测到；Ansys 各模块的许可证范围未核实。

## 1 项目愿景与范围

### 1.1 愿景

建一个“AI 驱动的算力中心（AIDC）液冷系统设计平台”。人负责定目标、做判断、签闸门；AI 负责查资料、算数、写脚本、跑批处理、对账和写报告。平台把附图的冷板七步门控流程（①需求与输入 → ⑦样件与试验）跑成可复算、可回归、可审计的工作链，并逐步延伸到托盘水力、数字孪生和 AI 在环控制。

### 1.2 项目目标（可度量）

| 编号 | 目标 | 度量 | 目标值 | 期限 |
|---|---|---|---|---|
| O-1 | 一维工具可复算 | 对 v2.0 §9 与 cycle.json 的回归偏差 | 全部关键量 ≤ 0.5% | M1（2026-10-23） |
| O-2 | 设计点单一来源 | 报告、xlsx、CAD、CFD 的数字都从 `designpoints/*.yaml` 派生 | 冲突项清零或显式登记 | M1 |
| O-3 | 几何自动化 | 216 孔 v2 整板与流体域可由参数一键生成 | 生成 + 规则门 + STEP 回读 ≤ 10 min | M2（2026-11-06） |
| O-4 | CFD 自动化 | journal/PyFluent 批处理、日志解析、结果入账 | 单胞一条命令跑通；V4 锚定偏差 < 15% | M3（2026-12-04） |
| O-5 | DR3 仿真评审 | 网格无关性、能量平衡、R 与 ΔP 判据 | 相邻网格差 < 3%，能量偏差 < 1% | M4（2026-12-18） |
| O-6 | V&V 闭环 | 试验与仿真偏差自动计算，触发回路 | 偏差 > 15% 自动开 R2 工单 | M5（2027-01-29） |
| O-7 | 数字孪生原型 | ROM + 动态热网络，可离线回放 | ROM 对 CFD 留一验证误差 < 5% | M6（2027-02-26） |
| O-8 | 设计周期 | 一次“改孔径→出 1D→出 CAD→出单胞 CFD 结论”的人工时 | 由约 2 天降到 ≤ 0.5 天 | M7（2027-03-12） |

### 1.3 范围

范围内：

- B300 冷板（GPU 射流区、HBM 微通道区）与 Grace 冷板的①–⑦全流程。
- 托盘级水力分配：4 块 GPU 冷板 + 2 块 Grace 冷板并联，孔板配平。
- 平台工具链：一维、CAD、CFD/CAE、FEA、工程图、试验数据、V&V、ROM/数字孪生、AI 在环控制（仿真内）。
- 知识与记忆沉淀：skills、memories、Dify RAG 回灌。

范围外（本期）：

- CDU、一次侧、设施水系统的详细设计（只作为边界条件和孪生接口）。
- 两相冷板、浸没液冷、纳米流体（技术调查 v1.3 §8.3 已明确不作基线）。
- 向真实 CDU / 托盘下发控制参数（只做仿真和回放，见 §9.5）。
- 采购合同、订单 ICD、FAT 保证书（v2.0 声明本设计是候选，不是订单 ICD）。

### 1.4 证据等级与术语

| 证据等级 | 含义 | 例子 |
|---|---|---|
| E1 一维 | 关联式或能量平衡 | v2.0 §9 壳–进液 0.0326–0.0366 °C/W |
| E2 单元胞 CFD | 周期胞或局部带 | UC-01b m425，R(TIM–in) 0.03134 °C/W |
| E3 整板 / 半板 CFD | 含静压箱、歧管 | 尚无 |
| E4 实测 | TTV、流阻、红外、氦检 | 尚无 |

平台所有对外数字都要带证据等级、来源文件和日期。单元胞结果不能写成整板保证值（`agent.md` “不做”第 1 条）。

## 2 现状盘点

### 2.1 本次阅读的文档

工作区 `agent/practice01_0926/`：

- 根目录：`agent.md`、`README.md`、`软件界面方案.md`、`启动冷板设计台.ps1`、`oned.py`、`zones.py`。
- `mcp/server.py`（MCP stdio + HTTP 8765，8 个工具）；`ui/index.html`、`ui/app.js`、`ui/styles.css`。
- `knowledge/`：`catalog.json`、`cad-tracks.json`、`cad-kernel-gap.md`。
- `memory/`：`profile.md`、`index.json`、`episodic/` 2 条、`semantic/` 6 条。
- `skills/`：`design-loop`、`cad-loop`、`cfd-loop`、`fluent-gui-capture`。
- `cycle-20260926/`：`index.html`、`01_一维设计.html`、`02_三维CAD.html`、`03_单孔CFD仿真分析.html`、`04_结构工艺装配.html`、`make_cycle.py`、`build_cad.py`、`out/cycle.json`；`out/*.png`、`out/cad/*.step` 只核对了清单和大小。
- `references/`：B300 设计报告 v2.0（2026-09-14）与 v2.1/PG25（2026-09-29）、Grace 详细设计 v1.0（2026-09-26）与 v1.1/PG25（2026-09-29）、UC01 壁面射流说明、GB300 Grace 边界摘录、技术调查 v1.3、专利分析 v1.4。
- `runs/20260926-140511/params.yaml`。

上级背景（快速浏览）：

- `design/calc/model.py`（函数清单）、`validate_out.txt`、`calc_1d_out.txt`；`design/CFD-AI_Agent_能力评估与工作计划_v1.0_20260920.html`；`design/cfd/uc01b_2.4x3.0lessmesh12cells/UC01b_lessmesh_1D_CFD契合性分析报告_12cells_600step.html`；`design/cfd_HBM/HBM微通道冷板_1D设计报告_v1.0_20260929.html`。
- `cad/尺寸链计算/汇总报告/01_DR0_输入追溯.xlsx`～`04_DR3_仿真图纸与试验门.xlsx`、`cad/尺寸链计算/GB300_冷板液冷热量与流量分配表_PG25_20260929.xlsx`；`cad/` 目录结构（`build.py`、`coldplate/`、`tests/`、`params/`）。
- 平台层：仓库根 `CLAUDE.md`、`platform/CLAUDE.md`、`platform/registry.json`、`.mcp.json`、`.claude/agents/cp-design.md`、`ai-matlab.md`、`thermal-management.md`、`platform/shared/skills/git-release/SKILL.md`、`_meta/skill-registry.json`。
- 本机环境探测：`E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261` 存在，目录里有 fluent、icemcfd、scdm（SpaceClaim）、Discovery、CFX、optiSLang、TwinAI、Electronics、sherlock 等模块；`MATLAB_ROOT` 未设置，MATLAB、SolidWorks、FreeCAD 的标准安装路径都不存在；`cad/.venv` 有 build123d、numpy、scipy、pytest、pyyaml，没有 openpyxl、gmsh、pyvista、ansys-*。

没有逐页读的：`papers/pdfs/` 的 12 篇论文 PDF、`solutions/` 和 `Bp/` 的商业类 pptx/pdf、`cad/asm_0921_结构说明报告`、14 MB 的 12 格 CFD 结果 HTML。这些在 §10.5 由 `librarian` 按需检索。

### 2.2 已有成果

| 资产 | 位置 | 能力 | 成熟度 |
|---|---|---|---|
| 一维数值源 | `design/calc/model.py` | 物性、几何、Martin/驻点/短槽关联式、`solve()`、孔径扫描、承压、尺寸链 | 高，v2.0 全文由它生成 |
| 一维工具封装 | `agent/practice01_0926/oned.py`、`zones.py` | GPU 射流区按 Martin 适用域自动切换低 Re 准则；HBM 平槽；Grace 平行槽 | 中，无自动化回归 |
| MCP 工具服务 | `agent/practice01_0926/mcp/server.py` | `kb_catalog`、`memory_list`、`cad_tracks`、`cad_inspect`、`cad_build`、`oned_design`、`hbm_design`、`grace_design` | 中，已登记 `.mcp.json` |
| 设计台 UI | `agent/practice01_0926/ui/` | 9 页：总览、1D、HBM、Grace、CAD 工作台、CAE、知识库、记忆、工具 | 中 |
| 参数化 CAD 内核 | `cad/coldplate/`、`cad/build.py` | yaml → 派生 → 规则门 → 实体 → STEP/DXF/PNG/SolidWorks 宏 | 高，但只能表达 v1.0 |
| 设计循环 0926 | `agent/practice01_0926/cycle-20260926/` | 1D→3D CAD→单孔 CFD→结构工艺装配四页报告，216 孔整板 STEP | 中 |
| CFD 算例 | `design/cfd/uc01b_*`、`design/cfd_HBM/` | ICEM 网格 + Fluent 共轭，单胞、12 格带、HBM 七槽 | 中，判据未全关 |
| 尺寸链与门控表 | `cad/尺寸链计算/` | DR0–DR3/DR4 门控 xlsx、PG25 热量与流量分配 | 中 |
| 技能 | `agent/practice01_0926/skills/` | 设计循环、CAD 循环、CFD 循环、Fluent GUI 取图 | 中 |
| 记忆 | `agent/practice01_0926/memory/` | 6 条 semantic，均带治理字段 | 中 |
| 调研 | `references/` 技术调查 v1.3、专利 v1.4 | 路线、关联式窗口、专利方案 A/B/C、FTO 雷区 | 高 |

### 2.3 关键数据与参数

B300 冷板 CP-B300-JM-01（v2.0 水基线，来源：v2.0 §0、§5、§9；`cycle.json`）：

| 量 | DP-A 保证点 | DP-B 包络 | 证据 |
|---|---|---|---|
| 功率 / 流量 / 进液 | 1100 W · 2.0 L/min · 40 °C 水 | 1400 W · 2.4 L/min · 40 °C 水 | 输入 |
| 几何 | 95×75×8.5 mm；每 die 9×12，共 216 孔；D 0.50，Sx 3.0，Sy 2.4，H 2.0 mm | 同左 | 候选 |
| 孔速 / Re_D | 0.629 m/s · 478 | 0.755 m/s · 573 | E1 |
| 壳–进液热阻 | 0.0326–0.0366 °C/W（目标 < 0.028） | 0.0311–0.0351 °C/W（目标 < 0.025） | E1，不判定 |
| 板内压降 | 3.5–5.5 kPa（上限 20） | 3.7–5.7 kPa | E1，静压箱 3–5 kPa 为估值 |
| 流体温升 | 7.96 K | 8.44 K | E1 |
| HBM 近壁流速 | 0.463 m/s（帽 0.80） | 0.556 m/s | E1 |
| 结温 | 84.7–93.5 °C | 94.8–106.0 °C | E1 |
| 盖板跨射流阵 | 16.73 MPa，安全系数 4 | — | 解析 |

B300 v2.1 / PG25（来源：v2.1 §1、§3、§7）：工质 PG25 40 °C，模组 1400 W，项目要求冷却液温升 6 °C。设计流量为模组 3.512 L/min、GPU 核心 910 W 对应 2.283 L/min、HBM 每颗 43.7 W 对应 0.1096 L/min、Grace 0.753 L/min、整柜约 351.2 L/min。0.50 mm 孔速 0.897 m/s。壳–进液热阻没有按 PG25 和新流量重算。整板压降按流量平方外推落在 14–24 kPa，可能超过 20 kPa，尚无结论。

Grace CP-GRACE-MC-01（来源：Grace v1.0 §0、§5；v1.1 §3）：300 W 含内存（CPU 260 W + 内存 40 W），两层铜，48 条 0.40×1.20 mm 沿 Y 交错槽，200×120×8 mm 候选外形。水 0.55 L/min 时支路约 10 kPa；PG25 0.8 L/min 时现有 4×1.04 mm 孔板加 CPU 通道约 22.9 kPa，高于 20 kPa，孔板要重配。壳–进液目标 < 0.080 °C/W（E1 + TIM 余量）。

CFD（来源：`cycle-20260926/03_单孔CFD仿真分析.html`；`memory/semantic/cfd-uc01b.md`；12 格契合性报告）：

| 算例 | 网格 | 迭代 | ΔP | T_TIM 底 | R(TIM–in) | 备注 |
|---|---|---|---|---|---|---|
| UC-01b bc216 | 2,115,436 HEXA | 421 收敛 | 1091.51 Pa | 342.096 K | — | D 0.40 圆孔 |
| UC-01b m425 | 4,259,680 HEXA | 380 收敛 | 1087.09 Pa | 341.385 K | 0.03134 °C/W | R_conv 0.01493 |
| UC-01b 12 格带 | 28,005,504 HEXA | 600 二阶 | 1099.99 Pa | 342.049 K | 0.03208 °C/W | 能量比 1.0368；ΔP 比一维孔口高 27.6% |

### 2.4 已有结论

- 选型：分区杂交（GPU 射流 + 短槽，HBM 无喷嘴 + 限速，隔离肋）加权 4.50，排第一（v2.0 §5.1；`02_DR1_方案权衡.xlsx` 复算差约 0.05，名次不变）。
- 水力余量大，热设计没有余量。正确方向是“用压降换换热”（v2.0 §0.1）。
- Re_D < 2000，Martin 1977 不采用；保证值用短槽层流 + 驻点核（v2.0 §9.4；`oned.py` 自动判定）。
- 最优先杠杆：TIM2 升级到 ≤ 0.004 °C/W，孔径 0.50→0.40 mm（v2.0 §9.12）。
- 单胞 CFD 的 0.0313 °C/W 比一维下限 0.0326 低约 4%（`cycle-20260926/03` 原文写“落在下限与上限之间”，与数字不符，见 G-12），证据等级是 E2，网格孔径是 D0.40，不是整板保证。
- 工艺：机加 + 真空钎焊，整板增材不作为出货基线（v2.0 §6.1；专利 v1.4 §3.7）。

### 2.5 缺口与不一致清单

| 编号 | 缺口 / 不一致 | 来源 | 影响 | 建议处理 |
|---|---|---|---|---|
| G-01 | OEM 输入缺失：封装图、功率图、单板流量与压降窗、UQD、压装力 | v2.0 §13 C-01～C-04；`01_DR0_输入追溯.xlsx` | DR0 只能“有条件通过” | 输入追溯矩阵加责任人与日期；先用 TTV 打通物理可行性 |
| G-02 | 设计点基准漂移：v2.0 水 / 1100 W / 2.0 L/min 与 v2.1 PG25 / 1400 W / 6 °C / 3.512 L/min 并存 | v2.0 §0；v2.1 §1、§8 | 热阻、压降结论不在同一基准 | 用设计点注册表并存三组 DP，用户拍板主基准（§13 Q1） |
| G-03 | PG25 物性两套：`model.py` PG25_40（μ 1.15e-3，k 0.452）与 HBM 1D v1.0 的 DOWFROST LC 25（ρ 1022.5，μ 1.58e-3，k 0.476） | `design/calc/model.py`；`design/cfd_HBM/HBM微通道冷板_1D设计报告_v1.0` | 粘度差约 37%，Re、ΔP、h 都会偏 | 物性库带来源和温度曲线，选定一套（§13 Q2） |
| G-04 | HBM 截面与流路多版本：v2.0 16×0.60×1.50 横流；09-28 修订 7×0.80×2.00 交错；v2.1 7×0.80×2.00 每颗中心进液；HBM 1D v1.0 方案 D 11×0.45×2.00 | v2.0 修订节；v2.1 §0、§4；HBM 1D v1.0；`memory/semantic/b300-design-lock.md` | CAD、CFD、报告可能各用一版 | 注册表登记为 HBM-A/B/C/D 并标“当前采用” |
| G-05 | 孔径 D0.50（model.py、CAD、v2.1 采用）与 D0.40（CFD 网格）并存 | `01_DR0` IN-13；`cycle-20260926/index.html` | 1D 与 CFD 不能直接对比 | C11 工况补 D0.50 网格，或决议改 0.40 |
| G-06 | CAD 内核只有单一 `jets.pitch`，建不出 v2 216 孔；asm_0921 是 12.5 mm 三层；没有水嘴、UQD、歧管；Grace 未接规则门，STEP 仍是同向模型 | `knowledge/cad-kernel-gap.md`；Grace v1.0 §8 | ⑥ 图纸与⑤流体域都卡在这里 | 实施 S10–S13 |
| G-07 | CFD 判据未关：V4 Martin 锚定未做；三套网格无关性未做；12 格能量比 1.0368（判据 < 1%）；整板/半板未做，Q2 流量一致性、Q4 歧管压降未知；C01–C12 未开；v2.0 §10.2 工具仍写“待定” | v2.0 §10；12 格契合性报告；CFD-AI 评估 v1.0 | DR3 不能评审 | 实施 S14–S19 |
| G-08 | PG25 下压降可能超限：B300 整板外推 14–24 kPa；Grace 支路 22.9 kPa | v2.1 §3；Grace v1.1 §3 | 托盘配平未闭合 | 实施 S08 水力网络 |
| G-09 | 机械只做了解析板条；没有 FEA、完整 GD&T、焊接符号；压装力未定 | v2.0 §6.3、§8.11 | DR3 闸门不完整 | 实施 S20–S22 |
| G-10 | ⑦ 试验未开始；DR4 门表实测列为空 | v2.0 §11；`04_DR3_仿真图纸与试验门.xlsx` | 无 E4 锚点 | 实施 S23–S26 |
| G-11 | FTO 仅初筛 | v2.0 C-10；专利 v1.4 §6.2 | 量产风险 | 列为外部专业服务，AI 只做权利要求对照草稿 |
| G-12 | 数据治理：`calc_1d_out.txt` 仍是 128 孔旧口径；CFD-AI 评估 v1.0 写“本机无 ANSYS”已过时；DR2 xlsx 公式格没有缓存值，不经 Excel 重算读不出数；`oned.py`/`zones.py` 没有回归测试；记忆索引引用的 `uc01b-lessmesh.md` 中文损坏；`cycle-20260926/03` 把 0.0313 °C/W 写成“落在一维区间之间”，实际低于下限 0.0326 | 各文件 | 容易引用旧数 | 实施 S02、S04；旧文件加“已取代”标签 |
| G-13 | 平台能力缺：无数字孪生、无 AI 在环控制、无试验数据管理；MATLAB、SolidWorks、FreeCAD 未探测到；`cad/.venv` 无 PyAnsys、gmsh；`practice01_0926/` 整个目录在 git 中尚未跟踪 | 本机探测；`git status` | 工具选型受限 | §13 决策；S01 环境盘点 |
| G-14 | 命名：注册 id 为 `cp-design`，模块目录名为 `practice01_0926`，与平台“命名零漂移”约定不一致 | `platform/registry.json`；`platform/CLAUDE.md` §1 | 自动发现可用，但偏离约定 | 本期不改，S33 评审时一并处理 |

## 3 需求分析

### 3.1 角色与使用场景

| 角色 | 典型场景 | 平台要提供的 |
|---|---|---|
| 热设计负责人（用户） | 改孔径、改流量后马上看热阻和压降；签 DR 闸门 | 一条指令出 1D 计算书；闸门包；差异对比 |
| 仿真工程师 | 批量跑工况矩阵、查残差、出合格云图 | journal 模板、作业队列、日志解析、取图技能 |
| 结构 / 工艺工程师 | 尺寸链、公差、承压、出图 | 规则门、FEA 模板、DXF/PDF 草图、BOM |
| 试验工程师 | TTV 台架、流阻曲线、红外、氦检数据入库 | 试验大纲、数据模板、偏差自动计算 |
| 系统 / 运维工程师 | 托盘与机柜流量分配、孪生回放 | 水力网络、ROM、FMU |
| AI 智能体 | 按技能执行、写记忆、提醒闸门 | MCP 工具、技能、记忆治理 |

### 3.2 功能需求

| 编号 | 功能 | 说明 | 优先级 |
|---|---|---|---|
| FR-01 | 设计点注册表 | DP 的功率、工质、流量、几何、目标值统一放在 yaml，带来源、日期、置信度、状态 | P0 |
| FR-02 | 输入追溯与冲突检测 | 自动比对报告、xlsx、yaml、CAD 参数，列冲突 | P0 |
| FR-03 | 一维热–水力计算 | GPU 射流、HBM、Grace、能量平衡、热阻链、压降预算；关联式按适用域自动切换 | P0 |
| FR-04 | 敏感性、DOE、差距闭合 | 孔径、流量、TIM2、槽深、工质扫描；龙卷风图；所需 h | P0 |
| FR-05 | 水力网络 | 板内静压箱 + 托盘 4 GPU + 2 Grace 并联，孔板配平 | P1 |
| FR-06 | 参数化 CAD | 各向异性节距、HBM 多方案、Grace、水嘴/UQD 占位；规则门；STEP 回读核对 | P0 |
| FR-07 | CFD 前处理 | 流体域抽取、命名面、网格模板（ICEM 单胞 / Fluent Meshing 整板） | P1 |
| FR-08 | CFD 作业与后处理 | journal/PyFluent 批处理、显存与核数检查、残差与监视量解析、结果入账 | P1 |
| FR-09 | FEA | 3 bar 承压、压装力、热应力、焊后平面度 | P1 |
| FR-10 | 工程图 | 2D 视图、剖面、孔位表、BOM、尺寸链表，候选图与正式图分开 | P1 |
| FR-11 | 试验管理 | 大纲、台架 BOM、传感器不确定度、数据模板、导入校验 | P1 |
| FR-12 | V&V | V1–V5 对比，偏差 > 15% 自动开 R2 回路，参数反标定 | P1 |
| FR-13 | ROM / 数字孪生 | DOE→代理模型；动态热网络；FMU 导出；离线回放 | P2 |
| FR-14 | AI 在环控制 | 仿真内 MPC/RL，安全监督层，人工确认才能下发 | P2 |
| FR-15 | 报告生成 | md/html 计算书、闸门包、单文件离线 HTML | P0 |
| FR-16 | 知识与记忆 | 技能沉淀、记忆写入与过期、RAG 回灌 | P0 |

### 3.3 非功能需求

| 编号 | 要求 | 指标 |
|---|---|---|
| NFR-01 可复算 | 每个数字能追到脚本、输入和版本 | 报告页脚写数值源；重跑结果一致 |
| NFR-02 可回归 | 改代码后一维与规则门全部自测 | pytest 全过；黄金数据偏差 ≤ 0.5% |
| NFR-03 可审计 | 所有运行有 `runs/<时间戳>/` 目录，含参数副本、日志、产物、哈希 | 100% |
| NFR-04 不覆盖冻结件 | `cad/params/cp_b300_jm01.yaml`、已发 STEP、已发报告只读 | 规则门拒绝写入 |
| NFR-05 离线可用 | 报告单文件、无外部依赖；核心计算不依赖联网 | 100% |
| NFR-06 数据保密 | OEM 资料与几何不出本机或内网；云模型只见脱敏摘要 | 按 §10.1 分级 |
| NFR-07 资源安全 | GPU 求解前检查显存（2.2 GB/百万单元），超线只用 CPU | 不卡死桌面 |
| NFR-08 可移植 | 路径、版本、许可证服务器都放配置，不写死 | 换机只改配置 |
| NFR-09 性能 | 一维单点 < 1 s；1000 点 DOE < 1 min；CAD 整板 < 10 min | 达标 |
| NFR-10 可解释 | 关联式写明适用域；越域给警告而不是静默外推 | 100% |

### 3.4 接口需求

| 编号 | 接口 | 形式 | 现状 |
|---|---|---|---|
| IF-01 | 智能体 ↔ 工具 | MCP stdio（`cp-design`、`user-matlab`、`dify-rag`） | 前两者已登记，未验证 MATLAB |
| IF-02 | 人 ↔ 平台 | 设计台 HTTP `127.0.0.1:8765`；Cursor/Claude 对话 | 已有 |
| IF-03 | 1D ↔ CAD | 设计点 yaml → `cad/coldplate` Spec | 部分，缺 v2 字段 |
| IF-04 | CAD ↔ CFD | STEP（AP214/AP242）+ 命名面清单 json | 部分 |
| IF-05 | CFD ↔ 平台 | journal、`.cas.h5/.dat.h5`、transcript、surface report CSV | 部分 |
| IF-06 | FEA ↔ 平台 | PyMechanical/MAPDL 脚本、结果 CSV | 无 |
| IF-07 | 试验 ↔ 平台 | CSV 模板（时间戳、通道、单位、校准号） | 无 |
| IF-08 | 孪生 ↔ 外部 | FMU（FMI 2.0/3.0）、ROM 文件、时序 CSV | 无 |
| IF-09 | 平台 ↔ git | `git-release` 技能，提交信息规范，真实 push 由人执行 | 已有 |
| IF-10 | 平台 ↔ Dify | `librarian` → `rag-query` | 已有 |

### 3.5 约束

- 平台约定：先读 `platform/CLAUDE.md`；模块自包含；`.claude/agents/<id>.md` 是薄加载器；派生子智能体限 1 层且只有 `quant-research` 能派生，所以本项目不派生子智能体，新增能力要么是技能，要么是新注册智能体。
- 三道人工闸门（技能安装、记忆继承、实盘/资金动作），以及每个 DR 闸门由人签字。
- 冻结口径：v2.0 文字、v1.0 参数化内核、asm_0921 实测、UC-01b、Grace 概念五套数字各自归位（`agent.md` 职责第 2 条）。
- 本机硬件：i9-14900KF 24 核、128 GB、RTX 4090 24 GB（桌面占用约 2.2 GB）。整板 30–80 M 单元共轭不适合在本机过夜批量跑（CFD-AI 评估 v1.0 §2.1）。
- 软件：Ansys 2026 R1 已装，许可范围待核；MATLAB、SolidWorks 未探测到。
- 信息：NVIDIA/OEM 未公开封装图、功率图；所有几何是候选。
- PowerShell 会吞 `&` 和括号，多步命令写成脚本文件（`memory/semantic/environment.md`）。

## 4 总体技术架构

### 4.1 分层架构

<!-- fig:arch -->
```text
┌──────────────────────── 平台层 platform/ ────────────────────────┐
│ CLAUDE.md · registry.json · router.config.json · shared/skills    │
│ shared/memory · hooks（Stop Hook、memory_gc）· 三道人工闸门        │
└───────────────────────────────────────────────────────────────────┘
 交互层   设计台 UI（:8765） | Cursor/Claude 对话 | 单文件 HTML 报告
 智能体层 orchestrator → cp-design（主责） + ai-matlab + librarian + thermal-management
          cp-design 角色技能：需求/1D/CAD/CFD/FEA/出图/试验/V&V/孪生
 工具层   MCP cp-design（现有 8 工具 + 规划工具） | MCP user-matlab | MCP dify-rag
          适配器：PyFluent/PyMechanical/PyDPF/PyTwin | build123d/SpaceClaim/FreeCAD | OpenFOAM/gmsh
 求解层   Fluent · ICEM · Fluent Meshing · Mechanical · optiSLang · Twin Builder/TwinAI
          MATLAB/Simulink/Simscape（待确认） | OCC/build123d | OpenFOAM/CalculiX（备选）
 数据层   git 文本资产（yaml/json/md/py）| runs/<时间戳>/（大文件不入库 + 清单哈希）
          memory/ · skills/ · Dify RAG · 试验数据 · 物性/关联式库
```

图 4-1 · 平台分层架构。左侧平台层贯穿各层；AI 只通过 MCP 和文件接口驱动求解器。

各层职责：

| 层 | 职责 | 关键设计 |
|---|---|---|
| 平台层 | 宪法、注册表、路由、共享技能与记忆、闸门 | 复用现有，不另造 |
| 交互层 | 人看结果、改参数、签闸门 | 设计台继续当 HTTP API 的壳（`软件界面方案.md`） |
| 智能体层 | 拆解、调用工具、写报告和记忆 | `cp-design` 主责，按技能分角色 |
| 工具层 | 把软件变成可调用、可校验的函数 | 每个工具都有输入校验、`confirm` 门、`runs/` 落盘 |
| 求解层 | 真正算数 | 只经脚本和文件驱动，不靠 GUI 点选（截图只作 QA） |
| 数据层 | 单一来源、版本、审计 | 文本入 git；cas/dat/msh 不入 git，用清单和哈希追踪 |

### 4.2 多智能体分工

平台约定只有 `quant-research` 能派生子智能体，所以本项目前期**不新增注册智能体**，而是在 `cp-design` 内按角色拆技能。到 S33 再评审是否把 CAE、孪生拆成独立智能体（新增要建模块、薄加载器并登记 `registry.json`，由人确认）。

| 角色 | 承担者 | 主要技能（现有 / 规划） | 调用的工具 |
|---|---|---|---|
| 编排 | `orchestrator` | 拆解、路由、汇总 | Task |
| 冷板设计主责 | `cp-design` | `design-loop`（现有） | MCP cp-design |
| 需求与输入 | `cp-design` | `input-trace`（规划） | 设计点注册表、冲突检测 |
| 一维计算 | `cp-design` | `oned-calc`（规划） | `oned_*`、`hydro_network` |
| 系统 / 动态仿真 | `ai-matlab` | 环境内置 `matlab-*` | MCP user-matlab |
| CAD | `cp-design` | `cad-loop`（现有） | `cad_inspect`、`cad_build` |
| CFD | `cp-design` | `cfd-loop`、`fluent-gui-capture`（现有）；`cfd-batch`（规划） | `cfd_job_*` |
| FEA 与出图 | `cp-design` | `fea-loop`、`drawing-loop`（规划） | `fea_*`、`drawing_*` |
| 试验与 V&V | `cp-design` | `vv-loop`（规划） | `test_import`、`vv_compare` |
| 孪生与控制 | `cp-design`（后期可拆） | `twin-rom`、`control-sim`（规划） | `rom_*`、FMU |
| 文献与专利 | `librarian` | `rag-query`（共享） | MCP dify-rag |
| 行业与供应链 | `thermal-management` | — | WebSearch |

### 4.3 MCP 与工具接入

现有 `cp-design` MCP 的 8 个工具保留不变，按阶段新增。新增工具都遵循三条：先校验后执行；会写文件或占用求解器的工具必须 `confirm=true`；产物只写 `runs/<时间戳>/`。

| 工具（规划） | 阶段 | 作用 | 底层 |
|---|---|---|---|
| `dp_list` / `dp_diff` | P1 | 列设计点、比对两套设计点或报告数 | yaml + 解析器 |
| `oned_report` | P1 | 生成一维计算书 md/html/json | `oned` 包 |
| `oned_sweep` | P1 | DOE、龙卷风、差距闭合 | numpy |
| `hydro_network` | P1 | 板内 + 托盘水力网络、孔板配平 | scipy |
| `cad_inspect` / `cad_build`（扩展） | P2 | 支持 `pitch_x/pitch_y`、HBM 方案、Grace | `cad/coldplate` |
| `fluid_extract` | P2 | 抽流体域、命名面 | build123d / SpaceClaim 脚本 |
| `cfd_preflight` | P3 | 网格量、显存、许可、核数检查 | 本机探测 |
| `cfd_job_submit` / `cfd_job_status` | P3 | 提交 journal/PyFluent 作业、查状态 | 子进程 / PyFluent |
| `cfd_extract` | P3 | 解析 transcript、CSV，算 R、ΔP、能量比 | 解析器 |
| `fea_run` | P4 | 承压、压装、热应力 | PyMechanical / MAPDL |
| `drawing_build` | P4 | DXF/PDF 候选图 | ezdxf / FreeCAD TechDraw |
| `test_import` | P5 | 试验 CSV 校验入库 | pandas |
| `vv_compare` | P5 | V1–V5 偏差、R2 回路触发 | 解析器 |
| `rom_build` / `rom_eval` | P6 | 代理模型训练与评估 | scikit-learn / Twin Builder |

外部 MCP 与适配器：

| 接入 | 方式 | 状态 | 说明 |
|---|---|---|---|
| MATLAB/Simulink | 已登记 `user-matlab`（`@mathworks/mcp-matlab`），由 `ai-matlab` 使用 | 本机未探测到 MATLAB | 有授权才启用 |
| Ansys | 不另起 MCP，在 `cp-design` 内用 PyAnsys 适配器 | Fluent 已在本机运行；PyAnsys 未装 | 安装第三方包按供应链确认 |
| CAD | build123d（现有）；SpaceClaim `/RunScript`（现有）；FreeCAD 命令行；SolidWorks 宏（内核已有后端） | FreeCAD、SolidWorks 未探测到 | 见 §4.4.2 |
| Onshape | REST API | 未接 | 云端，涉及保密，默认不用 |
| OpenFOAM | WSL2 或 Docker | 未装 | 备选与交叉校核 |

### 4.4 选型对比与推荐

评分 1–5，5 最好。权重：本机可用性 25%、自动化/脚本能力 25%、工程可信度 20%、成本与授权 15%、数据保密 15%。

#### 4.4.1 一维与系统仿真

| 方案 | 可用性 | 自动化 | 可信度 | 成本 | 保密 | 加权 | 适合做什么 |
|---|---|---|---|---|---|---|---|
| Python 自建（model.py + oned + scipy） | 5 | 5 | 4 | 5 | 5 | **4.80** | 关联式、预算、DOE、水力网络、回归 |
| MATLAB / Simulink / Simscape Fluids & Thermal | 2 | 4 | 5 | 2 | 5 | 3.55 | 动态热网络、控制设计、MPC 工具箱 |
| Modelica（OpenModelica + 开源热流库） | 3 | 4 | 4 | 5 | 5 | 4.05 | 开源动态系统，可导 FMU |
| Ansys Twin Builder | 3 | 3 | 4 | 3 | 5 | 3.50 | ROM 集成、孪生部署 |

推荐：**Python 为主**（一维与水力网络全部在 Python，作为唯一数值源）；动态和控制在 MATLAB 有授权时交 `ai-matlab` 做 Simscape 对照，没有授权就用 Modelica 或 Python（scipy ODE）。两者都只消费设计点注册表，不另存一套参数。

#### 4.4.2 CAD 概念设计与出图

| 方案 | 可用性 | 自动化 | 可信度 | 成本 | 保密 | 加权 | 备注 |
|---|---|---|---|---|---|---|---|
| build123d（OCC，现有内核） | 5 | 5 | 4 | 5 | 5 | **4.80** | 已有规则门和后端；共面布尔有段错误，需过切 |
| CadQuery | 4 | 5 | 4 | 5 | 5 | 4.55 | 同为 OCC，不必换 |
| SpaceClaim / Discovery 脚本 | 5 | 4 | 4 | 4 | 5 | 4.45 | 已用于上色和托盘示意；适合 CFD 前处理 |
| FreeCAD（TechDraw 出图） | 3 | 3 | 3 | 5 | 5 | 3.60 | 开源出 2D 图，需安装 |
| SolidWorks API | 1 | 4 | 5 | 2 | 5 | 3.20 | 未探测到；内核已有宏后端 |
| Siemens NX | 1 | 3 | 5 | 2 | 5 | 2.95 | asm_0921 原始来源 |
| Onshape | 4 | 4 | 4 | 3 | 1 | 3.35 | 云端，OEM 数据不宜上传 |

推荐：**build123d 继续做参数化主内核**（先补 `pitch_x/pitch_y`）；**SpaceClaim 做 CFD 前处理**（抽流体域、命名面、修面）；**2D 候选图用 ezdxf（现有 DXF 后端）**，FreeCAD TechDraw 作为增强；**正式投产图由人在公司 CAD（SolidWorks 或 NX）定稿**，AI 只出宏和尺寸表。

#### 4.4.3 三维 CFD / 传热

| 方案 | 可用性 | 自动化 | 可信度 | 成本 | 保密 | 加权 | 备注 |
|---|---|---|---|---|---|---|---|
| Ansys Fluent（journal + PyFluent） | 5 | 4 | 5 | 3 | 5 | **4.45** | 已在用，已有收敛算例与取图技能 |
| Ansys Icepak | 3 | 3 | 4 | 3 | 5 | 3.50 | 托盘/机柜级电子散热；对 0.5 mm 孔常用降阶，不适合射流驻点 |
| Ansys CFX | 4 | 3 | 4 | 3 | 5 | 3.65 | 已装，无必要再引入 |
| OpenFOAM（chtMultiRegionFoam） | 2 | 5 | 4 | 5 | 5 | 4.05 | 开源，适合交叉校核和免许可扫描 |
| Simcenter STAR-CCM+ / FloTHERM | 1 | 3 | 5 | 1 | 5 | 2.80 | 未装 |

推荐：**Fluent 为主力**（v2.0 §10.2 的能力要求：共轭、低 Re/转捩、高纵横比网格、逐孔流量、批处理，Fluent 都满足），自动化以 **journal 为底线、PyFluent 为便利层**（CFD-AI 评估 v1.0 §4 已定此优先级）；**Icepak 留给托盘级**；**OpenFOAM 作开源校核**（V1 代码验证、单胞交叉对比），不作交付求解器，除非项目改口。

#### 4.4.4 网格

| 方案 | 适用 | 推荐 |
|---|---|---|
| ICEM CFD hex（replay） | 单胞、12 格带等规则几何，已有黄金 replay | 单胞与局部带继续用 |
| Fluent Meshing 水密流程（poly-hexcore） | 整板、半板、含静压箱与歧管 | 整板首选 |
| PyPrimeMesh | 网格脚本化 | 视许可，作为 Fluent Meshing 的脚本层 |
| gmsh / snappyHexMesh | OpenFOAM 路线 | 仅备选 |

#### 4.4.5 结构 FEA

推荐 **Ansys Mechanical（PyMechanical / PyMAPDL）** 做 3 bar 承压、300–500 N 压装、焊后热应力与平面度；**CalculiX** 作开源备选。v2.0 §6.3 的解析板条保留为一维对照。

#### 4.4.6 优化与 DOE

推荐 **Python（scipy、optuna）+ 一维模型**做大规模筛选；**optiSLang**（已装）在 CFD 级 DOE 和稳健性分析时使用。原则：一维筛到 3–5 个候选，再上 CFD。

#### 4.4.7 数字孪生与控制

推荐 **Python ROM（scikit-learn 高斯过程 / 多项式）+ FMU（FMPy）** 打底；有授权时用 **Twin Builder / TwinAI** 做 ROM 集成与部署；控制器设计用 **MATLAB MPC 工具箱**（若可用）或 **CasADi / do-mpc**。

### 4.5 本机算力与授权约束

| 资源 | 现状 | 规划中的用法 |
|---|---|---|
| CPU 24 核 / 128 GB | 已测 | 单胞、12 格带、单 die 阵列；整板需评估 HPC |
| RTX 4090 24 GB | 空闲约 21.5 GB | `-t1 -gpu` 不超过约 900 万单元；`-t4 -gpu` 不超过约 240 万；超线只用 CPU（`skills/cfd-loop`） |
| Ansys 2026 R1 | 已装，Fluent 已运行 | 许可模块（Mechanical、optiSLang、Twin Builder、HPC 核数）由 S01 核实 |
| MATLAB | 未探测到 | §13 Q4 |
| SolidWorks / NX | 未探测到 | §13 Q5 |

## 5 设计流程 ①–⑦ 与 AI 的结合

### 5.0 流程总图

<!-- fig:flow -->
```text
① 需求与输入 ─► ② 概念与选型 ─► ③ 性能设计 ─► ④ 一维计算 ─► ⑤ 三维仿真 ─► ⑥ 机械与图纸 ─► ⑦ 样件与试验
   DR0 输入冻结   DR1 方案选定    DR2 性能基线   DR2 闸门      DR3 仿真评审   DR3 闸门        DR4 送样放行
   [AI] RAG抽取    [AI] 权衡复算   [AI] 预算分配  [AI] 1D回归    [AI] 批处理    [AI] FEA/出图   [AI] V&V
回路 R1：仿真不达标 → 回 ③/④ 改几何（孔径、阵列密度、TIM2）
回路 R2：试验与仿真偏差 > 15% → 修正模型并回 ③（V&V 闭环）
```

图 5-1 · 门控流程、AI 结合点与两条强制回路。①–④ 已有报告，⑤ 只有单胞级，⑥ 是候选图纸，⑦ 未开始。

每一步的写法统一为：输入 → AI 动作 → 工具 → 输出 → 验收标准 → 现状与缺口。

### 5.1 ① 需求与输入（DR0 输入冻结）

| 项 | 内容 |
|---|---|
| 输入 | 芯片规格与热包络（B300 1100/1400 W、Grace 300 W）、机柜水力表（Lenovo LP2357 表 27）、接口与标准（OCP、ASHRAE、UQD）、项目要求（PG25、6 °C 温升、孔速 ≤ 2.0 m/s、近壁 ≤ 0.80 m/s） |
| AI 动作 | 经 `librarian` 检索公开资料并抽取数字，每条带来源、日期、置信度；生成输入追溯矩阵（IN-*）与假设登记册（AS-*）；比对报告、xlsx、yaml 找冲突；为缺失项生成索取清单 |
| 工具 | `rag-query`、`dp_list`、`dp_diff`、设计点注册表 |
| 输出 | `designpoints/*.yaml`、输入追溯矩阵、假设登记册、冲突清单、OEM 索取清单 |
| 验收 | 每个“缺失”项都有责任人和计划日期；冲突清单为零或每项都有处理决议；人签 DR0 |
| 现状 | v2.0 §3 与 `01_DR0_输入追溯.xlsx` 已有矩阵，含 6 项缺失；G-01～G-04 未闭合 |

### 5.2 ② 概念与选型（DR1 方案选定）

| 项 | 内容 |
|---|---|
| 输入 | 技术调查 v1.3 五条路线；专利 v1.4 方案 A/B/C 与雷区；DR0 输入 |
| AI 动作 | 复算加权矩阵并做权重敏感性（权重 ±20% 时名次是否翻转）；分区策略说明；对照 WO2026103052A1 等已公开权利要求，列出必要技术特征的差异点草稿 |
| 工具 | `rag-query`；Python 矩阵脚本 |
| 输出 | 方案决策矩阵、敏感性结果、分区策略、FTO 初筛对照表（草稿） |
| 验收 | 权重有量化依据；敏感性下第一名稳定；FTO 无红灯或红灯已有规避；人签 DR1 |
| 现状 | 已完成（分区杂交 4.50）；FTO 只是初筛（G-11） |

### 5.3 ③ 性能设计（DR2 性能基线）

| 项 | 内容 |
|---|---|
| 输入 | DR1 方案；结温包络；Rpkg、TIM2 假设 |
| AI 动作 | 从 Tj 倒推热阻预算并分配到 TIM2、铜壁、对流；给流道参数初值（D、Sx、Sy、H/D、槽宽深、HBM 截面）；流量与压降预算；每个参数标注所在窗口和越窗风险 |
| 工具 | `oned_design`、`oned_sweep` |
| 输出 | 热阻预算表、参数初值表、流量/压降预算 |
| 验收 | 预算闭合（各段加和等于目标）；每个参数在文献窗内或写明越窗理由 |
| 现状 | v2.0 §5 完成；PG25/1400 W 基准下的预算尚未重做（G-02） |

### 5.4 ④ 一维计算（DR2 闸门）

| 项 | 内容 |
|---|---|
| 输入 | ③ 的参数；设计点注册表 |
| AI 动作 | 运行一维工具出计算书；三模型上下界；PG25 复算；孔径、流量、TIM2、槽深敏感性；差距闭合矩阵（所需 h）；回归测试；水力网络（托盘配平） |
| 工具 | `oned_report`、`oned_sweep`、`hydro_network`；可选 `ai-matlab` 对照 |
| 输出 | 一维计算书（md/html/json）、敏感性图、差距闭合表、回归报告 |
| 验收 | 回归全过；能量平衡自洽；结论分“通过 / 不判定 / 不通过”三档；给出最优先杠杆；人签 DR2 |
| 现状 | v2.0 §9 完成，有条件通过（区间跨目标线）；缺自动回归、缺 PG25 热阻、缺托盘水力（G-02、G-08、G-12） |

### 5.5 ⑤ 三维仿真（DR3 仿真评审）

| 项 | 内容 |
|---|---|
| 输入 | 候选几何（STEP + 命名面）；v2.0 §10 需求规格（Q1–Q8、C01–C12、V1–V5） |
| AI 动作 | 写 journal / PyFluent 脚本；预检网格量与显存；提交与监控作业；解析残差、监视量、能量与质量守恒；网格无关性；V4 锚定；整理逐孔流量与压力分段；按 `fluent-gui-capture` 取报告图；与一维对表 |
| 工具 | `cfd_preflight`、`cfd_job_submit`、`cfd_job_status`、`cfd_extract`；Fluent、ICEM、Fluent Meshing |
| 输出 | CFD 报告、网格无关性报告、工况矩阵汇总、一维修正建议、几何修改建议 |
| 验收 | 残差连续/动量 < 1e-4、能量 < 1e-6；能量偏差 < 1%；质量偏差 < 0.1%；相邻网格 R 与 ΔP 差 < 3%；V4 对 Martin < 15%；R 与 ΔP 落在目标内，否则触发 R1；人签 DR3 仿真评审 |
| 现状 | 单胞与 12 格带已有收敛场；V4、无关性、整板未做；12 格能量比 1.0368 未达 1%（G-05、G-07） |

### 5.6 ⑥ 机械与图纸（DR3 闸门）

| 项 | 内容 |
|---|---|
| 输入 | 冻结候选几何；工艺路线；压装力与 UQD（待 ICD） |
| AI 动作 | 层叠与尺寸链校核（名义 + 统计）；公差分配；承压、压装、热应力 FEA；出 2D/3D/爆炸图候选与 BOM；图纸检查清单（标题栏、剖切、孔位表、GD&T、焊接符号） |
| 工具 | `cad_build`、`fea_run`、`drawing_build`；Mechanical；SpaceClaim |
| 输出 | FEA 报告、公差与尺寸链表、候选图纸包（DXF/PDF/STEP）、BOM |
| 验收 | 尺寸链全部闭合；3 bar 下安全系数 ≥ 2、平面度变化 ≤ 0.02 mm；图纸检查清单全过；人签 DR3 闸门 |
| 现状 | v2.0 §6、§8 有候选图与解析校核；无 FEA、无正式 GD&T（G-06、G-09） |

### 5.7 ⑦ 样件与试验（DR4 送样放行）

| 项 | 内容 |
|---|---|
| 输入 | DR3 图纸包；试验大纲 v2.0 §11 |
| AI 动作 | 写试验大纲与台架 BOM；不确定度分析；数据模板；导入校验；V&V 对比；偏差 > 15% 时开 R2 工单并给反标定建议 |
| 工具 | `test_import`、`vv_compare` |
| 输出 | 试验报告、V&V 报告、出厂三曲线（流阻、热阻、红外）、DR4 放行包 |
| 验收 | TTV Rθ,c-in < 0.028 °C/W（DP-A）；两 die 中心温差 ≤ 5 K；2.0 L/min 下 ΔP ≤ 18 kPa；100% 氦检；分区流量 80:20 ±10%；人签 DR4 |
| 现状 | 未开始；DR4 门表实测列为空（G-10） |

### 5.8 DR 闸门汇总

| 闸门 | 放行条件（摘要） | AI 准备的闸门包 | 签字 | 现状 |
|---|---|---|---|---|
| DR0 输入冻结 | 缺失项有责任人和日期；冲突清零 | 追溯矩阵、假设登记册、冲突清单 | 用户 | 有条件（6 项缺失） |
| DR1 方案选定 | 权衡矩阵有量化权重；FTO 无红灯 | 矩阵 + 敏感性 + FTO 对照 | 用户 | 已完成 |
| DR2 性能基线 | 预算闭合；一维可复算；有杠杆 | 计算书 + 回归报告 + 差距闭合 | 用户 | 有条件（区间跨线） |
| DR3 仿真评审 | 网格无关、守恒、V4、R 与 ΔP 达标 | CFD 报告 + 无关性 + V&V(V1–V4) | 用户 + 仿真负责人 | 未完成 |
| DR3 闸门 | 尺寸链闭合；FEA 通过；图纸清单过 | FEA + 图纸包 + BOM | 用户 + 结构/工艺 | 未完成 |
| DR4 送样放行 | TTV、氦检、流阻曲线达标 | 试验报告 + V5 + 三曲线 | 用户 | 未开始 |

### 5.9 两条强制迭代回路

| 回路 | 触发条件 | 回到 | 杠杆（按优先级，来自 v2.0 §4.2） | AI 的动作 |
|---|---|---|---|---|
| R1 仿真回路 | CFD 得到的 Rθ,c-in 超目标；或 ΔP > 20 kPa；或分区流量偏差 > ±10% | ③ / ④ | 孔径 0.50→0.40/0.35；TIM2 ≤ 0.004；流量 2.0→2.2/2.4；阵列加密；槽深 1.5→1.0 | 一维筛出 3–5 个候选，给 CAD 参数 overlay，人确认后再上 CFD |
| R2 验证回路 | TTV 实测与 CFD 偏差 > 15% | ③（并修正 ④ 的关联式与系数） | 实测反标定 h；复核 TIM2 压力与厚度；复核孔一致性与堵塞 | 偏差分解、反标定、更新模型版本和 semantic 记忆 |

回路每触发一次，都要留一条 episodic 记忆（触发量、杠杆、结果），这是后面训练 ROM 和总结设计规律的原始数据。

## 6 一维计算工具设计

### 6.1 定位与原则

- **唯一数值源**：数值只来自 `design/calc/model.py` 与其扩展，报告、xlsx、UI、MCP 都调用它，不另抄数字（v2.0 §4.3 的原则推广到全平台）。
- **适用域门控**：每个关联式带适用域，越域时自动降级并给出警告（已在 `oned.py` 实现 Martin 门控）。
- **证据等级标注**：输出里每个结论带 E1 标签和“保证值 / 对照值”身份。
- **不改冻结件**：现有 `oned.py`、`zones.py`、`model.py` 先用回归测试锁住，再逐步重构；重构期间旧接口保持兼容。

### 6.2 模块划分

| 模块 | 内容 | 现有来源 |
|---|---|---|
| `props` | 物性库：水、PG25（两套来源）、铜；温度曲线 | `model.py` WATER40、PG25_40；HBM 1D v1.0 |
| `correlations` | Martin 1977、驻点、Shah & London、层流发展段、肋效率、孔口 K | `model.py` |
| `zones.gpu_jet` | 射流区热阻、压降、Martin 门控、孔径杠杆 | `oned.py` |
| `zones.hbm` | HBM 多方案（A 横流 / B 交错 / C 中心进液 7 槽 / D 11 槽） | `zones.py`、HBM 1D v1.0 |
| `zones.grace` | 平行交错槽、孔板配平 | `zones.py`、`CP-GRACE-MC-01_calc.py` |
| `chain` | 热阻链、温度语义（Tf/Tw/Tj）、预算闭合 | `model.py` r_chain |
| `network` | 水力网络：节点–支路，孔板、UQD、歧管、冷板曲线；Newton 迭代 | 新建 |
| `sweep` | DOE、龙卷风、差距闭合、Pareto | `model.py` orifice_sweep |
| `report` | 计算书 md/html/json | `make_cycle.py` 模式 |
| `cli` | `python -m oned run --dp DP-A-W` | 新建 |

### 6.3 设计点数据模型

设计点放在 `agent/practice01_0926/designpoints/`，一个文件一个设计点，字段示例：

```yaml
id: DP-A-W            # 水基线 1100 W
status: baseline      # baseline / candidate / superseded
source: references/NVIDIA_B300_微通道冲击换热冷板设计报告_v2.0_20260914new.html#9
date: 2026-09-14
confidence: 0.8
fluid: {name: water, T_C: 40, props_ref: props/water40_v20}
power: {total_W: 1100, die_W: [429, 429], hbm_W: 24.75, hbm_n: 8, other_W: 44}
flow: {total_lpm: 2.0, split_gpu: 0.80}
geometry_ref: geo/b300_v20_216.yaml
targets: {R_c_in_max: 0.028, dP_max_kPa: 20, V_hbm_max: 0.80, V_jet_max: 2.0}
```

初始建三组：`DP-A-W`（水 1100 W 2.0 L/min）、`DP-B-W`（水 1400 W 2.4 L/min）、`DP-P-1400`（PG25 1400 W，6 °C，3.512 L/min）。HBM 截面用 `geo/hbm_A…D.yaml` 登记，`current: true` 只能有一个。

### 6.4 关联式库与适用域

| 关联式 | 适用域 | 越域处理 | 来源 |
|---|---|---|---|
| Martin 1977 阵列面平均 | 2000 ≤ Re ≤ 1e5；0.004 ≤ f ≤ 0.04；2 ≤ H/D ≤ 12 | 只作外推对照，不进保证值 | v2.0 §9.4 |
| 驻点核 Nu0 = 0.5 Re^0.5 Pr^0.4 | 孔正下方约 2D 范围 | 不代表整胞平均 | v2.0 §9.4 |
| 层流发展段 Nu = max(4, 1.86 Gz^1/3) | Re < 2000，矩形槽 | Re > 2000 警告 | `oned.py` |
| Shah & London f·Re | 层流矩形槽 | 同上 | v2.0 §9.5 |
| Grace Nu = 4.8 | 三面受热矩形槽假设 | 标“假设，不是关联式” | Grace v1.0 §5 |
| 孔口 K = 1.8 | 锐边孔 | 由 CFD 反标定（12 格带显示 +27.6%） | v2.0 §9.3 |

关联式升级候选（经 `librarian` 检索后再定）：低 Re 液体阵列射流关联式（覆盖 Re 300–2000）、带短槽回流的复合模型。新关联式入库前要有 CFD 或试验对照，并在记忆里写适用域。

### 6.5 水力网络

用节点–支路模型描述：供液歧管 → UQD → 冷板入口 → 静压箱 → 孔口（216 并联）→ 槽 → 回液缝 → 出口 → UQD → 回液歧管。托盘层是 4 块 GPU 冷板与 2 块 Grace 冷板并联，Grace 入口孔板配平。每条支路的压降 ΔP = R·Q + K·ρV²/2，CFD 或试验得到的曲线可以替换解析支路。输出：各支路流量、压降、孔板孔径建议。首个验证用例：Grace PG25 0.8 L/min 下 4×1.04 mm 孔板 22.9 kPa（Grace v1.1 §3）。

### 6.6 输出与计算书

每次运行写 `runs/<时间戳>-oned-<dp>/`：`inputs.yaml`（参数副本）、`result.json`（全部数字）、`report.md` 与 `report.html`（计算书：公式、代入值、结果、判据、证据等级）、`log.txt`。json 结构与现有 `oned_design` 返回值兼容，设计台和 MCP 直接读取。

### 6.7 回归与验证

| 层次 | 黄金数据 | 容差 |
|---|---|---|
| 单元 | 关联式手算点（Shah & London 表值、Martin 原文例） | 0.1% |
| 回归 A | v2.0 §9 表：孔速、Re、孔口 ΔP、R_conv、R 区间、ΔTf、HBM 速度、压降分段 | 0.5% |
| 回归 B | `cycle-20260926/out/cycle.json` 全部字段 | 0.5% |
| 回归 C | v2.1 与 PG25 工作簿：3.512 L/min、0.897 m/s、0.1096 L/min、0.753 L/min | 0.5% |
| 回归 D | Grace v1.1：0.502 m/s、2.44 kPa、20.5 kPa、22.9 kPa | 1% |
| 交叉 | 与 CFD E2 结果对表（不作通过判据，只记偏差） | 记录 |

注意：DR2 工作簿 `03_DR2_一维性能核算.xlsx` 的公式格没有缓存值，需要先用 Excel 或 LibreOffice 重算保存，或在 Python 里按公式重算，才能当黄金数据。

### 6.8 与 MATLAB/Simulink 协同

- 分工：Python 管稳态一维与网络（唯一数值源）；MATLAB/Simscape 管动态（启停、负载阶跃、失冷）和控制设计。
- 接口：Simulink 模型从 `designpoints/*.yaml` 读参数（MATLAB `yamlread` 或先转 json），输出时序 CSV 回 `runs/`。
- 对照：同一稳态点，Simscape 与 Python 的 ΔTf、ΔP 偏差应 < 1%，否则以 Python 为准并查 Simscape 参数。
- 授权不可用时，同样的动态模型用 Modelica 或 Python ODE 实现，接口不变。

## 7 CAD / CFD / 工程图自动化链路

### 7.1 链路总图

<!-- fig:chain -->
```text
设计点 yaml ─► 一维 oned ─► 规则门 rules.py ─►[人确认]─► build123d 实体 ─► STEP + 命名面清单
      │                                                          │
      │                                        ┌─────────────────┴──────────────┐
      ▼                                        ▼                                ▼
  计算书 html                     SpaceClaim 抽流体域 / 修面          Mechanical FEA（承压/压装）
                                          ▼                                ▼
                         网格（ICEM 单胞 / Fluent Meshing 整板）      工程图 DXF/PDF + BOM ─►[人审]
                                          ▼
                   预检（显存/许可）─►[人确认]─► Fluent journal/PyFluent ─► 解析 CSV/日志 ─► 结果入账 ─► 与 1D 对表 ─► R1 判定
```

图 7-1 · CAD→CFD→FEA→出图自动化链路。方括号是人工确认点。

### 7.2 几何轨道与内核升级

- 四条轨道继续分开（`knowledge/cad-tracks.json`）：`parametric-v1`、`measured-asm0921`、`grace-concept`、`tray-schematic`。规划新增第五条 `parametric-v2`，作为 v2 216 孔的参数化轨道，**不覆盖** v1 冻结 yaml。
- v2 内核改动：`jets.pitch` 拆成 `pitch_x`、`pitch_y`（保留 `pitch` 向后兼容）；`rules.REPORT_REFERENCE` 指向 v2 数字（`cad-kernel-gap.md` 已写明这一路径）；HBM 方案参数化（槽数、宽、深、进液方式）；水嘴、UQD、静压箱先做占位特征，ICD 到后替换。
- 每次建模做 STEP 回读核对：包围盒、体积、孔数、孔径（圆柱面取包围盒中点，`environment.md`）。
- 已知坑：OCC 共面布尔会段错误，切除要过切，失败先重试；build123d 放进 Compound 时用 `Pos(0,0,0) * part` 复制。

### 7.3 CFD 前处理

- 流体域：由固体实体做布尔反求，或在 SpaceClaim 里 `Volume Extract`。命名面规范：`inlet_*`、`outlet_*`、`wall_heat`、`interface_*`、`periodic_*`、`sym_*`，清单写 json，网格脚本按名字取面。
- 简化规则遵循 v2.0 §10.3：允许沿 X 中线取 1/2；不允许 1/4；喷嘴不能当多孔介质；必须共轭。
- 网格路线：单胞与局部带用 ICEM hex（已有黄金 replay，人录、AI 改参）；整板用 Fluent Meshing 水密流程。网格判据见 v2.0 §10.4（驻点首层 ≤ 3 μm、y+ < 1 等）。

### 7.4 求解与作业管理

- 控制面：Fluent journal（批处理 `-g -i`）为底线；PyFluent 封装为便利层；GUI 只用于 `fluent-gui-capture` 取报告图。
- 预检：网格量 × 2.2 GB/百万单元 与空闲显存比较；CPU 核数与许可核数比较；同机已有 Fluent 进程时不再启动（`cycle-20260926/index.html` 的做法）。
- 作业目录：`runs/<时间戳>-cfd-<case>/`，含 journal 副本、transcript、监视量 CSV、`manifest.json`（网格、边界、迭代数三者来自同一次运行，`cfd-loop` 第 1 条）。大文件 `.cas.h5/.dat.h5/.msh` 留在算例目录，不入 git，清单记录路径、大小和哈希。
- 工况矩阵：C01–C12（v2.0 §10.7）用一个参数表驱动，失败自动重试一次，再失败就停下来报告。

### 7.5 后处理与结果入账

- 自动提取：Rθ,c-in、ΔP 分段、ΔTf、能量比、质量比、逐孔流量（216 行）及偏差、HBM 近壁最大速度、残差末值。
- 判据自动核：v2.0 §10.8 六条；不满足的标“不可引用”，不写结论句。
- 报告图：走 `fluent-gui-capture`（期刊驱动 GUI、Auto Range、壁面面值、不切在 `z=-2.00 mm` 交界面上）。
- 入账：结果 json 写回算例目录和设计点的 `evidence` 列表，证据等级 E2/E3。

### 7.6 FEA

模板三类：① 3 bar 均布内压（盖板跨射流阵、跨 HBM 区）；② 300–500 N 四角压装 + TIM2 等效弹簧，看接触面平面度；③ 钎焊冷却热应力（可选）。材料用退火 C11000（屈服 70 MPa，E 110 GPa）。结果与 v2.0 §6.3 解析值对表：解析 16.73 MPa 应落在 FEA 最大值的同一量级。

### 7.7 工程图

- 候选图（AI 自动）：外形三视图、底板流道、A-A/B-B 剖面、射流单元、孔位表、爆炸图、BOM，DXF + PDF，图号沿用 JM01-A0～A6。
- 正式图（人定稿）：GD&T 体系、表面处理、焊接符号、检验要求表。AI 提供尺寸表、公差建议和 SolidWorks 宏草稿。
- 图纸检查清单：标题栏、比例、单位、剖切符号、尺寸链闭合、孔数与孔径、公差、材料、版本号；每项自动核或人工勾选。

### 7.8 AI 的能力边界

| AI 可以主责 | AI 辅助、人主责 | 只能人做 |
|---|---|---|
| 写参数、跑规则门、生成 STEP、写 journal、解析日志、对表、出候选图和报告 | 网格拓扑设计（黄金 replay）、发散时的局部修复、FEA 边界合理性、图纸 GD&T | 签 DR 闸门、对外发图、下采购和外协订单、实物上电和试验操作、许可证管理 |

## 8 试验验证与 V&V

### 8.1 试验层级

| 层级 | 内容 | 来源 |
|---|---|---|
| 出厂检验（100%） | 外形、平面度与粗糙度、氦检 3 bar、流阻、喷嘴通畅 | v2.0 §11.1 |
| 型式试验（首件） | T1 热阻、T2 均温、T3 驻点对位、T4 分区流量、T5 包络、T6 PG25、T7 耐久堵塞、T8 压装影响 | v2.0 §11.2 |
| 系统验收（SAT） | 托盘分流后的实际工作点与壳温 | v2.0 §11.3 |
| 先行验证 | 1:1 铜样 + PMMA 透明流道样 + 双 die/八 HBM 加热块；PIV 或染色法看 cell/bank 拓扑 | v2.0 §11.3 注 |

### 8.2 TTV 台架

- 加热：两块 25×25 mm 加热块模拟双 die，八块小加热块模拟 HBM；功率分路可调，独立测量。
- 测量：进出口温度（4 线 Pt100，±0.05 K）、差压（±0.1 kPa）、流量（科氏或电磁，±0.5%）、加热块嵌入热电偶、红外热像（PMMA 样件或去盖测量）。
- 不确定度：按 GUM 合成，目标是热阻测量不确定度 ≤ 5%。若不确定度超过 5%，15% 的 V&V 判据就失去分辨力。
- 工况：从 C01、C03、C04、C08 中选，与 CFD 一一对应。

### 8.3 V&V 层级

| 层级 | 对比对象 | 可接受偏差 | 不达标怎么办 | 现状 |
|---|---|---|---|---|
| V1 代码验证 | 解析解（层流平板、圆管 f·Re） | < 2% | 换求解器或修正设置 | 未做 |
| V2 能量平衡 | 一维 ΔTf | < 2%（硬约束；DR3 判据为 1%） | 查边界与热源加载 | 单胞 1.0015；12 格 1.0368 |
| V3 压降分段 | 一维孔口与槽 | 孔口 < 20%；歧管以 CFD 为准 | 复核 K | 12 格 +27.6%（路径不同） |
| V4 文献锚定 | Martin（Re≈3000 有效域内） | < 15% | 先锚定再外推 | 未做 |
| V5 试验确认 | TTV 实测 Rθ,c-in | < 15% | 触发 R2 回路 | 未开始 |

### 8.4 偏差 > 15% 回路

<!-- fig:vv -->
```text
模型预测（1D / CFD，带版本） ─► 试验测量（TTV，带不确定度） ─► 偏差 ε = |sim − test| / test
        ▲                                                                   │
        │                                          ε ≤ 15% ─► V5 通过 ─► DR4 闸门包
        │                                          ε > 15% ─► 开 R2 工单
        │                                                         ▼
  回 ③ 性能设计 ◄── 模型修正（反标定 h 倍率、TIM2、K、接触）◄── 偏差分解（TIM2/装配/堵塞/模型）
```

图 8-1 · V&V 闭环。

偏差分解顺序：先排除测量（不确定度、传感器位置、热损失）；再排除装配（TIM2 厚度与压力、平面度）；再排除样件（孔径一致性、钎料堵塞，用流阻曲线和 X-ray/CT 判断）；最后才改模型。模型修正只改有物理意义的参数（h 倍率、TIM2 面积热阻、孔口 K、接触热阻），用最小二乘或贝叶斯反标定，并记录参数的置信区间。修正后模型升小版本号，旧版本保留，并写 semantic 记忆（含适用域与 `valid_until`）。

### 8.5 试验数据格式

每次试验一个目录 `vv/tests/<日期>-<样件号>-<工况>/`：`meta.yaml`（样件号、图纸版本、台架版本、传感器与校准证书号、操作者）、`raw.csv`（时间戳、通道、值、单位）、`steady.csv`（稳态窗口均值与标准差）、`photos/`、`ir/`。`test_import` 校验单位、量程、稳态判据（如 10 min 内温度漂移 < 0.1 K），不过就拒收。

## 9 数字孪生与 AI 在环控制

### 9.1 孪生分级

| 级别 | 内容 | 数据来源 | 用途 | 阶段 |
|---|---|---|---|---|
| L0 静态孪生 | 一维模型 + 设计点 | model.py | 设计计算 | 已有 |
| L1 代理模型 | ROM：R(Q, P, Tin, 工质)、ΔP(Q)、Tmax(热点) | CFD DOE + 1D | 快速评估、托盘优化 | P6 |
| L2 动态孪生 | 热 RC 网络 + 水力网络，冷板–托盘–CDU | L1 + 质量热容 | 启停、负载阶跃、失冷窗口 | P6 |
| L3 运行孪生 | 在线校准：进出口温度、流量、ΔP、GPU 遥测（如 DCGM） | 试验台或机柜数据 | 状态估计、堵塞预警、控制 | P6 后期 |

### 9.2 ROM

- 训练数据：一维大样本 + CFD 小样本（多保真度）。CFD 样本用拉丁超立方取 20–40 点（Q、P、Tin、孔径、TIM2）。
- 模型：高斯过程或多项式响应面，输出带不确定度；留一交叉验证误差 < 5% 才可用。
- 导出：Python pickle 与 FMU 两种；有 Twin Builder 授权时导入做静态 ROM。
- 使用边界：只在训练域内用，越域时返回警告并回退一维。

### 9.3 动态模型

托盘级：4 块 GPU 冷板 + 2 块 Grace 冷板，每块冷板用 3–5 节点热网络（芯片、TIM、铜底、流体）；水力用 §6.5 网络。输入：GPU 功率时序、泵转速、阀位、供液温度；输出：芯片温度、出水温度、各支路流量。用来回答：负载阶跃下的超调、失冷多少秒到 Tj 上限（v2.0 不承诺秒数，孪生给区间）、堵塞 20% 时的温升。

### 9.4 AI 在环控制

- 控制对象：CDU 泵转速、托盘或机柜阀位、供液温度设定（在仿真里）。
- 目标：Tj ≤ 上限、泵功最小、温度波动最小；约束：ΔP ≤ 20 kPa、孔速 ≤ 2.0 m/s、近壁 ≤ 0.80 m/s。
- 方法：基线 PID；MPC（用 L1/L2 孪生做预测模型）；RL 只在仿真里训练，作为研究项。
- 评估：与 PID 对比的泵功、超调、约束违反次数；鲁棒性（ROM 误差 ±10%、传感器噪声）。

### 9.5 安全边界

<!-- fig:twin -->
```text
物理对象（试验台 / 托盘 / CDU） ─► 传感器数据 ─► 数字孪生（ROM + RC + 在线校准）
                                                         │
                                                         ▼
                                         AI 控制器（MPC / RL，仅仿真内）
                                                         │
                                                         ▼
                                   安全监督层（硬限值、速率限制、看门狗、回退 PID）
                                                         │
                          ┌──────────────────────────────┴───────────────┐
                          ▼                                              ▼
                 仿真执行器（默认）                     真实执行器（需人工确认，比照闸门③）
```

图 9-1 · 孪生与 AI 在环控制的安全架构。

规则：AI 控制器在本期**只驱动仿真执行器**。任何向真实泵、阀、CDU 下发设定值的动作，以及试验台通电加热，都建议比照平台第③道闸门（实盘/资金动作）由人确认；这一映射需要用户批准（§13 Q8）。

## 10 数据与知识管理

### 10.1 数据分级与存放

| 级别 | 例子 | 存放 | 能否给云端模型看 |
|---|---|---|---|
| D1 公开 | NVIDIA/Lenovo 公开规格、论文、专利 | git + Dify | 可以 |
| D2 内部设计 | 设计点、几何参数、计算书、报告 | git | 可以（项目默认），由用户确认 |
| D3 敏感 | OEM 封装图、功率图、订单 ICD、供应商报价 | 本机或内网，不入公开仓库 | 只给脱敏摘要；触发 `on_sensitive_data` 降级路由 |
| D4 大文件 | cas/dat/msh、原始试验数据、红外视频 | 算例目录或 NAS，不入 git | 只给提取后的 CSV/json |

远程仓库 `origin/main` 的可见性（公开或私有）要由用户确认，D2 是否能推送取决于它（§13 Q7）。

### 10.2 单一数据源与版本

- 设计点、物性、关联式、几何参数：yaml/py 是唯一源；xlsx 是视图，由脚本生成或只读对照。
- 报告：由脚本生成，页脚写数值源与版本；旧报告不删，加“已取代”标签（如 CFD-AI 评估 v1.0、`calc_1d_out.txt`）。
- 命名：`<名称>_v<主>.<次>_<YYYYMMDD>.<ext>`，与现有报告一致。
- 发布：关键步骤后按 `git-release` 生成提交信息，真实 push 由人执行。

### 10.3 skills 沉淀机制

1. 每完成一个实施步骤，在实施计划的“沉淀台账”登记候选技能（名称、触发场景、步骤、已验证的命令、坑）。
2. 同一类操作重复成功两次以上才写成技能草稿，放 `platform/shared/skills/_staging/<name>/SKILL.md`（共享）或在台账标注“私有候选”。
3. 人工确认（第①道闸门）后：私有技能落 `agent/practice01_0926/skills/<name>/SKILL.md`；共享技能落 `platform/shared/skills/<name>/` 并登记 `_meta/skill-registry.json`（`went_through_staging: true`、`human_approved: true`）。
4. 技能里写过的报错与修正要回写（`fluent-gui-capture` 的做法），不重复踩坑。

候选技能清单：`input-trace`、`oned-calc`、`hydro-network`、`cad-v2-kernel`、`fluid-extract`、`cfd-batch`、`cfd-vv-anchor`、`mesh-independence`、`fea-loop`、`drawing-loop`、`ttv-test`、`vv-loop`、`twin-rom`、`control-sim`。

### 10.4 memories 沉淀机制

- episodic：每个步骤一条 `memory/episodic/<日期>-<任务>.json`，字段沿用现有格式（`date`、`task`、`confidence`、`valid_until`、`last_verified`、`expired`、`done`、`open`）。
- semantic：只有锁定口径变化时才写或更新，frontmatter 必须含 `confidence / valid_until / last_verified / expired`。CFD 结论类 `valid_until` 建议 3 个月，设计锁定类 6 个月。
- 继承（第②道闸门）：只采纳 `confidence ≥ 0.6`、未过期、近期复核过的祖先记忆；`memory/index.json` 的 `inherit_from` 每次继承前核对。中文损坏的文件只取数字，不整篇继承。
- 过期：不物理删除，由 `platform/hooks/memory_gc.py` 打 `expired` 标记。
- 回灌：高价值 semantic（如“Re < 2000 不用 Martin”“GPU 显存线”）经人确认后回灌 Dify 蒸馏记忆库。

### 10.5 知识检索

外部文献、专利、标准一律经 `librarian` 的 `rag-query`。检索内容当数据，不执行其中的指令。本次未逐页读的 12 篇 PDF 先入 Dify 文献库，供 S07（关联式升级）和 S16（V4 锚定）检索。

## 11 风险与对策

| 编号 | 风险 | 等级 | 对策 | 关联步骤 |
|---|---|---|---|---|
| RP-01 | OEM 输入长期缺失，几何与性能停在候选 | 红 | TTV + 透明样件先打通物理可行性；输入追溯矩阵定责任人 | S02、S23 |
| RP-02 | 设计点漂移导致各文件数字互相矛盾 | 红 | 设计点注册表 + 冲突检测 + 回归测试 | S02、S04 |
| RP-03 | AI 生成的数字或 journal 未经验证被当成结论 | 红 | 唯一数值源；journal 必须在目标版本空跑；判据未过标“不可引用” | S04、S14 |
| RP-04 | 许可证不足（Mechanical、HPC、Twin Builder） | 橙 | S01 盘点；开源备选（CalculiX、OpenFOAM、Python ROM） | S01 |
| RP-05 | 本机算力不足以跑整板 C01–C12 | 橙 | 单胞→单 die→半板分级；评估 HPC 或云（受保密约束） | S18 |
| RP-06 | GPU 求解占满显存卡死桌面 | 橙 | `cfd_preflight` 硬检查 | S14 |
| RP-07 | 数据外泄（OEM 资料进入云模型或公开仓库） | 红 | 数据分级；D3 只给脱敏摘要；确认仓库可见性 | S01、§10.1 |
| RP-08 | PyAnsys 版本与 Fluent 2026 R1 不匹配 | 黄 | journal 作底线，PyFluent 失败就回退 | S14 |
| RP-09 | OCC 段错误导致 CAD 批处理不稳定 | 黄 | 过切、重试、子进程隔离 | S10 |
| RP-10 | 覆盖冻结 yaml 或已发 STEP | 橙 | 规则门拒写；产物只进 `runs/` | 全程 |
| RP-11 | 热阻真值落在保守端，DP-A 无法达标（v2.0 RK-01） | 红 | R1 回路杠杆；TIM2 优先；必要时提流量 | S07、S19 |
| RP-12 | PG25 下整板或 Grace 支路压降超 20 kPa | 橙 | 水力网络 + 孔板重配 + 整板 CFD | S08、S18 |
| RP-13 | 试验不确定度过大，15% 判据失去意义 | 橙 | 不确定度预算 ≤ 5%；传感器校准 | S23 |
| RP-14 | FTO 风险 | 橙 | 外部专业检索；AI 只做对照草稿 | 外部 |
| RP-15 | 技能与记忆膨胀、过期内容被误用 | 黄 | 台账 + 闸门 + memory_gc | S32 |
| RP-16 | 动态孪生或 AI 控制误下发到真实设备 | 红 | 默认只驱动仿真；真实执行器需人工确认 | S29 |

## 12 里程碑

<!-- fig:gantt-plan -->
```text
周次        W1  W3  W5  W7  W9  W11 W13 W15 W17 W19 W21 W23
M0 规划评审 ■
M1 一维与回归 ■■■
M2 CAD v2       ■■■
M3 CFD 自动化     ■■■■■■
M4 FEA 与图纸             ■■■■
M5 样件与 V&V               ■■■■■■■■
M6 孪生与控制                   ■■■■■■■■■■
M7 平台化                                 ■■■■■■
```

图 12-1 · 里程碑甘特图（W1 = 2026-10-05 当周）。M5 的长度取决于外协加工周期。

| 里程碑 | 完成日期 | 交付物 | 闸门 | 对应实施步骤 |
|---|---|---|---|---|
| M0 规划评审 | 2026-10-09 | 本规划与实施计划评审意见、§13 决策记录 | 用户确认 | S01–S03 |
| M1 一维与回归 | 2026-10-23 | 设计点注册表、一维工具、回归报告、水力网络、DR2 复审包 | DR2 复审 | S04–S09 |
| M2 CAD v2 | 2026-11-06 | `parametric-v2` 内核、216 孔整板与流体域、Grace 接入规则门 | 人确认几何 | S10–S13 |
| M3 CFD 自动化 | 2026-12-04 | 作业工具、V4 锚定、网格无关性、单 die/半板 C01 | — | S14–S18 |
| M4 FEA 与图纸 | 2026-12-18 | 工况矩阵汇总、FEA 报告、候选图纸包 | DR3 仿真评审 + DR3 闸门 | S19–S22 |
| M5 样件与 V&V | 2027-01-29 | 试验大纲、台架、首件数据、V&V 报告 | DR4 | S23–S26 |
| M6 孪生与控制 | 2027-02-26 | ROM、动态孪生、MPC 仿真报告 | 用户评审 | S27–S30 |
| M7 平台化 v1.0 | 2027-03-12 | MCP 工具扩展、设计台新页、技能与记忆正式入库、智能体拆分评审 | ①② 闸门 | S31–S33 |

## 13 需用户决策的问题

| 编号 | 问题 | 选项 | 建议 | 影响 |
|---|---|---|---|---|
| Q1 | 主设计基准 | A 水 1100 W 2.0 L/min（v2.0）；B PG25 1400 W 6 °C 3.512 L/min（v2.1）；C 两者并行 | C，B 为主线、A 作回归基线 | 全部计算与 CFD 工况 |
| Q2 | PG25 物性取哪套 | model.py PG25_40 或 DOWFROST LC 25 表值 | 用供应商实际工质表，两套都入库并标来源 | Re、ΔP、h |
| Q3 | GPU 孔径与 HBM 截面 | D 0.50 / 0.40；HBM A/B/C/D | 决定后注册表只留一个 `current` | CAD、CFD、图纸 |
| Q4 | MATLAB/Simulink 是否可用 | 有授权 / 无 | 无则用 Modelica 或 Python，不阻塞主线 | S09、S28、S29 |
| Q5 | 正式工程图用哪种 CAD | SolidWorks / NX / FreeCAD / 只出 DXF | 公司标准 CAD 定稿，AI 出 DXF 与宏 | S22 |
| Q6 | Ansys 许可范围 | Mechanical、optiSLang、Twin Builder、HPC 核数、PyAnsys 是否允许安装 | S01 盘点后确认 | S14、S20、S27 |
| Q7 | 数据保密与仓库可见性 | `origin` 公开或私有；OEM 资料能否进云模型 | D3 不出本机；确认仓库私有后再推送 D2 | 全程 |
| Q8 | 工程类人工闸门映射 | 外协加工、采购、对外发图、实物上电是否比照闸门③ | 比照③，AI 只到草案 | S22–S26、S29 |
| Q9 | 算力 | 本机 / 内网 HPC / 云 | 先本机分级，整板前评估 | S18、S19 |
| Q10 | 样件与试验资源 | 自建台架 / 外协试验室 | 先 PMMA 透明样 + 铜样 | S23 |
| Q11 | 智能体拆分 | 维持 `cp-design` 单体 / 拆 `cp-cae`、`cp-twin` | 前期单体，S33 再评审 | S33 |
| Q12 | 开源 CFD 是否安装 | OpenFOAM（WSL2/Docker） | 作为交叉校核，可后装 | S16 |

## 附录 A 来源文件索引

| 简称 | 路径 | 日期 |
|---|---|---|
| v2.0 | `agent/practice01_0926/references/NVIDIA_B300_微通道冲击换热冷板设计报告_v2.0_20260914new.html` | 2026-09-14（含 09-28 修订节） |
| v2.1 | `agent/practice01_0926/references/NVIDIA_B300_微通道冲击换热冷板设计报告_v2.1_PG25_20260929.html` | 2026-09-29 |
| Grace v1.0 | `agent/practice01_0926/references/NVIDIA_Grace_GB300_冷板详细设计报告_v1.0_20260926.html` | 2026-09-26 |
| Grace v1.1 | `agent/practice01_0926/references/NVIDIA_Grace_GB300_冷板详细设计报告_v1.1_PG25_20260929.html` | 2026-09-29 |
| 技术调查 v1.3 | `agent/practice01_0926/references/AI算力芯片液冷冷板技术调查分析报告_v1.3_20260907.html` | 2026-09-07 |
| 专利 v1.4 | `agent/practice01_0926/references/AI算力芯片液冷冷板专利分析报告_v1.4_20260907.html` | 2026-09-07 |
| 循环 0926 | `agent/practice01_0926/cycle-20260926/` | 2026-09-26 |
| CFD-AI 评估 | `design/CFD-AI_Agent_能力评估与工作计划_v1.0_20260920.html` | 2026-09-20（部分过时） |
| 12 格契合性 | `design/cfd/uc01b_2.4x3.0lessmesh12cells/UC01b_lessmesh_1D_CFD契合性分析报告_12cells_600step.html` | 2026-09-27 |
| HBM 1D | `design/cfd_HBM/HBM微通道冷板_1D设计报告_v1.0_20260929.html` | 2026-09-29 |
| DR 门表 | `cad/尺寸链计算/汇总报告/01–04_*.xlsx` | 2026-09-29 |
| PG25 分配表 | `cad/尺寸链计算/GB300_冷板液冷热量与流量分配表_PG25_20260929.xlsx` | 2026-09-30 修订 |

## 附录 B 版本记录

| 版本 | 日期 | 内容 |
|---|---|---|
| v1.0 | 2026-10-02 | 首版：现状盘点、需求、架构与选型、①–⑦ AI 结合、一维工具设计、自动化链路、V&V、孪生与控制、数据与知识、风险、里程碑、决策清单 |

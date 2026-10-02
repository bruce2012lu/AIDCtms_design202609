# UC-01b 2.4×3.0 — 怎么打开 ICEM、怎么跑

本目录是 **单孔单元胞**，不是整板。先读 `UC01b_ICEM_Fluent_工作方案_v1.0.html`（或 `.md`）。

## ANSYS 路径（2026 R1 / v261）

```
set AWP_ROOT261=E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261
set AWP_ROOT=%AWP_ROOT261%
set ICEM=%AWP_ROOT261%\icemcfd\win64_amd\bin\icemcfd.bat
set FLUENT=%AWP_ROOT261%\fluent\ntbin\win64\fluent.exe
```

## 打开 ICEM（GUI）看现有网格

当前 Fluent 网格是 **Python 笛卡尔 hex**（`mesh\write_hex_msh.py` → `mesh\uc01b.msh`），**不是** ICEM tetra。`logs\icem_batch.log` 里 tetra 失败（surface file 空），所以没有 ICEM 原生 tet，也没有 `.blk` blocking。

ICEM 工程：`icem\uc01b.prj` + `icem\uc01b.uns`（116320 HEXA_8，由 `icem\uc01b.nas` 经 IcedNastran 转入；`readfluent` 读不了 Fluent-26 的 msh 括号写法）。体积 part 名是 `ET3D1`（Nastran PID），不是 Fluent zone 名。质量只看 `icem\views\quality.txt`。

**一键打开（推荐）：**

```bat
cd /d D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0
call run_icem_view.bat
```

或：启动 `icemcfd.bat` → **File → Open Project** → `icem\uc01b.prj`（会加载 `icem\uc01b.uns`）。

若画面空：File → Mesh → Open Mesh → `icem\uc01b.uns`，再 **Fit（F9）**。  
也可 File → Replay Scripts → Replay → `icem\view_uc01b.rpl`（拟合、显示 hex、质量直方图、截图）。

**目视看什么（单位：米；几何 tin 是毫米，不要叠在一起）：**

1. **三短槽**：Y ≈ −0.80 / 0 / +0.80 mm，Z = 0–1.5 mm。切面 `Z = 0.75 mm`（`icem\views\section_slots_z075.png`）。
2. **射流孔**：X=0、Y=0，等面积方孔边长 0.3545 mm（官方圆孔 D=0.40 在 tin 里）。切面 `X=0`（`icem\views\section_jet_x0.png`）。
3. **回液缝**：±X 两端半缝（各 0.40 mm），顶面 `return_slot` 上抽。等轴测 `icem\views\iso.png`。

Parts / zones：`inlet_jet wall_orifice wall_lid wall_imp fin return_slot SYM fluid`。

质量数字只信 `icem\views\quality.txt`（ICEM 算过才写）。不要用本 README 编造质量。

## 批处理 ICEM

```bat
cd /d D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0
call run_icem.bat
```

日志：`logs\icem_batch.log`。许可证或 replay 失败时不要假装网格已检查。

## 应急笛卡尔 hex（方案 §4 允许）

圆孔 hex blocking 若批处理失败，用等面积方孔（边长 0.3545 mm）出网格，让 Fluent 能起步：

```bat
python mesh\write_hex_msh.py
```

写出 `mesh\uc01b.msh`。这不是 ICEM 质量检查过的网格。

## 批处理 Fluent（层流，必做）

```bat
call run_fluent.bat
```

journal：`fluent\uc01b_cht_v2_t4_gpu_n216_q105.jou`（当前 DP-A 边界）  
名义 q''=55.16975308641976 W/cm²，施加 q''=57.92824074074075 W/cm²（×1.05），ṁ=**1.2249382716049385×10⁻⁴ kg/s**（1.60 L/min / 216）。不要填 2.0 L/min，也不要把 5% 乘到流量上。  
下面的 `uc01b_laminar.jou` 仍是旧 128 孔入口 2.0671e-4 kg/s，不要再当当前边界。

## 四步

1. 工作方案 HTML+MD  
2. ICEM 几何+网格  
3. Fluent 短算  
4. 结果报告 HTML+MD（有残差才能写）

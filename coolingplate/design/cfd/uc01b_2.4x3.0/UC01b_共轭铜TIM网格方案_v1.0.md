# UC-01b 共轭铜 + TIM2 网格方案 v1.0

**文档编号：** AIDC-B300-CFD-UC01b-CHT-PLAN-001  
**版本：** v1.0  
**日期：** 2026-09-22  
**算例：** UC-01b　单孔单元胞 **Option B / CHT**（流体 + 铜底座/肋 + TIM2）  
**目录：** `design/cfd/uc01b_2.4x3.0/`  
**本文件性质：** 共轭网格与材料冻结方案。**不是**仿真结果。图 3–4 是几何示意 SVG，**不是** Fluent 云图。结果只写进结果报告，且必须来自已开 GUI 的实跑。

配套 HTML（同图、可滚读）：`UC01b_共轭铜TIM网格方案_v1.0.html`。流体-only 方案见 `UC01b_ICEM_Fluent_工作方案_v1.0.html`。本页只加固体层。

---

> **当前设计边界（2026-09-25 起，网格几何不改）：** 9×12 = 108 孔/die，两 die 216。DP-A 名义 q''=551697.5308641976 W/m²（55.16975308641976 W/cm²），施加边界 ×1.05 = 579282.4074074075 W/m²（57.92824074074075 W/cm²）。单孔 ṁ=1.2249382716049385×10⁻⁴ kg/s，不加 5%。板规格仍是 1100 W。下表里的 56.746 W/cm² 和 2.067×10⁻⁴ kg/s 是画网格时的旧 128 孔口径，不是现在要施加的边界。

## 0. 冻结结论（先读）

数值只来自 `calc/model.py` 与已写出的网格计数。本页不写 Fluent 残差、ΔT、y⁺ 实测、GCI。

| 项 | 冻结值 | 出处 / 禁止项 |
|---|---|---|
| 单元胞 | \(S_x=\) **3.0 mm**（沿槽）× \(S_y=\) **2.4 mm**（跨槽） | UC-01b；`S_jet=3.0`；三槽刚好 3×0.80 |
| 喷孔 | **圆 D=0.40 mm** | **不是** GEO 默认 0.50；**不是** 等面积方孔 0.3545 |
| 槽 / 肋 | ch_w=0.40，ch_h=1.50，pitch=0.80，肋厚 0.40 | GEO；Y 向 3 槽 + 2 满肋 + 2 半肋 = 2.40 |
| 间隙 / 盖 / 箱 | H_jet=2.0；t_lid=2.5（流体建孔，盖实体不建）；H_plenum=2.0 | GEO |
| 回液 | 物理缝 0.80 mm 在 ±X，本胞各见半缝 0.40 | 与 X 邻胞共享；上抽 |
| 铜 | `base_cu`=2.0 mm + 肋（肋顶 z=1.50）；k=**390** W/mK | `K_CU` / `GEO['base_cu']` |
| TIM2 | t=**80 μm**；k_eff=**8.818 W/mK**（R=0.006） | \(k=t/(R\cdot A_{2\mathrm{die}})\)；\(A=1512\,\mathrm{mm}^2\) |
| 封装 | 实体不建；R_pkg=0.008–0.012 一维外叠 | `R_PKG` |
| 热流 | q''=**56.746 W/cm²** 在 TIM 底 | DP-A die **面平均**；不是热点、不是 HBM |
| P_cell | **4.0857 W** | q'' × 3.0×2.4 mm |
| ṁ | **2.067×10⁻⁴ kg/s** | GPU **1.60 L/min** / 128。2.0 L/min 是整板 DP-A，不是单孔 |
| 压降窗 | 冷板本体 20 kPa | **不含 UQD** |
| 工质 | DI 水 40 °C，Tref=313.15 K | WATER40：ρ=992.2，cp=4179，k=0.631，μ=6.53e-4 |
| 网格（交付） | Python 圆孔 O-grid hex，三体区 | 方孔 coupon **不是** CHT 网格 |

**k_eff 不是某牌 TIM 的本体导热。** 80 μm 键合线把本体导热 + 接触热阻（空洞、粗糙、泵出）捆成一层，使两 die 一维 \(R_{\mathrm{TIM2}}\) 落回 `model.py` 的 0.004–0.008 °C/W。本轮不查、不写具体品牌。

---

## 1. 几何（model.py 为权威）

坐标系：原点在**中槽底面中心**；+X 沿槽；+Y 跨槽；+Z 向上（射流 −Z 打到槽底 / 铜顶）。

### 1.1 平面装填

Y：`3×0.40 槽 + 2×0.40 满肋 + 2×0.20 半肋 = 2.40 mm`。侧槽中心距孔轴 0.80 mm = 2.0 D。

| Y (mm) | 零件 | X (mm) | 零件 |
|---|---|---|---|
| [−1.20, −1.00] | 半肋（SYM） | [−1.50, −1.10] | −X 半缝（上抽） |
| [−1.00, −0.60] | 侧槽 − | [−1.10, +1.10] | 三槽 + 间隙主体 |
| [−0.60, −0.20] | 满肋 | [+1.10, +1.50] | +X 半缝 |
| [−0.20, +0.20] | 中槽（对孔） | | |
| [+0.20, +1.20] | 满肋 / 侧槽+ / 半肋 | | 与上表对称 |

### 1.2 Z 堆叠（共轭）

| Z (mm) | 体区 | 说明 |
|---|---|---|
| −2.080 → −2.000 | `solid_tim2` | 80 μm 全胞 XY；底面 = q'' |
| −2.000 → 0 | `solid_cu` 底座 | 2.0 mm 余铜 |
| 0 → 1.50 | 槽/缝 = fluid；肋 = Cu | 肋顶 z=1.50 |
| 1.50 → 3.50 | fluid 间隙 | H=2.0，壁面射流贴肋顶 |
| 3.50 → 6.00 | 圆孔流体 + 回液缝 | 盖板实体不建；孔壁 = 圆柱 D=0.40 |
| 6.00 → 8.00 | 短静压箱 | 顶面 inlet_jet |

流路不改口：**下射 → 驻点（仅中槽底）→ 壁面射流沿 ±X 并扫入侧槽 → ±X 缝向上抽。** 禁止 bank 长槽、禁止 1/4 对称。

---

## 2. 为什么必须共轭（不能再用 Cu 壳）

`model.py` 湿润面积增益：单 die 35 槽，\(A_{\mathrm{wet}}/A_{\mathrm{die}}=\) **AREA_GAIN ≈ 4.25**。热从 TIM 底进入后要在 2 mm 铜里横向扩展，再经肋导入三槽。Option A 把 q'' 打在流体底再加 2 mm **壳**，铜内没有真实肋导热路径，也没有 TIM 厚向网格。

\[
R_{\mathrm{wall}} = t_{\mathrm{base}} / (k_{\mathrm{Cu}}\cdot A_{2\mathrm{die}}) = 0.002 / (390\times 1.512\times10^{-3}) = 0.003392\ ^\circ\mathrm{C/W}
\]

\[
R_{\mathrm{c-in}} = R_{\mathrm{TIM2}} + R_{\mathrm{wall}} + R_{\mathrm{conv}},\qquad
R_{\mathrm{j-in}} = R_{\mathrm{pkg}} + R_{\mathrm{c-in}}
\]

CHT 把 TIM 与铜建成实体：界面 `wall_tim_cu`、`wall_cu_fluid` 耦合。才能看到 spreading 和 AREA_GAIN，而不是壳上的一维 \(\Delta T=q''\cdot t/k\)。

---

## 3. 三维示意（SVG，不是 CFD）

同 HTML 内嵌图。独立文件便于 Markdown 预览。

**图 3-1　单元胞等轴测。** 金=Cu，红=TIM，蓝=水，橙=回液，绿顶=质量入口。盖板实体未建。尺寸来自 model.py / UC-01b 冻结。

![图 3-1 等轴测](figs/scheme_iso.svg)

**图 3-2　分层爆炸。** 热从 TIM 底进入，经铜扩展与肋，再交给水。封装层不建。

![图 3-2 爆炸堆叠](figs/scheme_explode.svg)

---

## 4. 三向二维剖面（材料 + BC + 网格意图）

下列剖面标材料分区、边界、以及**打算怎么加密**。不是算出的 T/|V|。

**图 4-1　X=0（过射流 / YZ）。** 中槽对准圆孔。虚线：冲击底与孔壁打算做 Δy≤3 μm、增长≤1.2 的边界层。

![图 4-1 X=0 YZ](figs/scheme_yz.svg)

**图 4-2　Y=0（沿槽 / XZ）。** 左右半缝上抽；中间圆孔下射。壁面射流沿 ±X。

![图 4-2 Y=0 XZ](figs/scheme_xz.svg)

**图 4-3　Z 向三刀。** 上：Z=4.75 盖内（圆孔+缝）。中：Z=0.75 三槽。下：TIM 满铺 / Cu 座满铺。网格意图：孔用 O-grid，槽角与缝唇加密。

![图 4-3 Z 切](figs/scheme_zcuts.svg)

---

## 4b. 实网格截图（medium HEXA，不是云图）

下列 PNG 画的是 `mesh/uc01b_cht_medium.msh` 的**单元边**。源：同一套 `write_cht_circle_msh.py`（`UC01B_MESH=medium`）。体网格 **425320 HEXA**（fluid 321168 / Cu 88264 / TIM 15888）。msh 单位是**米**；图上坐标标成 mm。蓝=水，金=Cu，红=TIM。**不是**速度 / 温度 / 热流云图。没有 ICEM 导出 `uc01b_cht_icem.msh`。coarse 165112 同拓扑；fine 见 §4c（4472280，中槽壁已加密）。本页只画 medium。脚本：`mesh/plot_cht_mesh_shots.py`。

**图 4b-1　三维等轴测。** X=0 剖面上 18416 个 HEXA 面 + 5 层真实 XY 网格（17464 个 quad）。共 143520 条边。TIM 底（红）、Cu 座（金）、槽/间隙（蓝）、盖段只剩圆孔。0.50 mm 比例尺。

![图 4b-1 三维网格](figs/mesh3d_iso.png)

**图 4b-2　X=0（过射流 / YZ）。** **18416** 个被切 HEXA 面。三槽 + 中间圆孔柱 + TIM 底条。0.40 mm 比例尺。

![图 4b-2 X=0 网格](figs/mesh_cut_x0.png)

**图 4b-3　Y=0（沿槽 / XZ）。** **15352** 个被切 HEXA 面。左右回液半缝上抽，中间圆孔下射。

![图 4b-3 Y=0 网格](figs/mesh_cut_y0.png)

**图 4b-4　Z 切盖段 zc=4.625 mm（层 k=106）。** **1576** 个 quad：中心圆孔 O-grid + ±X 回液缝。盖实体未建，故中间空白。

![图 4b-4 孔平面网格](figs/mesh_cut_z_orifice.png)

**图 4b-5　Z 切间隙 zc=2.500 mm（层 k=78）。** **3972** 个 quad，全是水。中心仍是圆孔 O-grid 投影。

![图 4b-5 间隙网格](figs/mesh_cut_z_gap.png)

**图 4b-6　Z 切槽中 zc=0.750 mm（层 k=34）。** **3972** 个 quad。蓝=三槽+缝，金=肋/半肋。

![图 4b-6 槽中网格](figs/mesh_cut_z_slot.png)

**图 4b-7　Z 切 TIM2 zc=−2.050 mm（层 k=1，TIM–Cu 界面邻层）。** **3972** 个 quad，整面 TIM。XY 与上面各层共形。

![图 4b-7 TIM 网格](figs/mesh_cut_z_timcu.png)

**图 4b-8　加密局部。** 左：X=0 驻点，|Y|&lt;0.22，**1440** 个切面单元；首层 Δz=**2.5 μm**（≤3 μm，y⁺&lt;1 意图，未测）。右：孔唇 O-grid，zc=4.625 mm，**736** 个 quad，节点在 r=0.20 mm 上。

![图 4b-8 边界层与孔唇](figs/mesh_bl_zoom.png)

---

## 4c. 细化 fine 网格（含导流/回液槽壁面边界层）

已检查的体网格是 `mesh/uc01b_cht_v2.msh`（4472280 HEXA，圆孔 D=0.40 mm）。孔板切面：

![v2 圆孔](figs/v2mesh_z_orifice.png)

z = 4.711 mm，真实单元面。喷孔边界是圆。中心小方块是 O-grid 内 H，不是等面积方孔。方孔 coupon（116320 HEXA）不是本节。

源：`mesh/uc01b_cht_fine.msh`（米）。**4472280 HEXA**（fluid 2760804 / Cu 1533156 / TIM 178320）。medium 不覆盖。

| 项 | medium | fine（本档） |
|---|---|---|
| HEXA | 425320 | **4472280** |
| 孔壁首层 | 8 μm | **3.0 μm**（800 边实测，≥10 层） |
| **中槽**壁/底/顶 | 无（O-square 均匀） | **2.5 μm，n_BL=10，增长≤1.2** |
| 侧槽/回液缝壁 | ~10 μm 或不加密 | **2.5 μm，n_BL=10，增长≤1.2** |
| TIM 层 | 4 | **6** |
| Cu 座层 | 10 | **14**（偏两侧界面） |
| 盖板 | 不建 | **solid_cu** |
| 射流核 Δx | 0.0117 mm | **0.0028 mm** |
| 孔周过渡 | 到 S_FR=0.34 | 外环 + 笛卡尔到 **0.85 mm** |

图是单元边，**不是**云图。无 Fluent y⁺。

**图 4c-1　三维等轴测。** 4472280 HEXA。

![图 4c-1](figs/fine_mesh3d_iso.png)

**图 4c-2　X=0。** 三槽 + 圆孔柱 + 盖铜 + TIM。

![图 4c-2](figs/fine_mesh_cut_x0.png)

**图 4c-3　Y=0。** 回液缝上抽。

![图 4c-3](figs/fine_mesh_cut_y0.png)

**图 4c-4　Z 盖段。** 圆孔 O-grid + 回液缝 + 盖铜。

![图 4c-4](figs/fine_mesh_cut_z_orifice.png)

**图 4c-5　Z 槽中 zc=0.789 mm。** 中槽 y=±0.20 沿 X 有壁面簇；O-grid 只占 |x|,|y|&lt;0.38。侧槽不是中槽的替代。

![图 4c-5](figs/fine_mesh_cut_z_slot.png)

**图 4c-6　孔壁 / 驻点。** 冲击底首层 2.5 μm、n_BL=10；孔壁径向 3.0 μm（800 边实测）。

![图 4c-6](figs/fine_mesh_bl_zoom.png)

**图 4c-7　固体多层。** TIM 6 层、Cu 座 14 层。

![图 4c-7](figs/fine_mesh_solid_zoom.png)

**图 4c-8　回液缝 + 侧槽（不是中槽）。** 首层 **2.5 μm**，**n_BL=10**，增长≤1.2。

![图 4c-8](figs/fine_mesh_slot_bl.png)

**图 4c-9　中槽流体边界层（从 msh Y/Z 节点量）。** 左：Z 切 zc=0.789，X∈[0.42,1.12]，Y∈[−0.60,0.60]。右：X=0.80 YZ，两侧壁 + 底/顶。实测首层 **2.5 μm**，**n_BL=10**。50 μm 比例尺。

![图 4c-9](figs/fine_mesh_center_slot_bl.png)

**图 4c-10　喷孔 + 周边过渡。** 左：盖段，实线 r=0.20、虚线 r=0.85。右：0.80 mm 窗口，孔壁径向簇 3.0 μm。

![图 4c-10](figs/fine_mesh_orif_trans.png)

**图 4c-11　Y=0 过孔竖切。** 轴向孔柱 + 径向过渡。

![图 4c-11](figs/fine_mesh_orif_trans_xz.png)

**CFD 状态：** iter **7900** 已收敛（continuity **4.0743e-07**，日志 `solution is converged`）。场是 `fluent/uc01b_cht_v2_i7900.cas.h5` / `.dat.h5`。圆孔 D=0.40。静压 ΔP = **2227.11 Pa = 2.227 kPa**（表压，iter 7900，已收敛；见结果报告第 4 节）。方孔 0.048 与 iter 3861 / 1439 不是当前结果。云图见结果报告第 8 节。

---

## 4d. 网格规范与缺口

冻结规范（fine，从 `uc01b_cht_fine.msh` 同源节点量；**不是** Fluent y⁺）。旧 medium 盘上文件未重写：中槽当时是 O-square 均匀段，中槽壁 **FAIL**（图 4b-6）。

| 位置 | 规范 | fine 实测 | 结果 |
|---|---|---|---|
| 圆孔壁径向 | ≤3 μm，≤1.2，≥10 层 | 3.0 μm（800 边） | PASS |
| 射流核 r&lt;0.20 | 10–20 μm 量级 | Δx=2.8 μm | PASS |
| 孔周过渡 r=0.20→0.6–1.0 | 增长≤1.2 | 外环 + 笛卡尔到 0.85 mm | PASS |
| 冲击底 / 中槽底 | ≤3 μm，≤1.2，≥8 层 | 2.5 μm，10 层 | PASS |
| 中槽两侧壁 y=±0.20 | ≤3 μm，≤1.2，≥8 层，沿 X | 2.5 μm，10 层（\|x\|&gt;0.38） | PASS |
| 中槽顶 z=1.50 | ≤3 μm，≤1.2，≥8 层 | 2.5 μm，10 层 | PASS |
| 侧槽壁 / 回液缝 | 同上 | 2.5 μm，10 层 | PASS |
| TIM 厚向 | ≥4 | 6 | PASS |
| Cu 座厚向 | ≥6 | 14 | PASS |

O-grid 外框 S_FR=0.38 mm＞孔半径 0.20：圆与中槽同宽，O-grid 岛内不能再铺一套正交槽壁。槽壁边界层在笛卡尔段沿 X 贯通（图 4c-9）。无 y⁺。

---

## 5. TIM2、热流、流量（只重复已冻结公式）

\(A_{2\mathrm{die}}=27\times28\times2=\) **1512 mm²**。t=80 μm 固定。\(k_{\mathrm{eff}}=t/(R\cdot A)\)。

| R_TIM2（两 die） | k_eff | 角色 |
|---|---|---|
| 0.004 °C/W | **13.228 W/mK** | 乐观 |
| **0.006 °C/W** | **8.818 W/mK** | **默认 CHT** |
| 0.008 °C/W | **6.614 W/mK** | 保守 |

Fluent 固体 `tim2`：ρ=2800 kg/m³，cp=1000 J/kgK（只导热，密度/比热不进稳态能量），**k=8.818342 W/mK**。

TIM 厚向 **4 层 hex**（medium 每层 20 μm）。k_eff 把键合线导热 + 接触/空洞捆在 80 μm 一层，用来收回报告热阻，**不是牌号 k**。

q'' = 1100 × 0.39 / (27×28 mm) = **56.746 W/cm²** = 567460.32 W/m²，P_cell=**4.0857 W**。这是 die **面平均**；热点 1.5–2.5×、HBM≈20.5 W/cm² 本胞不加。

ṁ = ρ · (1.60 L/min) / 128 = **2.067×10⁻⁴ kg/s**。圆孔 \(V=\dot m/(\rho A)\approx\) **1.66 m/s**，Re_D≈1008（设计估计，用来定首层，**不是** Fluent 打印）。

备选法（不采用）：取目录 k=3–8 反算 t。例如 k=5、R=0.006 → t=45.4 μm，偏薄。本算固定 80 μm。

---

## 6. 网格意图与三档计划（无 GCI 数字）

圆孔必须 O-grid / 圆柱，节点在 r=0.20 mm 上。相对旧 116k 流体笛卡尔：先加密近壁与射流核，不三向同时 8×。增长硬顶 **1.2**。换热墙（冲击、肋、槽、孔）首层 Δy≤3 μm，设计目标 y⁺&lt;1（**Fluent 打印以前只是估计**）。TIM ≥4 层；孔径向 ≥8–12。

`UC01B_MESH=coarse|medium|fine python mesh/write_cht_circle_msh.py`  
基准 medium 复制为 `mesh/uc01b_cht.msh`。方孔脚本 **不是** CHT 交付。

| 档 | 文件 | HEXA | fluid / Cu / TIM | Δy / n_BL / 径向 |
|---|---|---|---|---|
| coarse | `uc01b_cht_coarse.msh` | **165112** | 126112 / 32216 / 6784 | 3.0 μm / 10 / 8 |
| **medium** | `uc01b_cht_medium.msh` | **425320** | 321168 / 88264 / 15888 | **2.5 μm / 12 / 10** |
| fine | `uc01b_cht_fine.msh` | **4472280** | 2760804 / 1533156 / 178320 | 2.5 μm / 10 / 孔壁 3.0 μm |

medium 面区：`inlet_jet` 736，`return_slot` 840，`wall_heat`/`wall_tim_cu` 3972，`wall_cu_fluid` 18486，`wall_orifice` **1280**（圆柱），`wall_lid` 21596，`SYM` 24904。圆孔节点 |r−R|_max ≈ 0（机器误差）。

\*y⁺ 估计：V=1.66 m/s，Re_D≈1008，ν=6.58e-7，层流平板量级。驻点剪切更大，故 medium/fine 收到 2.5/2.0 μm。**Fluent 打印 y⁺ 才算数。**

**GCI / ΔP / T_w / R_conv 三档表：等 GUI 跑完再写。** §10 门槛：相邻档 R_conv（两 die）变化 &lt;3%。未跑完不填。

Python 圆孔 hex（**米**）已写出，给已开 Fluent 直接读。ICEM tetin（**毫米**）给已开 ICEM 做 O-grid / Fluent V6 导出；**不要把 tin 和 msh 叠在同一视图。**

---

## 7. 零件、材料、界面

| Zone | 类型 | 材料 / BC |
|---|---|---|
| `fluid` | cell | water-liquid 40 °C（992.2 / 4179 / 0.631 / 6.53e-4） |
| `solid_cu` | cell | copper k=390 |
| `solid_tim2` | cell | tim2 k=8.818 |
| `inlet_jet` | mass-flow-inlet | 2.067e-4 kg/s，T=313.15 |
| `return_slot` | pressure-outlet | T=313.15 回流 |
| `wall_heat` | wall | q''=567460.32 W/m² |
| `wall_tim_cu` | coupled wall | TIM–Cu |
| `wall_cu_fluid` | coupled wall | Cu–水（槽底/肋） |
| `wall_orifice` | wall | 圆柱 D=0.40 |
| `wall_lid` / `SYM` | 绝热 / 对称 | 盖下；±X±Y |

SST（主）；层流可作包络。Tref=313.15 K。20 kPa 是板内窗，不含 UQD。

Option A（已跑）：流体-only + `wall_imp` 热流 + 2 mm Cu **壳**。禁止把 Option A 的 T_w / R 抄到本页当 CHT 结果。

---

## 8. 已开 ICEM / 已开 Fluent — 只 Replay / Read Journal

**不要再启动** `icemcfd.bat` 或 `fluent.exe`。许可证已在两个 GUI 里。

短清单（与 `GUI_STEPS.txt`、`icem/OPEN_ICEM_THEN_FLUENT.txt` 相同）：

```
ICEM（毫米 tin）
  File → Replay Scripts → Replay
  D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0\icem\replay_cht_circle.rpl
  等价 Tcl：icem\replay_cht_circle.tcl
  Fit (F9) → 应看到胞盒 + 圆 D=0.40 + TIM/Cu 点
  （可选）Hexa O-grid 围圆，首层 ≤0.003 mm，增长 ≤1.2
  Output → Fluent V6（ICEM 的 fluent6 写出器）
       → mesh\uc01b_cht_icem.msh
  详细：icem\OPEN_ICEM_THEN_FLUENT.txt

Fluent（米 msh）
  File → Read → Journal
  D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0\fluent\uc01b_cht_gui.jou
  默认读 mesh\uc01b_cht_medium.msh（圆孔 Python hex，米）
  若 ICEM 已导出 icem.msh，先改 journal 里的 read-case 再读
  Journal 不 /exit。80 步后写 fluent\uc01b_CHT
```

单位：**ICEM tin = mm**；**Python / Fluent msh = m**。不要 overlay。

ICEM 路径（已开，勿再启）：`E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\icemcfd\win64_amd\bin\icemcfd.bat`  
Fluent 路径（已开；journal 里不要写 `-shortcut`）：`E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\fluent.exe -r26.1.0`

Transcript 有 T、P 之后（**不要编造**）：

```
R_conv_cell = (T_wall_cu_fluid - 313.15) / 4.085714
R_conv_2die = R_conv_cell / 210
R_c-in = 0.006 + 0.003392 + R_conv_2die
R_j-in = R_c-in + R_pkg     R_pkg = 0.008 to 0.012
```

---

## 9. 闸门

| 闸门 | 本方案 |
|---|---|
| TIM t / k_eff 冻结 | 80 μm / 8.818 W/mK（R=0.006） |
| 圆孔冻结 | D=0.40，O-grid，节点在圆上 |
| 三区网格已写 | `mesh/uc01b_cht_medium.msh`（425320 HEXA） |
| 方案图 | HTML 内嵌 SVG + `figs/scheme_*.svg`；**另有** `figs/mesh_*.png` 实网格边 |
| Fluent / ICEM | 已开 GUI；只 Replay / Read Journal；不二次启动 |
| GCI / ΔT | **未跑完不填** |
| 提交 | 本轮不 commit |

*AIDCtms / uc01b_2.4x3.0 · 共轭铜 TIM 网格方案 v1.0 · 2026-09-22*

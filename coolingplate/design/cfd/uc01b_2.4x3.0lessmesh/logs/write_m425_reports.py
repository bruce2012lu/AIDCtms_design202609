# -*- coding: utf-8 -*-
from pathlib import Path
root = Path(r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh")

res_md = r'''# UC-01b lessmesh 结果报告 v1.0

**文档编号：** AIDC-B300-CFD-UC01b-LESS-RES-001  
**日期：** 2026-09-25  
**性质：** 当前设计点的运行记录。数字来自 `logs/fluent_cht_less_m425_gpu.log`，iter 380。网格是加密后的 4,259,680 HEXA。不是旧的 567460.32 W/m²、0.0002067 kg/s 场，也不是上一份 2,115,436 单元、iter 421 的场。

场：`fluent/uc01b_cht_less_m425_bc216.cas.h5` / `.dat.h5`。网格：`mesh/uc01b_cht_less.msh`（2026-09-25 11:42）。

---

## 0. 状态

| 项 | 值 |
|---|---|
| 孔数 | 每颗 die **108**，两颗 **216**。单孔模型，进口区只有一个孔 |
| 胞尺寸 | Y（导流槽所在的跨槽方向）**2.4 mm**，X 沿槽 **3.0 mm**。孔距未压缩，孔心未移动 |
| 热流 | `wall_heat` **579282 W/m²**（57.928 W/cm²） |
| 流量 | `inlet_jet`（单孔）**1.225×10⁻⁴ kg/s**。不是 ×108，也不是 ×216 |
| 入口温度 | 313.15 K |
| 网格 | Fluent 读入 **2055516 + 2083716 + 120448 = 4259680** HEXA。边界层首层 2.5 μm，n_BL=10，增长 1.2 |
| 平面加密 | 孔外过渡段均匀 **0.080 mm**（原 0.354 mm）；缝唇外侧 **0.0675 mm**（原 0.135 mm）；槽芯 Y **0.045 mm × 6**（原 0.090 mm × 3）；肋芯 **0.068 mm**（原 0.135 mm） |
| 求解 | 3ddp **-t4 -gpu**，桌面 GUI，无 `-g`。SST k-ω，能量，共轭。iter **380** 已收敛 |

启动命令：

```
"E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\fluent.exe" 3ddp -r26.1.0 -t4 -gpu -i fluent\uc01b_cht_less_m425_bc216.jou
```

`FLUENT_INC` 是目录 `...\v261\fluent`。窗口标题：`uc01b_cht_less_m425_bc216 Parallel Fluent@DESKTOP-JHEHF28 [3d, dp, pbns, sstkw, 4-processes, gpu]`，会话 1。期刊没有 `/exit`，窗口在写完 cas/dat 后仍开着。

---

## 1. 残差

```
   380  6.2412e-07  6.2793e-07  1.9747e-06  2.6352e-06  9.9059e-07  1.1046e-06  1.6245e-04
!  380 solution is converged
```

| 量 | iter 380 | 判据 |
|---|---|---|
| continuity | 6.241e-07 | < 1e-4 |
| x / y / z | 6.279e-07 / 1.975e-06 / 2.635e-06 | < 1e-4 |
| energy | 9.906e-07 | < 1e-6 |
| k / omega | 1.105e-06 / 1.625e-04 | < 1e-3 |

前 300 步一阶，之后二阶。coupled + pseudo-transient。GPU：4 个进程共用 RTX 4090。

---

## 2. 工程量（216 孔口径）

q'' = 579282 W/m²。A_cell = 3.0×2.4 mm² = 7.20×10⁻⁶ m²。  
P_cell = **4.17083 W**。N = **216**。P_2die = **900.899 W**。T_in = 313.15 K。

| 量 | Fluent 打印 |
|---|---|
| T_in (`inlet_jet`) | **313.15 K** |
| T_out (`return_slot`，面积加权) | **320.910 K** |
| T_TIM 底 (`wall_heat`) | **341.385 K** |
| T_铜–水 (`wall_cu_fluid`) | **326.600 K** |
| T_TIM–铜 (`wall_tim_cu`) | **336.130 K** |
| 热流 (`wall_heat`) | **579282 W/m²** |
| P_in | **1087.09 Pa** |
| P_out | **0 Pa** |
| 静压 ΔP | **1087.09 Pa = 1.087 kPa** |

R(T_TIM−T_in)_2die = (341.38529−313.15)/900.899 = **0.03134 K/W**。单胞 **6.770 K/W**。已含 TIM、铜、对流，不要再加 R_TIM2、R_wall。  
R_conv,2die = (326.59968−313.15)/900.899 = **0.01493 K/W**。单胞 **3.225 K/W**。  
h(TIM 底) = q''/(T_TIM−T_in) = **2.052×10⁴**。h(铜–水，同一 q'') = **4.307×10⁴**，不是湿面局部对流系数。

R_wall（一维，A_2DIE=1512 mm²）= 0.003392 K/W。  
**R_c-in = (0.004–0.008)+0.003392+0.01493 = 0.02232–0.02632 K/W。**  
**R_j-in = (0.008–0.012)+R_c-in = 0.03032–0.03832 K/W。**

U = 0.9825 m/s，Re_D = **597**。低于 Martin 1977 的 Re≥2000，不引用 Martin h。  
T_out 是面积平均。ṁ cp ΔT_area / P_cell = **0.952**，不要当成能量已经闭合。需要的 bulk 温升是 8.147 K（出口 bulk 321.30 K）。

---

## 3. 和上一份 bc216（2,115,436 单元，iter 421）的差别

边界条件相同：579282 W/m²，单孔 1.225×10⁻⁴ kg/s。变的是平面上的粗格子。

| | 上一份 iter 421 | 本次 iter 380 |
|---|---|---|
| 单元 | 2,115,436 | **4,259,680** |
| 静压 ΔP | 1091.51 Pa | **1087.09 Pa** |
| T_TIM | 342.096 K | **341.385 K** |
| T_铜–水 | 326.838 K | **326.600 K** |
| T_out | 320.993 K | **320.910 K** |

压降低 4.4 Pa（约 −0.4%），TIM 底低 0.71 K。加密没有改掉设计点的量级。
'''

fit_md = r'''
# UC-01b lessmesh 一维与 CFD 契合性分析报告

**文档编号：** AIDC-B300-CFD-UC01b-LESS-CMP-001  
**日期：** 2026-09-27  
**来源：** 《NVIDIA B300 微通道冲击换热冷板设计报告》v2.0（2026-09-14）及其计算模块 `design/calc/model.py`；《NVIDIA Grace GB300 冷板详细设计报告》v1.0（2026-09-26）。CFD 场 `uc01b_cht_less_m425_bc216`，iter 380，4,259,680 HEXA。

本胞是 B300 GPU 射流阵列里的一个孔。设计报告正文的孔径是 D = 0.50 mm，本网格按报告里的单胞口径取 D = 0.40 mm。流量、孔数、热流冗余与 v2.0 的 DP-A 相同。Grace 是托盘上的另一块 300 W 冷板，第 4 节单独列表。

相对差 = (CFD − 1D) / 1D。同一口径、约在 ±20% 以内记为接近。分母或组成不同的量只并列，不相减。

## 1. B300 设计报告中的设计点

下列数字由 v2.0 的同一计算模块复算，与报告摘要中的壳–进液区间 0.0326–0.0366 °C/W、板内压降 3.5–5.5 kPa 一致。水物性 40 °C：ρ = 992.2 kg/m³，cp = 4179 J/kg·K，μ = 6.53×10⁻⁴ Pa·s，k = 0.631 W/m·K，Pr = 4.32。铜 k = 390 W/m·K。孔口系数 K = 1.8。Martin 1977 的有效域是 Re_D ≥ 2000，DP-A 的 Re_D = 478（D = 0.50 mm）和本胞的 597（D = 0.40 mm）都低于该下限，报告不采用 Martin h。

| 项 | DP-A（本胞所属） | DP-B（报告中的包络，本场未算） |
|---|---|---|
| 整板功率 / 流量 | 1100 W，2.0 L/min，进液 40 °C | 1400 W，2.4 L/min，进液 40 °C |
| 功率拆分 | die 429 W × 2，HBM 24.75 W × 8，其它 44 W | die 546 W × 2，HBM 31.5 W × 8，其它 56 W |
| GPU 支路 | 858 W，1.60 L/min（总流量的 80%） | 1092 W，1.92 L/min |
| 孔 | 每 die 9 × 12 = 108，两 die 216。节距 X 3.0 mm × Y 2.4 mm | 同左 |
| 单孔流量 | 0.007407 L/min，ṁ = 1.22494×10⁻⁴ kg/s | 0.008889 L/min，ṁ = 1.46993×10⁻⁴ kg/s |
| 胞热流 | 名义 55.170 W/cm²（551698 W/m²）。施加边界 ×1.05 = 57.928 W/cm²（579282 W/m²）。单胞名义 3.972 W，边界 4.171 W。两 die 边界功率 900.9 W | 名义 70.216 W/cm²，边界 73.727 W/cm² |
| die 面热流 | 56.75 W/cm²（die 27 × 28 mm） | 72.22 W/cm² |
| 整板流体温升 | 7.959 K，出液约 47.96 °C | 8.441 K，出液约 48.44 °C |
| 单孔名义温升 | 7.760 K | 8.230 K |
| 单孔边界温升 | 8.147 K，出口 bulk 321.30 K | 本场未按 DP-B 加热 |
| 壳–进液目标 | < 0.028 °C/W | < 0.025 °C/W |
| 板内压降目标 | ≤ 18 kPa，上限 20 kPa | 同左 |

### 1.1 几何

| 特征 | 设计报告 | 本网格 |
|---|---|---|
| 板 | 95 × 75 × 8.5 mm | 本计算域是一个胞 |
| 射流 | 正文 D = 0.50 mm，H = 2.0 mm，S/D_x = 6.0，S/D_y = 4.8，H/D = 4.0，f = 0.0273 | 圆孔 D = 0.40 mm。间隙高 2.0 mm（肋顶 z = 1.50 mm 到 z = 3.50 mm）。S/D_x = 7.5，S/D_y = 6.0，H/D = 5.0，f = 0.0175 |
| 胞 | 3.0 × 2.4 mm，面积 7.20 mm² | X = ±1.50 mm，Y = ±1.20 mm |
| 短槽 | 0.40 × 1.50 mm，节距 0.80 mm，每个 Y 向胞 3 条。Dh = 0.632 mm，f·Re = 17.98。湿润面积放大 4.25 倍 | 三条 0.40 mm 槽，槽深 1.50 mm，边界层首层 2.5 μm |
| 余铜 | 槽底以下 2.0 mm，k = 390 W/m·K | 铜从水界面 z = 0 向下。TIM 为单独一层 |
| 盖板 | 2.5 mm；歧管压降按 3–5 kPa 留区间 | 本胞含孔板与回液缝，不含整板歧管 |

### 1.2 短槽模型 C 与热阻链

R_wall = 0.003392 °C/W。R_TIM2 假设 0.004–0.008 °C/W。R_pkg 假设 0.008–0.012 °C/W。R_θ,c-in = R_TIM2 + R_wall + R_conv，再乘整板功率。

| 量 | DP-A，D = 0.50 mm | 同一公式，D = 0.40 mm |
|---|---|---|
| 孔口 | 0.629 m/s，Re = 478，353 Pa | 0.9824 m/s，Re = 597，862 Pa |
| 短槽（就近排走） | 0.0343 m/s，Re = 33，1.5 Pa | 不随孔径变 |
| 短槽（单向对比上界） | 0.635 m/s，Re = 609，75 Pa | 同左 |
| Nu / h_ch / 肋效率 | 5.777 / 5772 W/m²·K / 0.948 | 同左 |
| 驻点 h | 2.48×10⁴ W/m²·K | 3.46×10⁴ W/m²·K |
| h_eff / R_conv | 2.55×10⁴ W/m²·K，0.02524 °C/W | 2.54×10⁴ W/m²·K，0.02530 °C/W |
| R_θ,c-in | 0.03263–0.03663 °C/W | 0.03269–0.03669 °C/W |
| ΔT_c / T_c / T_j（×1100 W） | 35.9–40.3 K；75.9–80.3 °C；84.7–93.5 °C | 与上列只差约 0.06 K |
| 对 0.028 °C/W | 两端都高于目标 | 同左 |

DP-B、D = 0.50 mm：孔口 0.755 m/s，Re = 573，508 Pa；R_conv = 0.02373 °C/W；R_θ,c-in = 0.03113–0.03513 °C/W；T_c = 83.6–89.2 °C；T_j = 94.8–106.0 °C。

HBM 区无喷嘴。DP-A：0.40 L/min，0.463 m/s（帽 0.80 m/s），Re = 603，槽压降 168 Pa。本胞不含 HBM。

### 1.3 压降预算

| 分段 | DP-A | DP-B | 本胞 CFD |
|---|---|---|---|
| 喷嘴孔口 K = 1.8 | 0.353 kPa（D = 0.50 mm）；0.862 kPa（D = 0.40 mm） | 0.508 kPa | 入口静压 1.087 kPa，出口 0 |
| GPU 短槽 | 0.0015 kPa | 0.0018 kPa | 含在 1.087 kPa 里 |
| HBM 槽 | 0.168 kPa | 0.202 kPa | 本胞无此区 |
| 歧管 / 隔墙 | 3–5 kPa | 3–5 kPa | 本胞无整板歧管 |
| 板内合计 | 3.52–5.52 kPa | 3.71–5.71 kPa | 单胞静压差 1.087 kPa |

## 2. 与 iter 380 的对照

期刊把 1.22494×10⁻⁴ kg/s 写成 1.225×10⁻⁴ kg/s（+0.005%）。面速度积分：入口与出口都是 1.22500×10⁻⁴ kg/s，出口比入口 +0.00033%。

| 项目 | 一维 | CFD iter 380 | 相对差 | 判断 |
|---|---|---|---|---|
| 入口温度 | 313.15 K | 313.15 K | 0 | 契合 |
| 孔数 / 节距 | 216；3.0 × 2.4 mm | 单孔单元胞 | 0 | 契合 |
| 单孔 ṁ | 1.22494×10⁻⁴ kg/s | 1.22500×10⁻⁴ kg/s | +0.005% | 契合 |
| 热流 | 边界 579282 W/m² | wall_heat 579282 W/m²，P_cell = 4.17083 W | 0 | 契合 |
| 孔径 | 单胞口径 0.40 mm | 圆孔 0.40 mm | 0 | 契合 |
| 孔口速度 | 0.9824 m/s | 入口面 0.98265 m/s | +0.022% | 契合 |
| Re_D | 597 | 597 | 0 | 契合。低于 2000，不用 Martin h |
| 孔口静压 | 862 Pa | 1087.09 Pa | +26.1% | 超出 ±20%。CFD 含射流、槽和回液缝 |
| 整板流体温升 | 7.959 K | 本胞质量加权温升 8.159 K | 分母不同 | 整板含 HBM 与其它功率 |
| 能量温升 | 边界 8.147 K，bulk 321.297 K | 质量加权 321.309 K，温升 8.159 K。面积加权 320.910 K | bulk +0.15%；面积加权 −4.8% | 接近。能量比 1.0015 |
| R_conv | 0.02524 °C/W（D = 0.50 mm） | 0.01493 °C/W，界面温升 13.45 K | 约 −41% | 短槽模型偏保守；一个是有效肋面，一个是界面面积加权 |
| TIM 层 | 假设 0.004–0.008 °C/W | 80 μm，k = 8.818，温降 5.255 K，0.00583 °C/W | 落在假设区间内 | 这是该层导热 |
| 余铜 | 0.003392 °C/W | 温降 9.530 K，0.01058 °C/W | 组成不同 | CFD 含肋和扩散 |
| R(T_TIM−T_in) | 0.03263–0.03663 °C/W，乘 1100 W | 341.385 K，0.03134 °C/W，除以 900.899 W | 分母不同 | 共轭场已含 TIM 与铜 |
| R_θ,j-in | T_j = 84.7–93.5 °C | 本场没有管芯温度 | — | R_pkg 仍是假设 |
| 目标 0.028 | 短槽链两端都高于目标 | 0.03134 的分母是 900.9 W | — | 设计未关闭 |

## 3. 差从哪里来

压降：D = 0.40 mm 的孔口一维是 862 Pa，CFD 静压差 1087 Pa，高 225 Pa（+26.1%）。短槽一维只有 1.5 Pa。与 2,115,436 单元 iter 421 相比，ΔP 从 1091.51 Pa 到 1087.09 Pa，TIM 底从 342.096 K 到 341.385 K。

能量：质量加权出口 321.309 K。入口、出口积分流量相对差 +0.00033%。面积加权 320.910 K 的温升比是 0.952。能量闭合看质量加权，比值 1.0015。

热阻：模型 C 约 22 K 的流体侧温升，CFD 铜–水界面比进液高 13.45 K。R_θ,c-in 乘整板 1100 W。CFD 的 0.03134 °C/W 乘两 die 边界功率 900.9 W。两个数都高于 0.028。

## 4. Grace 设计报告中的数

来自 Grace v1.0，计算域与本胞不同。水：ρ = 992 kg/m³，cp = 4179，μ = 6.53×10⁻⁴，k = 0.632。300 W、温升 8 K 对应 0.543 L/min，设计取 0.55 L/min。

Grace 报告第 3 节对照表写 B300 为 128 孔、总厚 12.5 mm。B300 v2.0 是 216 孔、板 95 × 75 × 8.5 mm。本页 B300 列以 v2.0 为准。

| 项 | Grace v1.0 |
|---|---|
| 热设计点 | 300 W。CPU 260 W，两侧内存合计 40 W |
| 面热流 | CPU 窗口 40 × 32 mm 为 20 W/cm²；一侧内存 50 × 70 mm 为 0.6 W/cm²；裸片 25 × 25 mm 时 CPU 约 42 W/cm² |
| 结构 | 两层铜，200 × 120 × 8.0 mm（平面候选）。通道深 1.2 mm。C11000 / TU1 |
| CPU 通道 | 48 条，0.40 × 1.20 mm，节距 0.80 mm，长 32 mm，Dh = 0.60 mm |
| 内存通道 | 每侧 6 条，1.20 × 0.80 mm，长 70 mm，Dh = 0.96 mm |
| 流量 | 0.55 L/min，包络 0.70 L/min。CPU 0.47 L/min，单侧内存 0.036 L/min |
| CPU 水力 | 0.34 m/s，Re = 310，0.71 kPa，h ≈ 5100 W/m²·K，对流温升约 12 K。Nu 按 4.8 |
| 单侧内存 | 0.11 m/s，Re = 153，槽 0.17 kPa，缝另补约 0.5 kPa，h ≈ 3200，约 5 K |
| 壳–进液目标 | < 0.080 °C/W。一维对流约占 0.046 °C/W |
| 孔板 | 4 × ⌀1.04 mm，流量系数 0.62，约 9.3 kPa。支路约 10 kPa，窗口 8–12 kPa，上限 18 kPa，极限 20 kPa |
| 接头 | 外径 8 mm、内径 6 mm。0.55 L/min 时约 0.32 m/s |
| 进厂 | 平面度 ≤ 0.05 mm，Ra ≤ 0.8 μm。过滤 ≤ 25 μm |

## 5. 不用的数

不用 iter 430 / 547 的 2237.64 Pa、335.404 K，也不用 i7900 的 2227.11 Pa、335.428 K。那些场的热流是 567460 W/m²，单孔流量是 2.067×10⁻⁴ kg/s。网格说明文件里的同一组旧热流也不是 iter 380。iter 421 的 1091.51 Pa、342.096 K 只作更稀网格的对照。总压差、GCI、y+ 本场没有导出。

'''

def md_to_html(title, md):
    lines = md.splitlines()
    body = []
    in_table = False
    in_code = False
    for ln in lines:
        if ln.startswith("```"):
            if in_code:
                body.append("</pre>")
                in_code = False
            else:
                body.append("<pre>")
                in_code = True
            continue
        if in_code:
            body.append(ln.replace("&","&amp;").replace("<","&lt;"))
            continue
        if ln.startswith("|") and ln.endswith("|"):
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            tag = "td"
            if not in_table:
                body.append("<table>")
                in_table = True
                tag = "th"
            body.append("<tr>" + "".join("<%s>%s</%s>" % (tag, c, tag) for c in cells) + "</tr>")
            continue
        if in_table:
            body.append("</table>")
            in_table = False
        if ln.startswith("# "):
            body.append("<h1>%s</h1>" % ln[2:])
        elif ln.startswith("## "):
            body.append("<h2>%s</h2>" % ln[3:])
        elif ln.startswith("---"):
            body.append("<hr>")
        elif ln.strip() == "":
            body.append("")
        else:
            body.append("<p>%s</p>" % ln)
    if in_table:
        body.append("</table>")
    css = "body{font-family:Segoe UI,Microsoft YaHei,sans-serif;max-width:980px;margin:2rem auto;line-height:1.5;padding:0 1rem}table{border-collapse:collapse;width:100%;margin:1rem 0}th,td{border:1px solid #ccc;padding:.4rem .5rem;text-align:left}th{background:#f4f4f4}pre{background:#f6f6f6;padding:1rem;overflow:auto}"
    return "<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><title>%s</title><style>%s</style></head><body>\n%s\n</body></html>" % (title, css, "\n".join(body))

pairs = [
    ("UC01b_lessmesh_结果报告_v1.0", "UC-01b lessmesh 结果报告 v1.0", res_md),
    ("UC01b_lessmesh_1D_CFD契合性分析报告", "UC-01b lessmesh 1D与CFD契合性", fit_md),
]
for name, title, md in pairs:
    (root / (name + ".md")).write_text(md, encoding="utf-8", newline="\n")
    (root / (name + ".html")).write_text(md_to_html(title, md), encoding="utf-8", newline="\n")
    print(name, "md", (root / (name + ".md")).stat().st_size, "html", (root / (name + ".html")).stat().st_size)

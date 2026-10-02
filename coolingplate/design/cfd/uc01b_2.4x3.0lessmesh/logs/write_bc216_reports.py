# -*- coding: utf-8 -*-
from pathlib import Path
root = Path(r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh")

res_md = r'''# UC-01b lessmesh 结果报告 v1.0

**文档编号：** AIDC-B300-CFD-UC01b-LESS-RES-001  
**日期：** 2026-09-25  
**性质：** 当前设计点的运行记录。数字来自 `logs/fluent_cht_less_bc216.log`，iter 421。不是旧的 567460.32 W/m²、0.0002067 kg/s 场。

场：`fluent/uc01b_cht_less_bc216.cas.h5` / `.dat.h5`。网格：`mesh/uc01b_cht_less.msh`。

---

## 0. 状态

| 项 | 值 |
|---|---|
| 孔数 | 每颗 die **108**，两颗 **216**。单孔模型，进口区只有一个孔 |
| 胞尺寸 | Y（导流槽所在的跨槽方向）**2.4 mm**，X 沿槽 **3.0 mm**。孔距未压缩，未重划网格 |
| 热流 | `wall_heat` **579282 W/m²**（57.928 W/cm²） |
| 流量 | `inlet_jet`（单孔）**1.225×10⁻⁴ kg/s**。不是 ×108，也不是 ×216 |
| 入口温度 | 313.15 K |
| 网格 | **2115436** HEXA。边界层首层 2.5 μm，n_BL=10，增长 1.2，孔壁径向首层 3.0 μm |
| 求解 | 3ddp **-t4 -gpu**，桌面 GUI，无 `-g`。SST k-ω，能量，共轭。iter **421** 已收敛 |

---

## 1. 窗口为何关掉

求解在 iter 421 打印 `solution is converged`，并已写出 cas/dat。随后期刊执行

```
/report/fluxes/mass-flow yes inlet_jet return_slot () no
```

日志只吃进 `yes inlet_jet`，接着报错：

```
Error: Please answer y[es] or n[o].
Error Object: inlet_jet
```

期刊开头是 `/file/set-batch-options yes yes no`（遇错退出）。期刊里没有 `/exit`。窗口是在温度、热流、压力都打印完、场已保存之后，被这条质量流提示错误关掉的。不是发散，也不是 `fluent.exe` 路径错误。

---

## 2. 残差

```
   421  1.3775e-07  3.4445e-07  1.0778e-06  1.1785e-06  9.8449e-07  2.1453e-07  1.9775e-04
!  421 solution is converged
```

| 量 | iter 421 | 判据 |
|---|---|---|
| continuity | 1.378e-07 | < 1e-4 |
| x / y / z | 3.445e-07 / 1.078e-06 / 1.179e-06 | < 1e-4 |
| energy | 9.845e-07 | < 1e-6 |
| k / omega | 2.145e-07 / 1.978e-04 | < 1e-3 |

---

## 3. 工程量（216 孔口径）

q'' = 579282 W/m²。A_cell = 3.0×2.4 mm² = 7.20×10⁻⁶ m²。  
P_cell = **4.17083 W**。N = **216**。P_2die = **900.899 W**。T_in = 313.15 K。

| 量 | Fluent 打印 |
|---|---|
| T_in (`inlet_jet`) | **313.15 K** |
| T_out (`return_slot`，面积加权) | **320.993 K** |
| T_TIM 底 (`wall_heat`) | **342.096 K** |
| T_铜–水 (`wall_cu_fluid`) | **326.838 K** |
| T_TIM–铜 (`wall_tim_cu`) | **336.840 K** |
| 热流 (`wall_heat`) | **579282 W/m²** |
| P_in | **1091.51 Pa** |
| P_out | **0 Pa** |
| 静压 ΔP | **1091.51 Pa = 1.092 kPa** |

R(T_TIM−T_in)_2die = (342.09574−313.15)/900.899 = **0.03213 K/W**。单胞 **6.940 K/W**。已含 TIM、铜、对流，不要再加 R_TIM2、R_wall。  
R_conv,2die = (326.83835−313.15)/900.899 = **0.01519 K/W**。单胞 **3.282 K/W**。  
h(TIM 底) = q''/(T_TIM−T_in) = **2.001×10⁴**。h(铜–水，同一 q'') = **4.232×10⁴**，不是湿面局部对流系数。

R_wall（一维，A_2DIE=1512 mm²）= 0.003392 K/W。  
**R_c-in = (0.004–0.008)+0.003392+0.01519 = 0.02259–0.02659 K/W。**  
**R_j-in = (0.008–0.012)+R_c-in = 0.03059–0.03859 K/W。**

U = 0.9825 m/s，Re_D = **597**。低于 Martin 1977 的 Re≥2000，不引用 Martin h。  
T_out 是面积平均。ṁ cp ΔT_area / P_cell = **0.963**，不要当成能量已经闭合。

---

## 4. 和旧场的差别（旧场不是当前设计）

| | 旧 lessmesh iter 430 | i7900 | 本次 iter 421 |
|---|---|---|---|
| q'' | 567460.32 W/m² | 567460.32 W/m² | **579282 W/m²** |
| 单孔 ṁ | 2.067×10⁻⁴ kg/s | 2.067×10⁻⁴ kg/s | **1.225×10⁻⁴ kg/s** |
| 静压 ΔP | 2237.64 Pa | 2227.11 Pa | **1091.51 Pa** |
| T_TIM | 335.404 K | 335.428 K | **342.096 K** |
| T_铜–水 | 321.995 K | 322.087 K | **326.838 K** |

流量约为旧场的 0.59 倍，孔口动压约按速度平方降到大约 0.35 倍，所以压降从约 2.23 kPa 降到 1.09 kPa。热流只高 2%，TIM 底升高约 6.7 K，主要因为单孔流量变小、对流变弱。
'''

fit_md = r'''# UC-01b lessmesh 一维与 CFD 契合性分析报告

**文档编号：** AIDC-B300-CFD-UC01b-LESS-CMP-001  
**日期：** 2026-09-25  
**性质：** 对照记录。当前设计点是 216 孔、q''=579282 W/m²、单孔 ṁ=1.225×10⁻⁴ kg/s。CFD 是 lessmesh iter 421。旧的 567460.32 W/m² / 0.0002067 kg/s 和 i7900 不放进「当前设计」列。

相对差 = (CFD − 1D) / 1D。定义相同且约在 ±20% 内 → **接近**。定义不同 → **不可比**。Re&lt;2000、面积加权出口，标为 **限制**。

---

## 1. 口径

| 项 | 一维 / 设定 | 写入 Fluent 的值 |
|---|---|---|
| 孔数 | 每颗 108，两颗 216 | 网格是单孔单元胞。进口区名 `inlet_jet`，面积约 1.26×10⁻⁷ m²，等于 D=0.40 mm 一个圆孔 |
| 单孔流量 | 0.007407 L/min = **1.225×10⁻⁴ kg/s** | **1.225×10⁻⁴ kg/s** 写在 `inlet_jet`。总流量就是这个数，没有乘 108 或 216 |
| 热流 | 216 孔名义值加 5%，**579282 W/m²** | `wall_heat` 打印 **579282 W/m²** |
| 槽向胞 | Y = **2.4 mm**，不压缩孔距 | 网格 Y 从 −1.20 mm 到 +1.20 mm。X 沿槽 3.0 mm。未重划网格 |
| 入口温度 | 313.15 K | 313.15 K |
| 出口 | 压力出口表压 0，回流 313.15 K | `return_slot` 打印静压 **0 Pa**。`return_slot:015` 为邻铜壁面 |

P_cell = 579282×7.20×10⁻⁶ = **4.17083 W**。两 die 按 216 孔：P_2die = **900.899 W**。

一维孔口静压用与旧对比相同的 K=1.8：ΔP = 1.8×½ρU²。本流量 U=**0.9825 m/s**，Re_D=**597**，ΔP_1D=**862.0 Pa**。

---

## 2. 对照

| 项目 | 1D / 设定 | CFD iter 421 | 相对差 | 判断 |
|---|---|---|---|---|
| 入口温度 | 313.15 K | 313.15 K | 0 | 契合 |
| 单孔 ṁ | 1.225×10⁻⁴ kg/s | 设在单孔 `inlet_jet`，1.225×10⁻⁴ kg/s | 0 | 契合 |
| 热流 | 579282 W/m² | `wall_heat` 579282 W/m² | 0 | 契合 |
| 孔径 | D=0.40 mm | 圆孔 D=0.40 mm，2115436 HEXA，边界层保留 | 0 | 契合 |
| U | 0.9825 m/s | 由同一 ṁ 和 D 得到，与设定一致 | 0 | 契合 |
| Re_D | 597 | 597 | 0 | 契合。**限制：** &lt;2000，不用 Martin h |
| 静压 ΔP | 孔口 K=1.8：**862 Pa** | 1091.51−0 = **1091.51 Pa** | **+26.6%** | 超出约 ±20%。一维几乎只有孔口；CFD 含射流、槽和回液缝 |
| 能量温升 | P_cell/(ṁ cp)=**8.147 K**，出口 bulk **321.30 K** | 面积加权出口 320.993 K，温升 7.843 K | 温升 −3.7% | **限制。** 面积加权不是 bulk。Q 比 0.963 |
| R(T_TIM−T_in) | 一维不从共轭场取 TIM 底 | 342.096 K。两 die **0.03213 K/W** | 不可比 | 已含固体，不加 R_TIM2、R_wall |
| R_conv | Martin 在 Re=597 不适用 | (326.838−313.15)/900.899 = **0.01519 K/W** | 不可比 | 不是湿面局部 h |
| R_c-in | R_TIM2+R_wall 仍是假设 | 0.02259–0.02659 K/W（叠在本次 R_conv 上） | 不可与旧流量的 Martin 带比 | 旧带 0.01845–0.02245 属于更高流量 |
| R_j-in | 再加 R_pkg 0.008–0.012 | **0.03059–0.03859 K/W** | 假设叠加 | 设计未关闭 |

---

## 3. 差从哪里来

压降 CFD 比孔口一维高 230 Pa（+26.6%）。旧的高流量场里，CFD 静压（2.227 kPa）比同一 K=1.8 公式（2.454 kPa）低 9%。流量降到约 0.59 倍以后，孔口损失按速度平方降到 862 Pa，CFD 仍有槽道和回液缝，所以孔口公式偏低。这是路径不同，不是残差没收敛。

TIM 底 342.096 K 比旧高流量场的 335.4 K 高约 6.7 K。热流只从 56.746 W/cm² 增到 57.928 W/cm²（+2%），温升主要来自单孔流量减小。

能量比 0.963 用的是面积加权出口温度。和旧场一样，不能写成能量已经闭合，也不能据此把热阻写成设计已关闭。

---

## 4. 不用的数

不用 iter 430 / 547 的 2237.64 Pa、335.404 K，也不用 i7900 的 2227.11 Pa、335.428 K 当作本次设计结果。那些场的热流是 567460.32 W/m²，单孔流量是 2.067×10⁻⁴ kg/s。
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
            if set(cells[0].replace("-","")) == set() or all(set(c) <= set("-: ") for c in cells):
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
    (root/ (name+".md")).write_text(md, encoding="utf-8", newline="\n")
    (root/ (name+".html")).write_text(md_to_html(title, md), encoding="utf-8", newline="\n")
    print(name, "md", (root/(name+".md")).stat().st_size, "html", (root/(name+".html")).stat().st_size)

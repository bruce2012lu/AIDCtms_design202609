# UC-01b lessmesh ICEM / Fluent 结果报告 v1.0

**文档编号：** AIDC-B300-CFD-UC01b-LESS-RES-002  
**日期：** 2026-09-25  
**场：** `fluent/uc01b_cht_less_m425_bc216.cas.h5`（140055032 字节，13:37:13）与 `.dat.h5`（443504689 字节，13:37:24）。只有 iter 380。网格 4259680 HEXA。

TIM 底面积加权 **341.38529 K（68.24 °C）**。静压差 **1087.0927 Pa**。R(T_TIM−T_in)=**0.031341 K/W**。能量比 **0.952**，未闭合。

数字来自 `logs/fluent_cht_less_m425_gpu.log` 与 `mesh/cht_mesh_info_less.txt`。不是细网格 iter 8587，也不是 2115436 单元 iter 421。日志中没有 Error。切面极值未导出，不借用细网格的数。

---

## 1. 边界与收敛

| 量 | iter 380 |
|---|---|
| 阵列 | 9×12/die，两 die 216。D=0.40 mm。进口只有一个孔 |
| 网格 | `mesh/uc01b_cht_less.msh`，11:42。2055516 + 2083716 + 120448 = **4259680** HEXA。Y 向 2.4 mm，孔心未移动 |
| 施加 q'' | **579282 W/m²（57.928 W/cm²）**，216 胞 900.899 W |
| ṁ | **1.225×10⁻⁴ kg/s**（期刊设定；质量流量积分未再打印）。不是 ×108 或 ×216 |
| 入口 / 回流 | 313.15 K。`return_slot` 表压 0。`return_slot:015` 为壁面 |
| 求解 | SST k-ω，能量，共轭。3ddp -t4 -gpu，RTX 4090 |
| 残差 | `6.2412e-07  6.2793e-07  1.9747e-06  2.6352e-06  9.9059e-07  1.1046e-06  1.6245e-04`，solution is converged |
| 静压差 | 入口 1087.0927 Pa，出口 0 |

## 2. 温度

| 面 | iter 380 |
|---|---|
| TIM 底 wall_heat | 面积加权 **341.38529 K**；本面 341.375–341.394 K |
| TIM 中面 z=−2.0364 mm | 338.991–339.010 K |
| TIM–Cu | 面积加权 **336.13005 K**；切面 336.120–336.139 K |
| 铜座中面 z=−1.028 mm | 334.638–334.725 K |
| 铜–水整个界面 | **326.59968 K** |
| 铜–水底面 z=0 | 332.485–333.538 K |
| 出口 | 面积加权 **320.90984 K**；面上 318.693–322.009 K |
| 入口 | **313.15 K** |
| 出口温升 / 能量温升 | 7.75984 / 8.14731 = **0.952**，未闭合 |

![TIM bottom](figs/m425_wall_heat_T.png)

![TIM mid](figs/m425_ztim_mid_T.png)

## 3. 热阻

R(T_TIM−T_in)=(341.38529−313.15)/900.899=**0.031341 K/W**。不再加 R_TIM2 与 R_wall。单胞 6.770 K/W。

| 定义 | 两 die |
|---|---|
| R(T_TIM−T_in) | **0.031341 K/W** |
| R_conv | **0.014929 K/W** |
| R_c-in | **0.022321–0.026321 K/W** |
| q''/(T_TIM−T_in) | 2.052×10⁴ W/(m²·K) |
| q''/(T_cu−water−T_in) | 4.307×10⁴ W/(m²·K) |

两条链不能相加。Re_D=597 &lt; 2000，不引用 Martin。

## 4. 速度与 Re

U=ṁ/(ρ·π·D²/4)=**0.9825 m/s**。Re_D=**597.1**。各切面 |V|max 未导出。

| 切面 | 水温度 | \|V\|max |
|---|---|---|
| z=0.750 mm | 未导出 | 未导出 |
| z=2.500 mm | 未导出 | 未导出 |
| z=4.711 mm 圆孔 | 未导出 | 未导出 |
| Y=0 | 未导出 | 未导出 |
| Y=0.800 mm | 未导出 | 未导出 |
| X=0 | 未导出 | 未导出 |
| X=0.556 mm | 未导出 | 未导出 |
| 回液缝入口 | 未导出 | 未导出 |
| 回液缝中段 | 未导出 | 未导出 |
| 出口 | 面积加权 320.90984 K | 未导出 |

未导出、因此不写：热流云图、总压差、GCI、y+、质量流量积分。

## 5. 云图

全部为 iter 380，`figs/m425_*.png`，不是细网格的 `n216_i8587_*.png`。槽中水取最近平面 z=0.674 mm，圆孔取 z=4.750 mm。

![TIM-Cu](figs/m425_ztimcu_T.png)
![copper mid](figs/m425_zcu_mid_T.png)
![floor](figs/m425_z0_T.png)
![rib mid](figs/m425_zrib_mid_T.png)
![rib top](figs/m425_zrib_solid_T.png)
![orifice slots](figs/m425_zorif_slot_vel.png)
![slot](figs/m425_zmid_TV.png)
![gap](figs/m425_zgap_TV.png)
![orifice](figs/m425_zorif_TV.png)
![slit](figs/m425_slitin_TV.png)
![return mid](figs/m425_zreturn_mid_TV.png)
![outlet](figs/m425_return_TV.png)
![Y0](figs/m425_y0_TV.png)
![Y side](figs/m425_yside_TV.png)
![X0](figs/m425_x0_TV.png)
![X mid](figs/m425_xmid_TV.png)

## 6. 网格剖面（不是温度）

来源 `mesh/uc01b_cht_less.msh`，4259680 HEXA，底面四边形 30112。首层 0.0025 mm，10 层。孔外过渡 0.080 mm，缝唇外 0.0675 mm，槽芯 Y 0.045 mm，肋芯 0.068 mm。

![mesh TIM](figs/m425_mesh_wall_heat.png)
![mesh floor](figs/m425_mesh_z_floor.png)
![mesh rib](figs/m425_mesh_z_rib.png)
![mesh orifice](figs/m425_mesh_z_orifice.png)
![mesh X0](figs/m425_mesh_x0.png)
![mesh Y0](figs/m425_mesh_y0.png)
![mesh BL](figs/m425_mesh_y0_bl.png)

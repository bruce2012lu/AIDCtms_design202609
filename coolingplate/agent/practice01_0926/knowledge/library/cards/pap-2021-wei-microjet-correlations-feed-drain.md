---
id: pap-2021-wei-microjet-correlations-feed-drain
trust_level: L2
verified_from: fulltext（公式已对照 p.11 页面图像）
last_verified: 2026-10-02
stages: [3, 4, 5]
benchmark_candidate: true
---

# Wei et al. 2021 · 交替进排液微射流的 Nu 与压降关联式

Wei, T., Oprins, H., Fang, L., Cherman, V., Beyne, E., Baelmans, M. "Heat transfer and pressure drop correlations for direct on-chip microscale jet impingement cooling with alternating feeding and draining jets." *Int. J. Heat Mass Transfer* 182 (2022) 121865，在线 2021-10-01。DOI 10.1016/j.ijheatmasstransfer.2021.121865。imec / KU Leuven。

本地文件：`files/papers/pap-2021-wei-microjet-correlations-feed-drain.pdf`（作者课题组主页副本，出版社排版版，`redistributable=false`）。

## 为什么重要

这是目前入库全文里唯一同时覆盖本项目射流雷诺数（约 290–600）、给出 Nu 与压降两套关联式、并有实验验证的来源。它的拓扑是“进液孔与排液孔交替布置”（分布式出口），和本项目“射流 + 短槽就近抽走”同属抑制交叉流的一类，比 Martin 1977 的边缘出口阵列更接近。

## 关键公式

面平均 Nusselt 数（Eq.(19)，p.11，±30 %）：

\[
\overline{Nu}_f=\Big(5.64\,a^2+0.031\,a-0.000632\Big)\Big(\tfrac{H}{L}\Big)^{-0.29} Re_d^{\,0.48\,a^{-0.16}},\qquad a=\tfrac{d_i}{L}=\tfrac{d_o}{L}
\]

适用：\(0.01\le a\le0.4\)，\(0.01\le H/L\le0.4\)，\(32\le Re_d\le2048\)，\(0.05\le H/d_i\le20\)，\(0.01\le t/L\le0.4\)。Pr 固定 7.56（去离子水，p.5）。

定义（Eq.(2)、(4)，p.5）：\(Nu_f=\dfrac{q\,d_i}{(T_s-T_{in})\,k_{fl}}\)，q 按芯片面积，\(T_s\) 为固液界面平均温度，参考温度是**进口温度**；\(Re_d=\rho d_i V_{in}/\mu\)。

压降系数（Eq.(20)，p.11，±30 %）：

\[
k=\Big(21.2\,a+14.5\Big)Re_d^{-0.73\,a^{-0.26}}\Big(2.26\tfrac{t}{L}+0.89\Big)\Big(0.37\,(\tfrac{H}{L})^{0.15}+0.55\Big)+0.8,\qquad k=\frac{\Delta P}{\tfrac12\rho\bar V_{in}^2}
\]

适用：\(0.05\le a\le0.6\)，\(0.5\le H/d_i\le20\)，\(32\le Re_d\le1024\)，\(t/L\ge0.1\)。**原文排版中 “0.15” 的位置有歧义**（可能是指数，也可能是系数），使用前需向作者或期刊勘误确认；本库 `tools/correlations.py` 暂未实现 Eq.(20)。

## 物理结论（可直接用于设计判断）

- 0.3 ≤ H/L < 1 时 H/L 对 Nu_f 影响很小；H/L < 0.1 进入 “pinch-off” 通道流区，压降骤增（p.10，Fig.8–9）。
- Re 指数随 d_i/L 变化，b 一般 0.5–0.8（p.2–3）。
- 单元胞 CFD 用 SST k-ω，边界层 15 层，GCI 评估驻点温度离散误差 0.2 %（p.4）——这是本项目 UC-01b 应该达到的报告方式。

## 验证数据

| 样件 | d_i 实测 | d_i/L | H/L | 来源 |
|---|---|---|---|---|
| 3D 打印 3×3 | 0.95 mm | 0.36 | 0.33 | Table 3 p.12 |
| 3D 打印 4×4 | 0.75 mm | 0.375 | 0.33 | Table 3 p.12 |
| 3D 打印 8×8 | 0.38 mm | 0.38 | 0.33 | Table 3 p.12 |
| Brunschwiler 硅冷却器 19044 孔 | 0.043 mm | 0.287 | 0.33 | Table 3 p.12，原始数据见 Brunschwiler 2006 |

工质去离子水，流量计 ±0.2 % 读数，压差计 < ±0.5 % 满量程，热测量合成不确定度 ±1.8 %（p.11）。Nu–Re 实测点只在 Fig.14/15，需要数字化后才能当基准。

## 对本项目

用 `tools/correlations.py wei` 算（L = √(Sx·Sy) = 2.683 mm，H = 2.0 mm）：

| 工况 | Re | Nu_f（原式，水） | 是否在域内 |
|---|---|---|---|
| 水基线 v2.0，D0.50，1.60 L/min | 478 | 10.5 | d_i/L、Re、H/d_i 在内；**H/L = 0.745 超上限 0.4**；Pr 4.34 ≠ 7.56 |
| PG25 v2.1 设计点，D0.50，2.283 L/min（内部物性） | 399 | 9.4 | 同上，Pr 9.9 |
| 同上，Dow LC 0623 物性（二手） | 290 | 7.7 | 同上，Pr 13.0 |

按平板靶面、2 × 27 × 28 mm 投影面积换算，对流热阻约 0.060–0.071 °C/W。内部 v2.0 短槽模型给 0.0252 °C/W（水），UC-01b 单元胞 CFD 折算约 0.033 °C/W。差距要靠短槽的湿润面积放大（v2.0 记为 4.25 倍、肋效率 0.948）来解释；这一放大量没有外部实验支撑，需要 CFD 网格收敛与 TTV 实测闭合。

## 注意

- 出口拓扑不同：本项目没有排液孔，靠短槽横向抽走；Wei 的 d_o 项在本项目里没有对应物。
- H/L 与 Pr 都在域外，结果只能当量级交叉核对，不能写进保证值。
- id 年份用在线发表年 2021，卷期年 2022。

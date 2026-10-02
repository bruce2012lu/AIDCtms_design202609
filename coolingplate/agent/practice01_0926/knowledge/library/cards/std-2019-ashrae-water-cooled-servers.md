---
id: std-2019-ashrae-water-cooled-servers
trust_level: L2
verified_from: fulltext
last_verified: 2026-10-02
stages: [1, 2, 6, 7, 8]
benchmark_candidate: false
---

# ASHRAE TC 9.9 · Water-Cooled Servers: Common Designs, Components, and Processes（2019）

ASHRAE TC 9.9 白皮书，ASHRAE 官网免费下载。委员会白皮书，不是标准，记 L2；它引用的水质表原始出处是付费的 *Liquid Cooling Guidelines for Datacom Equipment Centers* 第 2 版（ASHRAE 2014）Table 6.1/6.2（条目 std-2014-ashrae-lc-guidelines-2ed）。

## 关键表

`tables/std-2019-ashrae-water-cooled-servers__tcs_water_quality.csv`（PDF p.24）。TCS（冷板侧回路）要点：

| 参数 | TCS |
|---|---|
| pH | 8.0–9.5 |
| 硫化物 / 硫酸盐 / 氯化物 | < 1 / < 10 / < 5 ppm |
| 细菌 | < 100 CFU/mL |
| 总硬度（CaCO₃） | < 20 ppm |
| 电导率 | 0.2–20 µS/cm |
| 悬浮物 / 蒸发残渣 / 浊度 | < 3 ppm / < 50 ppm / < 20 NTU |

## 过滤规则（PDF p.25）

> TCS 回路绝对过滤精度应比 IT 冷却设备里最细的流道尺寸小 7–10 倍；必须用绝对过滤等级，不是名义等级。

## 对本项目

- 最细流道：GPU 射流孔 0.40 mm、GPU 短槽宽 0.40 mm、HBM 槽宽 0.40–0.45 mm（随方案）。按 7–10 倍：绝对过滤 40–57 µm 量级。
- 内部 `cad/coldplate/rules.py` 的“过滤粗于孔径 1/10 → ERROR”落在 ASHRAE 规则的严格端，**被支持**。
- 这张水质表针对水基 TCS；PG25 的 pH 区间不同（OCP PG25 指南 pH 8.0–10.5，条目 std-2022-ocp-pg25-guidelines），不要混用。
- Lenovo LP2018 写在线过滤 50 µm；CoolIT CHx2000 写 25 µm。两者与本规则结合，0.40 mm 孔需要 ≤ 40–57 µm，50 µm 刚好在边缘，选 25 µm 更稳。

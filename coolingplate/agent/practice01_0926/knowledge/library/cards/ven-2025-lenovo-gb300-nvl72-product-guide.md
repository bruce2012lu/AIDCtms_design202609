---
id: ven-2025-lenovo-gb300-nvl72-product-guide
trust_level: L3
verified_from: fulltext（2026-10-02 下载版逐页核对）
last_verified: 2026-10-02
valid_until: 2027-03-31
stages: [1, 2, 3, 4, 8]
benchmark_candidate: false
---

# Lenovo Press LP2357 · NVIDIA GB300 NVL72 by Lenovo 产品指南

Lenovo Press LP2357，`https://lenovopress.lenovo.com/lp2357.pdf`。厂商官方产品指南，网页会改版，`valid_until` 设一年内。

## 关键数据

| 量 | 值 | 位置 |
|---|---|---|
| 整柜功率 | 135 kW TDP；峰值至 155 kW（取决于负载与 EDP） | p.2、p.24 |
| 液 / 风分担 | 约 90 % 液冷、10 % 风冷 | p.2、p.24 |
| B300 SXM TGP（Lenovo DLC） | 1100 W | p.19 GPU 规格表 |
| HBM | 288 GB HBM3e / 7.7 TB/s | p.19 |
| 工质 | 去离子水（推荐，出厂不带水）或 PG25 | p.24 |
| 非运行温度 | 带 DI 水 5–70 °C；带 PG25 10–70 °C | p.38 |
| 整柜供液温度–流量–压降 | 见下表 | p.38 Table 27 |
| NVL 交换托盘运行水温 | 2–50 °C（ASHRAE W45） | p.38 |

`tables/ven-2025-lenovo-gb300-nvl72-product-guide__table27.csv`：

| 供液温度 | 25 °C | 30 °C | 35 °C | 40 °C | 45 °C |
|---|---|---|---|---|---|
| 所需整柜流量 L/min | 59 | 71 | 89 | 119 | 177 |
| 整柜压降 psi（kPa） | 2.3（15.9） | 3.2（22.1） | 4.9（33.8） | 8.5（58.6） | 18.4（126.9） |

表 27 没有注明工质，也没有给单板或单 GPU 流量。

## 对本项目

- 支持内部 v2.0/v2.1 的：1100 W（Lenovo 口径）、135/155 kW、25–45 °C ↔ 59–177 L/min、16–127 kPa、DI 水或 PG25、供液最高 45 °C。
- 需要说明的口径差：NVIDIA Blackwell Ultra datasheet p.5 写 GB300 NVL72 形态“TDP configurable up to 1,400 W”，HGX B300 形态“up to 1,100 W”。Lenovo 在 GB300 NVL72 里写 1100 W。所以“1100 W 保证点”只有 Lenovo 支撑，“1400 W 包络”有 NVIDIA 支撑。
- 用项目 140 kW 和 PG25 物性反算表 27 的 177 L/min 得到温升约 12 °C，是内部算术，不是表上数据（v2.1 §6 已如此表述）。

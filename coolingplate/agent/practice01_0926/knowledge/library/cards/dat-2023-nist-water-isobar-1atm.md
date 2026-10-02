---
id: dat-2023-nist-water-isobar-1atm
trust_level: L1
verified_from: fulltext
last_verified: 2026-10-02
stages: [3, 4, 5, 7]
benchmark_candidate: true
---

# NIST WebBook · 水 1 atm 等压物性 20–80 °C

NIST Chemistry WebBook SRD 69，Thermophysical Properties of Fluid Systems（IAPWS-95 状态方程，IAPWS 粘度与导热公式）。本地是 2026-10-02 的 TSV 快照。

## 关键表

`tables/dat-2023-nist-water-isobar-1atm__20-60C.csv`。40 °C：

| ρ kg/m³ | cp kJ/(kg·K) | μ Pa·s | k W/(m·K) | Pr |
|---|---|---|---|---|
| 992.216 | 4.17941 | 6.52729 × 10⁻⁴ | 0.628486 | 4.341 |

## 对本项目（内部 v2.0 水基线 40 °C）

| 量 | 内部 | NIST | 偏差 |
|---|---|---|---|
| ρ | 992.2 | 992.216 | 0.0 % |
| cp | 4179 | 4179.41 | 0.0 % |
| μ | 6.53 × 10⁻⁴ | 6.527 × 10⁻⁴ | +0.04 % |
| k | 0.631 | 0.6285 | +0.4 % |
| Pr | 4.32 | 4.34 | −0.5 % |

结论：水基线物性**被支持**。Fluent 材料库若用默认 water-liquid（常温常数），应改成本表 40 °C 值或温度多项式。

这张表也是 PG 水溶液物性回归的 0 % 浓度端点。PG25 物性另有专题报告（`docs/knowledge/PG25物性溯源与推荐_20261002.md`，由其他任务撰写），本卡不重复。

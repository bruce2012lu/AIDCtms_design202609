---
id: pap-2020-wei-3d-printed-jet-large-die
trust_level: L2
verified_from: fulltext（几何与主要结果 p.1–2 已核对；R 与 ΔP 取自检索子任务摘录，引用前复核 p.3–4）
last_verified: 2026-10-02
stages: [3, 4, 5, 7]
benchmark_candidate: true
---

# Wei et al. ECTC 2020 · 大 die 封装级 3D 打印射流冷却器实测

"Demonstration of Package Level 3D-printed Direct Jet Impingement Cooling applied to High-power, Large Die Applications." IEEE ECTC 2020（imec）。本地为作者课题组主页副本，不可分发。

## 为什么重要

公开文献里几何最接近 B300 的射流冷板实测：大 die、上百孔、进排液交替、实测热阻与压降、有热测试芯片。可作本项目一维工具和 CFD 的“同类器件”量级基准。

## 几何与工况

| 项 | 值 | 位置 |
|---|---|---|
| 热测试芯片 | 23 × 23 mm²，16 个加热区，25 个测温点；封装基板 55 × 55 mm² | p.2 |
| 进液阵列 / 排液阵列 | 11 × 11 / 12 × 12（排液孔分布在进液孔之间） | p.2 |
| 孔距 / 孔径 | 2 mm / 0.6 mm（进、排相同） | p.2 Table 1 |
| 腔高（喷嘴到芯片） | 0.6 mm | p.2 Table 1 |
| 冷却器外形 | 55 × 55 × 17.5 mm³，O 形圈密封 | p.2 |
| 加热功率 | 250–285 W（随芯片温度），50 V | p.2 |
| 工质 | 去离子水 | — |

## 结果

| 量 | 值 | 位置 |
|---|---|---|
| 芯片温升 | 17.5 °C @ 285 W、3.25 L/min（摘要）；正文按 275 W 记 | p.1；正文 |
| 压降 | 约 0.7 bar @ 3.25 L/min | 检索子任务摘录，p.3 |
| 热阻 | 0.14 K/W @ 1 L/min | 检索子任务摘录，p.4 |
| 温度不均匀度 | 约 6 % | 检索子任务摘录 |

由 17.5 °C / 285 W 得 R ≈ 0.061 K/W（芯片平均温度到进口，含硅导热与扩散），面积归一化约 0.32 cm²·K/W。

## 对本项目

- 本项目是铜冷板 + TIM2 + 封装盖，不是裸 die 直冲，热阻链更长；不能直接比 R 绝对值。可比的是“单位面积对流 + 扩散”的量级与流量–压降曲线的形状。
- 本项目 d/L ≈ 0.19、H/L ≈ 0.75；该样件 d/L = 0.3、H/L = 0.3。
- 作为基准 BM-JET-02 登记在 `registry/benchmarks.json`，状态 `needs_fulltext_check`（R 与 ΔP 需对原页复核后改为 ready）。

---
id: pap-2009-whelan-nozzle-geometry-jet-array
trust_level: L2
verified_from: fulltext（Eq.(1)(2) 已对照 p.10 页面图像）
last_verified: 2026-10-02
stages: [3, 4, 7]
benchmark_candidate: true
---

# Whelan & Robinson 2009 · 液体射流阵列的喷嘴几何效应（含 Robinson & Schnitzler 关联式）

Whelan, B.P., Robinson, A.J. "Nozzle geometry effects in liquid jet array impingement." *Applied Thermal Engineering* 29 (2009) 2211–2221。DOI 10.1016/j.applthermaleng.2008.11.003。本地是 HAL 上的作者接受稿（hal-00511424）。

## 关键公式（转引 Robinson & Schnitzler 2007，原文付费，条目 pap-2007-robinson-schnitzler-jet-array）

自由表面射流阵列（Eq.(1)，p.10）：

\[
\frac{Nu_L}{Pr^{0.4}}=7.8\,Re_{d_n}^{0.49}\exp\!\Big(-0.025\,\frac{S}{d_n}\Big)
\]

受限淹没射流阵列，\(2\le H/d_n\le3\)（Eq.(2)，p.10）：

\[
\frac{Nu_L}{Pr^{0.4}}=23.39\,Re_{d_n}^{0.46}\Big(\frac{S}{d_n}\Big)^{-0.442}\Big(\frac{H}{d_n}\Big)^{-0.00716}
\]

原实验范围（p.10）：水，\(d_n=1\) mm，\(3\le S/d_n\le7\)，\(2\le H/d_n\le30\)，\(650\le Re_{d_n}\le6500\)。\(Nu_L\) 以加热面特征长度为基准，不是孔径。

## 实验结论

- 淹没射流在 2 ≤ H/d ≤ 3 时换热对喷距不敏感；5 ≤ H/d ≤ 20 单调下降（p.10）。
- 喷距较小时，换热对孔间距更敏感；减小孔间距（增加孔数）在给定换热下降低泵功（p.10）。
- 本文 6 种喷嘴（直孔、倒角、圆滑入口/出口），45 孔，d = 1 mm，S/d = 5，受限淹没 H/d = 2，800 ≤ Re ≤ 10000（p.12）。锐边与圆滑喷嘴在同等泵功下优于直孔（Royne & Dey 结论，p.11）。
- Nu 不确定度 5–7 %，摩擦系数 10–20 %（据检索子任务摘录，p.41 附近，引用前复核）。Nu–Re、f–Re 曲线在 Fig.3/4，需数字化。

## 对本项目

| 量 | 本项目 | 本式范围 | 判定 |
|---|---|---|---|
| Re | 290–600 | 650–6500 | 低于下限 |
| S/d | 4.8–7.5 | 3–7 | 基本在内 |
| H/d | 4–5 | 2–3（淹没式 Eq.2） | 超出 |
| 出口 | 短槽就近抽走 | 边缘排液（交叉流） | 拓扑不同 |

结论：只能作趋势参照（孔间距、喷距的影响方向），不能直接给本项目的 h。它是喷嘴入口倒角能降压降的证据，对 ⑥ 机械图纸里孔口倒角的取舍有用。

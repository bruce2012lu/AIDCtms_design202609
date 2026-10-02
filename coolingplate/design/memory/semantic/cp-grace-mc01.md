---
confidence: 0.7
valid_until: 2027-03-31
last_verified: 2026-09-28
expired: false
---

# CP-GRACE-MC-01

工作目录在 `agents/AIDCtms/coolingplate/design`。2026-09-28 起，流路改为沿 Y 交错。报告坐标：+X 从左接头到右接头，+Y 朝后面板，+z 从芯片面指向盖板。

## 锁定口径

- 对象：Lenovo GB300 计算托盘上的一颗 Grace。每块 NVL2 一颗，托盘两块。300 W TDP **含 LPDDR5X**（Lenovo Press LP2357）。
- 设计分工：CPU 260 W / 内存合计 40 W，总和仍是 300 W。
- 方案：两层铜，无微射流。型号仍是 CP-GRACE-MC-01。材料 C11000/TU1。
- 槽仍沿 Y。从左数，奇数槽流向 +Y，偶数槽流向 −Y。Y 向两端用铜墙封死，冷却液从 Z 向口进出。左右接头仍水平。
- 流量 0.55 L/min。CPU 48 × 0.40 × 1.20 mm，节距 0.80，润湿长 40 mm，受热 32 mm。核算：0.34 m/s，Re 310，通道压降 0.96 kPa。
- 一维配对模型：同向时铜底沿 Y 相差约 4.1 K；交错后约 0.2 K。对流温升仍约 12 K。这是筛算，不是 CFD。
- 每侧内存 6 条 1.20 × 0.80 mm，同样奇偶反向，润湿长 78 mm。每侧一条 0.80 × 1.20 mm、长 12 mm 的缝，放在该侧供液分到前后端之前。
- 入口孔板仍是 4 × Ø1.04 mm，支路配到约 10 kPa。
- 外形 200 × 120 × 8.0 mm 和窗口仍是候选。左右干管局部加深到 z 1.0–6.0。
- `out/grace/step` 里已有的 STEP 是改流路之前的同向模型。源码 `make_grace_concept.py` 已改，本机没有 build123d，没有重新导出。

## 文件

- 报告 `NVIDIA_Grace_GB300_冷板详细设计报告_v1.0_20260926.html`（2026-09-28 修订，图以报告内 SVG 为准）
- 概念几何 `make_grace_concept.py`
- 核算 `CP-GRACE-MC-01_calc.py`
- 来源 `参考_GB300_Grace_CPU与液冷边界_20260926.html`

`cfd_grace_cpu` 的网格是同向单槽，不能当作这一版的证据。

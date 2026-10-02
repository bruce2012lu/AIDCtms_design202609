---
id: ven-2025-nvidia-blackwell-ultra-datasheet
trust_level: L3
verified_from: fulltext
last_verified: 2026-10-02
valid_until: 2027-03-31
stages: [1, 2, 3]
benchmark_candidate: false
---

# NVIDIA Blackwell Ultra Datasheet

NVIDIA 官方数据表（NVIDIA DAM 公开链接）。厂商 L3。

## 关键数据（p.5 技术规格表）

| 量 | GB300 NVL72 形态 | HGX B300 形态 |
|---|---|---|
| Max TDP | Configurable up to 1,400 W | Configurable up to 1,100 W |
| GPU 显存 / 带宽 | 279 GB HBM3E / 8 TB/s | 270 GB HBM3E / 7.7 TB/s |

p.2：GB300 NVL72 为全液冷机架级架构，72 颗 Blackwell Ultra GPU + 36 颗 Grace CPU。

## 对本项目

- 1400 W 基线由 NVIDIA 一手文档直接支持（GB300 NVL72 形态）。
- NVIDIA 的 1100 W 对应 HGX B300，不是 GB300。内部 v2.0 把“DP-A 1100 W”标为“Lenovo TGP”是正确的出处，但不应写成 NVIDIA 对 GB300 的额定值。
- 显存口径：内部写“288 GB（数据手册另有 279 GB）”。NVIDIA datasheet 是 279 GB（GB300），Lenovo LP2357 是 288 GB。两者都有出处，按冷板设计无影响，但 HBM 堆叠数与布置要以官方封装图为准。
- 不含：封装外形、die/HBM 坐标、power map、结温上限、冷板流量与压降。这些在 NDA 热设计指南里（条目 ven-0000-nvidia-gb300-thermal-design-guide，login_required）。

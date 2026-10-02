---
confidence: 0.9
valid_until: 2027-03-31
last_verified: 2026-09-26
expired: false
---

# 四条 CAD 轨道

参数化内核、实测 STEP、Grace 概念、托盘示意是四份几何。2026-09-26 起，只有参数化内核接上了 `cad_inspect` / `cad_build`。

- 内核锁 v1.0：128 × D0.50，单一节距 3.0 mm，8.5 mm，三件（底板、喷嘴板、密封框）。入口 `cad/build.py`，AI 入口 `agent/practice01_0926/mcp/server.py`。
- asm_0921 是 12.5 mm 三层板，128 × D0.50，有静压箱，无水嘴。时间晚于 v2，喷嘴口径仍是 v1。只解释，不回写 yaml。
- v2 文字与 UC-01b 是 216 孔、D0.40、Y 节距 2.4 mm。内核缺少 `pitch_x/pitch_y`，所以还不能建。
- Grace 是平行微通道，无射流，脚本在 `design/make_grace_concept.py`。俯视加粗肋不是加工尺寸。

孔轴读取、OCC 共面切除、段错误重试、venv 与系统 Python 分离，见 `environment.md`。

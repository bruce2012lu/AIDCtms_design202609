---
confidence: 0.75
valid_until: 2027-03-31
last_verified: 2026-09-26
expired: false
---

# Grace 与托盘

Grace 型号 CP-GRACE-MC-01，工作目录在 `design/`，不放进 `cad/` 的 B300 结果。300 W TDP 含 LPDDR5X。设计分工 CPU 260 W、内存合计 40 W。两层铜，平行微通道，无微射流。流量 0.55 L/min，包络 0.70。CPU 槽 48 × 0.40 × 1.20 mm，节距 0.80，长 32 mm。外形 200×120×8 mm 仍是候选。左进右出，一种手性。壳–进液 < 0.080 °C/W 是一维加 TIM 余量，不是 CFD。

一块 asm_0921 冷板对应一颗 B300。整托盘 4 块 GPU 冷板 + 2 块 Grace。后面板单进单出。四块 GPU 的串并联照片不足以证实，水力 ICD 未到。推荐摆放：芯片朝下，进液边朝后面板。圆管转接和中线回液还不是 STEP 特征。

详细原文：`design/memory/semantic/cp-grace-mc01.md`，`cad/memory/semantic/asm_0921-三层铜冷板结构.md`。

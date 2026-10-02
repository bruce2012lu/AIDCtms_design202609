# 参数化 CAD 内核缺口

confidence: 0.9
valid_until: 2027-03-31
last_verified: 2026-09-26

`cad/coldplate` 已经是分层程序（参数、派生、规则、实体、后端），但在 2026-09-26 之前没有智能体入口：不能由对话选定轨道、不能在建模前拒绝不存在的字段、也不能把候选几何和冻结 yaml 隔开。`agent/practice01_0926/mcp/server.py` 补的是这一层。内核本身仍然只表达 v1.0。

## 现在能建的

- 外形 95 × 75 × 8.5 mm
- 零件 JM01-100 底板、JM01-200 喷嘴板、JM01-400 密封框
- 孔数 = die 数 × `count_x` × `count_y`，单一 `jets.pitch`
- 冻结点：128 孔、D0.50、S/D = 6、H/D = 4、GPU 1.60 L/min、HBM 0.40 L/min

规则在 `cad/coldplate/rules.py`。ERROR 包括尺寸链不闭合、余铜 < 1.8 mm、孔径 < 0.30 mm、齿壁 < 0.30 mm、槽深宽比 > 5、射流阵越出 die、跨 NV-HBI、HBM 流速超过 0.80 m/s、过滤粗于孔径 1/10、分流或功率加总对不上。与 v1.0 数字不符是 WARN，不是自动改报告。

## 现在不能建的

| 想要的几何 | 为什么当前 yaml 表达不了 |
|---|---|
| v2 / UC-01b：每 die 9×12 = 108，两 die 216，D0.40，X 节距 3.0、Y 节距 2.4 | 只有一个 `jets.pitch`。把节距改成 2.4 会连 X 一起改；孔数改成 9×12 且节距仍为 3.0 时，Y 向阵面超出 28 mm die，`JET_ARRAY_OFF_DIE` |
| asm_0921：12.5 mm，PLATE / COVER1 / COVER2，独立静压箱 | 内核是 8.5 mm 的底板 + 喷嘴板 + 密封框，没有 COVER2 |
| Grace 48 条平行槽、无喷嘴 | 另一套脚本 `design/make_grace_concept.py`，没有共用 Spec |
| 水嘴、中线回液、UQD | 两条 CAD 轨道都还没有这些特征 |

下一轮若要把 v2 接进内核，先加 `pitch_x` / `pitch_y`，并让 `rules.REPORT_REFERENCE` 指向 v2 数字，而不是改写 v1 对账表。在那之前，`cad_inspect` 遇到 `jets.pitch_x` 这类字段会拒绝，不会静默丢掉。

## 调用顺序

1. `cad_tracks` 选定 `parametric-v1`
2. `cad_inspect`，需要时带 overlay
3. 人确认门状态
4. `cad_build` 且 `confirm=true`，产物在 `agent/practice01_0926/runs/<时间戳>/`

冻结文件 `cad/params/cp_b300_jm01.yaml` 保持不动。

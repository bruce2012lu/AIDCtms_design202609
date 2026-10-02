---
name: cad-loop
description: 冷板 CAD 的智能体循环。改几何、出 STEP、解释 asm_0921 或 Grace 概念图时使用。先选轨道，再规则门，最后才建模。
---

# CAD 循环

启动时读 `agent/practice01_0926/knowledge/cad-tracks.json` 和 `agent/practice01_0926/knowledge/cad-kernel-gap.md`。

## 步骤

1. 用一句话声明轨道：`parametric-v1`、`measured-asm0921`、`grace-concept`、`tray-schematic` 之一。
2. 只有 `parametric-v1` 可以改数。调用 MCP `cad_inspect`。不要手改 `cad/params/cp_b300_jm01.yaml`。
3. 读 `gate`：
   - `block`：有 ERROR，或出现内核没有的字段。说明哪条规则，停止建模。
   - `warn`：已偏离 v1.0 对账。向人说明差异，得到确认后才 `allow_warn=true`。
   - `pass`：可以导出。
4. 导出用 `cad_build`，`confirm` 必须为 true。后端优先 `preview` 或 `drawing`；需要交接给 CFD / 供应商时再用 `neutral`。
5. 产物只出现在 `agent/practice01_0926/runs/`。把本次 overlay、gate、文件路径写入 `agent/practice01_0926/memory/episodic/`。

## 轨道禁令

- 用 v1 yaml 去“还原”asm_0921。厚度栈和零件数都不同。
- 把 Grace 槽宽、流量写进 B300 射流参数。
- 把俯视概念图里加粗的肋当成 0.40 mm 真槽。局部图和 `make_grace_concept.py` 的 `closeup()` 才是设计节距。
- 孔轴用 build123d 的 `center()`。asm_0921 记忆写明要取圆柱面包围盒中点。
- 在系统 Python（VeighNa）里安装 OCP。CAD 依赖在 `cad/.venv`。
- 切除体与被切面共面。内核已留过切；新特征继续留过切。OCC 约有间歇段错误，导出失败先重试。

## 人确认后再做

- 把 v2 的 216 孔 / D0.40 / 2.4×3.0 写进参数化内核
- 覆盖 `cad/out` 里已有 STEP
- 给 asm_0921 补水嘴并当作可加工发放图

---
confidence: 0.9
valid_until: 2027-03-31
last_verified: 2026-09-27
expired: false
---

# 本机环境

- CAD venv：`cad/.venv`（build123d、OCP、ezdxf、matplotlib、pyyaml、pytest）。系统 Python 是 VeighNa，不往那里装 OCP。
- OCC 共面布尔会段错误。切除要过切。间歇段错误时重试，不据此改设计。
- build123d 把零件放进 Compound 时用 `Pos(0,0,0) * part` 复制，否则单独导出 STEP 会失败。
- 圆柱面孔轴取包围盒中点。`f.center()` 在此返回的是 bbox 最小值，X 会偏半个半径。
- SpaceClaim：`E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\scdm\SpaceClaim.exe`。
- Fluent 同树 `fluent\ntbin\win64\fluent.exe`。求解用批处理 journal。报告云图见 `skills/fluent-gui-capture`：期刊文件驱动 GUI，色标为该切面 Auto Range 且 `global-range? no`，壁面用面值，法向坐标用 annotation、字号 `"24"`。报错改过的命令写回该技能。不要 `(load)` 存图，不要滚轮或中键改视角。
- PowerShell 会吞掉 `&` 和括号。多步命令写成脚本文件再跑。
- 超长路径加 `\\?\` 前缀。

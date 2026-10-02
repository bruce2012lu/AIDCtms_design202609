---
confidence: 0.85
valid_until: 2026-12-31
last_verified: 2026-09-27
expired: false
---

# Fluent GUI 取图

报告云图以 `skills/fluent-gui-capture` 为准。用期刊文件驱动已经打开的 Fluent GUI，不关窗口，不重划网格，不重算。不用 HDF5 涂色。不要 `(load)` 去存图。不要把 `/file/read-journal` 逐字打进控制台。三行一次贴入：`/file/read-journal`、期刊路径、`()`。贴完后若焦点不在 Fluent，回车不会执行，控制台没有 `Reading journal file`。先把主窗口放到前台，再把焦点放回 `CxConsole`，然后回车。

色标是当前切面、当前变量的 Auto Range。`range-option` / `auto-range-on` / `global-range? no`。云图 `coloring` / `smooth`，`smooth` 后面不要 `quit`。切面 `node-values? yes`，壁面 `node-values? no` 且 `boundary-values? yes`。Ground plane grid 关掉。注记只点击不拖拽。字号 `"24"`，字体 `"Microsoft YaHei"`。图题只用 ASCII：`z=-1.98 mm`、`x=0 mm`、`Y=1.2 mm`，中部加 ` center`。汉字会画成方框。存图默认 2400×720。文件已存在时 `save-picture` 下一行写 `yes`。

Z 法向（XY）相机在 +Z，up 为 `(-1, 0, 0)`，Y 正向在画面右侧，X 正向朝下。不要把 28.8 mm 的长边转成竖直。`auto-scale` 按图形窗口适配，窗口又高又方时，底面带子在画面里仍然很细。

不要把平面正好放在 TIM–铜交界 `z=-2.00 mm` 上。12 块 interface 会画成亮缝，约 0.4 K 的色标把接缝拉成裂纹。面积加权 336.79 K 是界面温度。铜侧第一层节点是 `z=-1.98 mm`。铜–水底面下 0.02 mm 的铜内切面是 `z=-0.02 mm`，文件 `zm002_temperature.png`。

X 法向速度矢量叠在该面速度云图上：先 `display` 云图，再 `add-to-graphics` 矢量。箭头等长，颜色是 `velocity-magnitude`。`fixed-length?` 在 `vector-opt` 下。`scale` 子菜单里 `auto-scale? no`，`scale-f 0.0005`。`skip 24`。改完对象要再 `quit` 回到 `>`。顶层 `in-plane?`、`options`、`auto-scale?` 会中断。600 步报告嵌入 png 字节，不用外链。

网格对象的 TUI 用 `edge-type`（`all` / `feature` / `outline`），不要写 `edge-type-options`。`coloring-options` 也无效，颜色在 `coloring` / `manual` 下。边是白色时存出来的图是空白。报告里的网格图还没有换成合格的 Fluent 线框图。

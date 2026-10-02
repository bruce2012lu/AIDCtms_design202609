---
name: fluent-gui-capture
description: >-
  用 Fluent 期刊保存报告剖面云图。色标是当前切面、当前变量的 Auto Range，并关掉 Global Range。壁面用面值。图题写明哪一张剖面。文件名写明界面和变量。正视，Z 在切面内时朝上。不要用 HDF5 涂色，不要用 (load) 存图。
---

# Fluent GUI 取图

报告云图必须是 Fluent 自己画出的切面。HDF5 网格面涂色在 12 格长切面上会碎、会糊，不能进报告。

先出一张样张，按下面的验收过关，再批量。YZ、XY、ZX 各验一张。一条坏命令会让期刊在该行停下，后面的命令不执行。

## 图必须满足

- 一张图一个变量。温度和速度分成两个文件。
- 色标是**这一张图的切面、这一个变量**的最小到最大。不锁 313–342 K，速度不沿用温度上下限，不手填 Min/Max。
- 壁面色标跟该面的面值走。节点值会把邻接单元卷进来：i300 底面面值约 342.10–342.33 K，节点着色却把色标拉到 341.19–342.33，温差挤在色标顶端，12 格几乎同色。这样的图不合格。
- 图题是 Fluent 画在画面上的 annotation，不是对象名，也不是事后贴上去的字。横断面写 `z=`，竖直 X 切面写 `x=`，沿 Y 的切面写 `Y=`，后面是毫米。例如 `z=-2.08 mm`、`x=0 mm`、`Y=1.2 mm`。字号用 `"24"`。对象名 `a043t` 不是图题。
- 文件名写明界面和变量，中部单元把 `center` 放在变量前：

```
figs12cells/i300/wall_heat_temperature.png
figs12cells/i300/wall_heat_center_temperature.png
figs12cells/i300/x0_temperature.png
figs12cells/i300/x0_velocity.png
figs12cells/i300/outlet_y_front_velocity.png
```

不要用 `wall_heat_T_T.png`、`x0_TV_T.png`。`figs12cells/fluent_native/i300/` 里 2026-09-27 中午的 `*_T.png` / `*_V.png` 名称和色标都不合格，不要拷进报告。

- 正投影。板边是水平或竖直的矩形，不是平行四边形。
- Z 法向截面（XY）把 Y 的正向放在画面右侧，X 的正向朝下。相机在 +Z，up 用 `(-1, 0, 0)`。不要把长边转成竖直。
- Z 在切面内时朝屏幕上方。
- 色标用普通小数、5 位有效数字，不要 `e+`。
- 色标和图题留在空白里。`zoom-camera` 小于 1 是缩小。色标压住云图时再缩小一点。模型已经缩成细条时，改画面比例去适应切面，不要继续缩小。底面约 28.8 mm × 3 mm，方形画面里会变成一条细带，不合格。
- 云图上下边在主体宽度上偏差不超过 2 px。喷孔尖不要当成板的上边。

批量前用两张样张对比：`wall_heat` 和 X=0 的色标数字必须不同。底面色标还要从面值跨度能分辨出各格，不能整条挤在橙红顶端。

## 会话

Fluent：`E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261\fluent\ntbin\win64\fluent.exe`。`AWP_ROOT261` 与 `FLUENT_INC` 指向 v261。要 GUI，不要加 `-g`。取图不要重算，不要加 `-gpu`。

命令只写在期刊文件里，由 Fluent 自己读。每个提示单独一行。相机的 X、Y、Z 各占一行；三个数写在一行时只读 X。

不要做这些事：

- 不要 `(load ...)`，也不要在 `(load)` 里调用 `save-picture`。文件读完后会连报 `Empty filename`，窗口未响应，键盘不再进命令。
- 不要用 UI Automation Invoke `Journal...`。Invoke 会卡在文件对话框上。
- 不要把 `/file/read-journal` 逐字打进控制台。连字符会被打成两个，或变成破折号，命令失效。
- 不要滚轮，不要中键。中键是旋转。
- 不要 `/exit`，不要杀掉正在响应的 cx2610。窗口已经未响应、或日志不停写 `Empty filename` 时，停止送键。只有用户要求重新开始时才另开 GUI。

已经停在 `>` 时，用脚本操作 Console，不要点图形窗口。图形窗口里的粘贴会变成 `handle-key`，期刊不会运行。Console 页签用 Invoke（没有 SelectionItem）。编辑框的 AutomationId 是 `ConsoleDockWidget.ConsoleParentWidget.CxConsole`。SetFocus 之后 Ctrl+End，再从剪贴板粘贴。粘贴进输入行之后再按回车。回车若抢在粘贴之前，下一行会粘到上一行，变成 `read-journalD:`，期刊不会启动。Scheme 和路径不要从外壳命令行传入，引号会被吃掉，控制台会停在未闭合的字符串里。把要粘贴的行写进文本文件，脚本按行读。

健康的 GUI 也可以用 `-i` 启动期刊。已经打开的窗口不要关。把下面三行贴进控制台：

```
/file/read-journal
D:/path/capture.jou
()
```

`()` 结束文件列表。空回车会再问一次。连字符放在剪贴板里粘贴，不要逐字键入。

窗口未响应后的重新打开（不求解）：

```
fluent.exe 3d -r26.1.0 -i D:/path/read_i300.jou
```

`read_i300.jou` 只读已有的 `uc01b_cht_less_12y_i300.cas.h5`（同名 `.dat.h5` 会一起读入），读完后停在 GUI。不要在这个期刊末尾写 `/exit`。

## 对象、色标、壁面

平面：

```
/surface/plane-surface p-z0 xy 0
```

`xy` / `yz` / `zx` 后面是该方向坐标，单位 m。Fluent 按这个坐标切，不必对齐到节点。

对象名只用小写字母和数字。`yslotT` 会被收成 `yslott`，显示时必须用收成之后的名字。`/display/objects/display` 和名字分两行。

温度对象在 `quit` 之前写上色标。`range-option` 里先选 `auto-range-on`，下一层才有 `global-range?`。两层都要 `quit`。只开 `auto-range-on` 时，温度仍停在全域 313.15–342.33。2026-09-27 在 i300 底面上关掉 `global-range?` 之后，色标变为 341.19–342.33，不再整条发红。每个对象单独关一次；新建对象默认仍开着 Global Range。

云图用光滑着色，不用 `banded`。`banded` 再加关节点值，切面上每个单元一块色，网格痕迹很重。默认着色已经是 `smooth`。`coloring` 再选 `smooth` 之后，提示符回到 `Choose setting to change>`，下一行直接写 `node-values?`。这里不要 `quit`：这个 `quit` 会退出整个对象，`node-values?` 落到顶层，期刊中断。只有改成 `banded` 时提示符才停在 `coloring>`，那种情况才要 `quit`。

切面打开节点值，颜色在节点之间过渡，网格痕迹消失。壁面仍然关掉节点值、打开边界值，避免邻接 TIM 单元把色标拉宽。2026-09-27 少写 `quit` 时期刊中断；补上并且壁面用面值之后，i300 底面色标为 342.10–342.33 K，X=0 为 313.15–340.87 K。600 步的图按光滑切面重出，300 步的图不改。

X 法向切面另存速度矢量，对象类型是 `vector`。先显示该面的速度云图，再用 `add-to-graphics` 把矢量叠上去，不要只画箭头。箭头等长，长度不表示快慢；颜色用 `velocity-magnitude`。`in-plane?` 和 `fixed-length?` 在 `vector-opt` 下面，写在顶层会中断。`scale` 是子菜单，里面关 `auto-scale?`，`scale-f` 用 `0.0005`。`skip` 在对象顶层，用 `24`；`12` 太密，箭头连成色柱。改完对象要再 `quit` 一次才回到 `>`，否则下一条 `/display` 会中断。`auto-scale?` 和 `options` 写在顶层是无效命令。

```
/display/objects/edit
vx0
vector-opt
in-plane?
yes
fixed-length?
yes
quit
scale
auto-scale?
no
scale-f
0.0005
quit
skip
24
quit
/display/objects/display
f044v
/display/objects/add-to-graphics
vx0
```

文件名如 `x0_velocity_vector.png`。`f044v` 是同一张切面已经建好的速度云图。矢量图先显示速度云图，再 `add-to-graphics`。600 步报告把 png 字节嵌进 `<img src="data:image/png;base64,...">`，不要留 `src="figs..."` 外链。

## 不要切在交界面上

TIM–铜交界是 `z=-2.00 mm`。平面正好压在这层壁上时，12 块网格的 interface 会画成竖直亮缝。色标只有约 0.4 K（336.74–337.18 K），接缝被拉成裂纹。面积加权 336.79 K 是界面温度，亮缝不是喷孔热丝。

铜侧第一层节点在 `z=-1.98 mm`（界面上方 0.020 mm）。全长和中部都切这里，图题写 `z=-1.98 mm`，不要再标成 `z=-2 mm`。铜–水底面在 `z=0`。其下 0.02 mm 的铜内切面是 `z=-0.02 mm`（`-0.00002` m），文件 `zm002_temperature.png`。最近的节点面是 `-0.0248 mm` 和 `-0.0186 mm`，平面不必落在节点上。

Z 法向一律 Y 正向朝右。把长边转成竖直会让 Y 朝上，不合格。`auto-scale` 按图形窗口适配，不按 `x-resolution` 把 28.8 mm×3 mm 的带子拉高。窗口又高又方时，带子在画面里仍然很细。

存图用固定像素，避免方形窗口把底面缩成细条：

```
/display/set/picture/use-window-resolution?
no
/display/set/picture/x-resolution
2400
/display/set/picture/y-resolution
720
```

```
/display/objects/create
contour
wallheat
field
temperature
surfaces-list
wall_heat
()
coloring
smooth
node-values?
no
boundary-values?
yes
range-option
auto-range-on
global-range?
no
quit
quit
/display/objects/display
wallheat
```

`/display/set/contours/auto-range yes` 只作用于经典 contour 菜单，不改变图形对象。

速度另建对象，场名 `velocity-magnitude`，同样关掉 Global Range。不要复用温度对象。

中部一格（Y=0–2.4 mm）用 iso-clip。第一项是场，然后是新表面名、源表面、下限、上限。下限前不要写 `()`。

```
/surface/iso-clip
y-coordinate
x0c2
cut-x0
0
0.0024
```

缝（|X|≥1.10 mm）对 X 再 clip 两次：`0.0011`–`0.0015`，以及 `-0.0015`–`-0.0011`。两个名字分两行写入 `surfaces-list`，用 `()` 结束。已经是固定 Y 的平面不要再按 Y clip。

新对象的数字格式：

```
/preferences/graphics/colormap-settings/number-format-type
general
/preferences/graphics/colormap-settings/number-format-precision
5
```

这只作用于新建对象。`/display/set/windows/scale/format` 改不到图形对象的色标。

## 相机

先正投影，再位置、目标、上方向，然后自适应、留白、滚转。滚转角度逆时针为正，`-0.13` 是顺时针。自适应并 `zoom-camera 0.72` 之后用这个滚转角，X=0 上约 900 px 宽度偏差 2 px。

YZ（x 为常数，沿 X 看，Z 朝上）。位置 X 比切面大 0.08，目标 X 为切面坐标，Y=0，Z=0.003：

```
/display/views/camera/projection
orthographic
/display/views/camera/position
0.08
0
0.003
/display/views/camera/target
0
0
0.003
/display/views/camera/up-vector
0
0
1
/display/views/auto-scale
/display/views/camera/zoom-camera
0.72
/display/views/camera/roll-camera
-0.13
```

XY（z 为常数，从上往下看，Y 朝右）。位置 `(0, 0, z+0.05)`，目标 `(0, 0, z)`，上方向 `(-1, 0, 0)`，随后同样自适应、0.72、`-0.13`。

ZX（y 为常数，沿 Y 看，Z 朝上）。位置 `(0, y+0.05, 0.003)`，目标 `(0, y, 0.003)`，上方向 `(0, 0, 1)`。已在 `slot-y`（y=0.0012）上出图。

## 存图

```
/display/save-picture
D:/path/x0_temperature.png
```

文件已存在时，下一行必须是 `yes`。文件还不存在时不要写 `yes`，否则 `yes` 被当成下一条命令，期刊在这一行中断。2026-09-27 批量期刊在写 `x0_temperature.png` 时没有 `yes`，下一行 `(display ...)` 被当成覆盖回答，整份期刊停在 `Please answer y[es] or n[o]`。生成期刊时按当时磁盘上的文件决定写不写 `yes`。样张先写出的 png，批量期刊里必须带 `yes`。

## 画面上的法向坐标

坐标写在 annotation 里，和对象名一样由 Fluent 画进 png。对象名只能是小写字母和数字，写不进 `x=0 mm`。

`/display/annotation/create`、`/display/annotation/list` 是无效命令。`/results/` 也不是命令。用下面这条：

```
/display/annotation/annotate
"x=0 mm"
"None"
```

`None` 必须加引号。不加引号会被收成 `none`，报 `invalid choice`，期刊中断。下一句是用左键点一个位置。只点击，不要拖拽。拖拽会从文字拉出一条黑色引出线，云图上方那条斜线就是它。Escape 和 PostMessage 取消不了这一步。点一下即可，名字是 `text-0`。已经拖出引线时，先删再点：

```
/display/annotation/delete
text-0
()
yes
```

`()` 结束名单，`yes` 确认。少写 `()` 时，下一行命令会被当成要删的名字，期刊中断。删完后重新 `annotate`，鼠标只点一下。

之后改文字和字号不再要鼠标。`text` 和 `font-size` 只在这个子菜单里有效，写在顶层 `>` 上会报 `invalid command`。空回车会退出这个子菜单。

```
/display/annotation/edit
text-0
text
"x=0 mm"
font-size
"24"
quit
```

字号必须是带引号的选项。不加引号的 `32` 报 `Invalid string/symbol`。用 `"24"`。

这张注记即使用 `"Microsoft YaHei"`，汉字仍画成方框。图题只用 ASCII：`z=-2.08 mm`、`x=0 mm`、`Y=1.2 mm`，中部单元加 ` center`。字体名有空格，必须加引号：

```
font-name
"Microsoft YaHei"
font-size
"24"
```

只改 annotation 的文字不会出现在新对象的 png 里。对象显示时会把窗口注记清掉。要挂到对象上。`annotations-list` 先问数量，再问名字。直接写 `text-0` 会报 `unbound variable`。

```
annotations-list
1
text-0
```

先改 `text`，再创建并挂上注记，然后设相机、存图。每张图存之前改一次 `text`。横断面 `z=`，X 切面 `x=`，沿 Y 的切面 `Y=`。读入另一个 case 会丢掉 annotation，需要再放置一次。

## 报错之后不要再犯

- `smooth` 后面不要 `quit`。默认已是 smooth，再 quit 会退出对象，`node-values?` 落到顶层。`banded` 才会停在 `coloring>`，那种情况才 quit。切面不要用 `banded` 加关节点值。切面 `node-values? yes`，壁面 `no` 且 `boundary-values? yes`。
- 底面整条发红：`auto-range-on` 之后还要 `global-range? no`。
- `(load)` 调用 `save-picture`：会连报 `Empty filename`，窗口未响应。命令只放进期刊文件。
- Invoke 菜单 `Journal...`：卡在文件对话框上。改贴 `/file/read-journal`。
- 逐字键入 `/file/read-journal`：连字符变成两个或破折号。从文件粘贴。
- 粘贴进图形窗口：日志是 `handle-key`。先 Invoke Console 页签，再 SetFocus 到 `CxConsole`。
- 逐行粘贴 `/file/read-journal`：控制台忙时两行粘成 `read-journalD:` 或 `read-journal()`。三行一次贴入。
- 背景里交叉的灰白线是 Ground plane grid，不是计算网格。关掉：`/preferences/graphics/graphics-effects/grid-plane-enabled` 然后 `no`。
- 注记黑斜线是拖拽出来的引出线。放置时只点击。删掉时名单以 `()` 结束，再写 `yes`。
- 外壳命令行里写 Scheme：引号被吃掉，字符串不闭合。行放在文本文件里。
- 覆盖已有 png 没有 `yes`：下一行被当成 yes/no，期刊停住。
- 字号写成不带引号的数字，或写成 `"32"`：用 `"24"`。
- 汉字用 Rubik：方框。`font-name` 用 `"Microsoft YaHei"`。
- `annotations-list` 后面直接写 `text-0`：它先要数量。写成 `1` 再写 `text-0`。
- `Append Quantity` 写成 `None`：写成 `"None"`。
- 对象还停在 `Choose setting to change>` 时写 `/display/annotation/edit`：无效，期刊中断。改完 `scale` 或 `vector-opt` 后再 `quit` 一次，回到 `>` 再显示、存图。
- 矢量顶层写 `in-plane?`、`options`、`auto-scale?`、`edge-type-options`、`coloring-options`：都是无效命令。`in-plane?` 和 `fixed-length?` 在 `vector-opt` 下。`scale` 进子菜单后关 `auto-scale?`，再写 `scale-f`。网格边类型用 `edge-type`，取值 `all`、`feature`、`outline`。
- `skip 12` 的射流箭头连成色柱。X 法向用 `skip 24`，`scale-f 0.0005`，`fixed-length? yes`。长度不表示快慢。
- 三行期刊贴进控制台后，焦点若在别的窗口，回车不会执行，控制台没有 `Reading journal file`。先把 Fluent 主窗口放到前台，贴上之后再把焦点放回 `CxConsole`，然后回车。
- 正好切在 `z=-2 mm` 交界面上：12 条亮缝。改切铜侧第一层 `z=-1.98 mm`。

样张过关后再写批量期刊。一批结束时用 `(display "CAPTURE-DONE")` 留标记。

已出过、可作相机和正视参照的图：X=0 温度与速度（速度 0–1.693 m/s）、z=0 温度、`slot-z` 速度、Y=1.2 mm 的 ZX 温度、Y=0–2.4 mm 的 iso-clip。这些图若仍是全域色标或没有图题，不能直接进报告。z=0 速度对象没有画出云图。网格对象能创建，图里没有网格线，不能替换报告网格图。

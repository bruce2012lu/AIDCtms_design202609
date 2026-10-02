"""为 asm_0921.stp 结构说明报告生成插图。

产出到 out/asm0921/（编号与报告正文的图号一致）：
    fig1_assembly.png     装配轴测
    fig2_exploded.png     爆炸图（沿 Z 拉开）
    fig3_plate.png        PLATE 说明图（轴测 + 俯视）
    fig4_cover1.png       COVER1 说明图
    fig5_cover2.png       COVER2 说明图（腔朝下，用仰视）
    fig6_section.png      过喷嘴列的真实剖面（全幅 + 局部放大）
    fig7_cutaway.png      局部剖切轴测
    fig8_flowpath.png     流体流通路径示意（YZ 剖面）

轴测线框走 build123d 的 project_to_viewport（OCC 的 HLR），不是三角网渲染，
所以出来是干净的工程线条，缩放后不糊。
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, Rectangle
from build123d import Align, Pos, import_step

_MIN3 = (Align.MIN, Align.MIN, Align.MIN)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parent
STP = ROOT / "asm_0921.stp"
OUT = ROOT / "out" / "asm0921"

# 三件都是铜，用同色系不同明度区分，避免看起来像不同材料
STYLE = {
    "PLATE": ("#b3611f", "PLATE · 换热底板"),
    "COVER1": ("#e2a75c", "COVER1 · 喷嘴板"),
    "COVER2": ("#7d4a1e", "COVER2 · 静压箱盖"),
}
ORDER = ["PLATE", "COVER1", "COVER2"]

ISO = dict(viewport_origin=(240, -300, 210), viewport_up=(0, 0, 1))
ISO_LOW = dict(viewport_origin=(240, -300, -210), viewport_up=(0, 0, 1))
TOP = dict(viewport_origin=(47.5, 37.5, 400), viewport_up=(0, 1, 0))
# 仰视：COVER2 的双腔与隔腔肋都开在朝下的一面，俯视和常规轴测都看不到
BOTTOM = dict(viewport_origin=(47.5, 37.5, -400), viewport_up=(0, 1, 0))


def load() -> dict:
    asm = import_step(str(STP))
    solids = sorted(asm.solids(), key=lambda s: s.bounding_box().min.Z)
    return dict(zip(ORDER, solids))


def draw(ax, shape, color: str, lw: float = 0.45, look_at=(47.5, 37.5, 6.0),
         view=None) -> None:
    """把一个实体的可见轮廓投到 ax 上。隐藏边不画，保持图面干净。"""
    cfg = dict(view or ISO)
    cfg["look_at"] = look_at
    visible, _hidden = shape.project_to_viewport(**cfg)
    for e in visible:
        pts = [(v.X, v.Y) for v in e.positions([i / 12 for i in range(13)])] \
            if e.geom_type.name != "LINE" else \
            [(e.start_point().X, e.start_point().Y), (e.end_point().X, e.end_point().Y)]
        ax.plot([p[0] for p in pts], [p[1] for p in pts],
                color=color, lw=lw, solid_capstyle="round")


def finish(ax) -> None:
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.margins(0.03)


def legend(ax, keys) -> None:
    handles = [plt.Line2D([], [], color=STYLE[k][0], lw=2.2, label=STYLE[k][1])
               for k in keys]
    ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=10)


def fig_assembly(parts) -> Path:
    fig, ax = plt.subplots(figsize=(9, 7.2))
    for k in ORDER:
        draw(ax, parts[k], STYLE[k][0])
    finish(ax)
    legend(ax, ORDER)
    ax.set_title("图 1　装配轴测　外形 95 × 75 × 12.5 mm", fontsize=13, pad=12)
    p = OUT / "fig1_assembly.png"
    fig.savefig(p, dpi=190, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return p


def fig_exploded(parts, gap: float = 16.0) -> Path:
    fig, ax = plt.subplots(figsize=(9, 9.6))
    lift = {"PLATE": 0.0, "COVER1": gap, "COVER2": 2 * gap}
    for k in ORDER:
        draw(ax, Pos(0, 0, lift[k]) * parts[k], STYLE[k][0],
             look_at=(47.5, 37.5, 18.0))
    finish(ax)
    legend(ax, ORDER)
    ax.set_title("图 2　爆炸图　自下而上：PLATE → COVER1 → COVER2",
                 fontsize=13, pad=12)
    p = OUT / "fig2_exploded.png"
    fig.savefig(p, dpi=190, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return p


def fig_part(parts, key: str, idx: int, caption: str,
             views: tuple = (("轴测", ISO), ("俯视", TOP))) -> Path:
    color = STYLE[key][0]
    body = parts[key]
    zc = body.bounding_box().center().Z
    fig, axes = plt.subplots(1, len(views), figsize=(6.75 * len(views), 6.0))
    for ax, (name, view) in zip(axes, views):
        draw(ax, body, color, lw=0.5, look_at=(47.5, 37.5, zc), view=view)
        ax.set_title(name, fontsize=11)
        finish(ax)
    fig.suptitle(f"图 {idx}　{STYLE[key][1]}　{caption}", fontsize=13, y=0.99)
    p = OUT / f"fig{idx}_{key.lower()}.png"
    fig.savefig(p, dpi=185, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return p


# ---------------- 流路示意 ----------------

CU = "#c8873f"
CU_DARK = "#8d5524"
WATER_IN = "#1f6fb2"
WATER_OUT = "#c0392b"


FLUID_IN = "#cfe4f5"
FLUID_MIX = "#dbeaf6"
FLUID_OUT = "#f6dcd8"

STEPS = [
    ("①", WATER_IN, "进液口",
     "COVER2 侧壁 y=75 一处矩形口，通向进液静压箱"),
    ("②", WATER_IN, "分流",
     "进液静压箱占据静压箱层的大腔，先稳压再沿 Y 铺开分配到整个喷嘴阵"),
    ("③", WATER_IN, "喷射",
     "COVER1 上 128 个圆孔（两片 8×8，对准两颗 die）把液体加速成微射流向下打出"),
    ("④", "#0b2748", "冲击 / 壁面射流",
     "射流打在 PLATE 余铜顶面形成驻点，动量转为径向，贴壁刮出薄高速层"),
    ("⑤", "#0b2748", "短槽导流",
     "壁面射流就近进入 PLATE 的短槽，废液在极短行程内离开驻点，避免交叉流吹歪下游"),
    ("⑥", "#2e7d5b", "汇集",
     "短槽与 HBM 侧腔都上抽进整板回流汇集层，该层横贯全板、单一连通"),
    ("⑦", WATER_OUT, "出液口",
     "回流经 COVER1 的回液窗口上抽进出液小腔，由 COVER2 侧壁 y=0 一处矩形口流出"),
    ("⑧", WATER_IN, "HBM 侧腔旁路",
     "进液静压箱另经两个角窗直接下灌左右侧腔，无喷嘴、低速平流掠过 HBM，再并入⑥"),
]


def fig_flowpath() -> Path:
    """YZ 剖面示意 + 图下分步说明。

    层界取自 asm_0921.stp 实测：
      0–2.0 余铜 / 2.0–3.5 短槽 / 3.5–5.5 回流 / 5.5–7.5 喷嘴 / 7.5–10.5 静压箱
    文字一律放到图外，剖面里只留编号，否则在 12.5 mm 的层高里必然互相压住。
    """
    # 轴框高度按 aspect 算出的实际内容高度给，否则剖面上下会留大片空白
    fig = plt.figure(figsize=(14, 7.6))
    ax = fig.add_axes([0.03, 0.57, 0.94, 0.38])
    ax_leg = fig.add_axes([0.03, 0.02, 0.94, 0.52])
    ax_leg.set_axis_off()

    def band(y0, y1, z0, z1, fc, ec=CU_DARK, lw=0.7, z=2):
        ax.add_patch(Rectangle((y0, z0), y1 - y0, z1 - z0, facecolor=fc,
                               edgecolor=ec, lw=lw, zorder=z))

    # --- 先铺流体，再压铜，避免出现白缝 ---
    band(2, 73, 2.0, 3.5, FLUID_MIX, ec=None, lw=0, z=1)      # 短槽层
    band(2, 73, 3.5, 5.5, FLUID_MIX, ec="#9dc3e0", z=1)       # 回流汇集层
    band(23.2, 75, 7.5, 10.5, FLUID_IN, ec="#9dc3e0", z=1)    # 进液静压箱
    band(0, 12.5, 7.5, 10.5, FLUID_OUT, ec="#e0a79f", z=1)    # 出液小腔
    band(2, 12.5, 5.5, 7.5, FLUID_OUT, ec="#e0a79f", z=1)     # 回液窗口

    band(0, 75, 0, 2.0, CU, z=3)                              # PLATE 余铜
    band(0, 75, 10.5, 12.5, CU_DARK, z=3)                     # COVER2 盖顶
    band(12.5, 23.2, 7.5, 10.5, CU_DARK, z=3)                 # 隔腔铜肋
    for y0 in [i * 2.0 for i in range(1, 37)]:                # 短槽间的肋
        band(y0, y0 + 0.85, 2.0, 3.5, CU, ec=None, lw=0, z=3)
    band(12.5, 75, 5.5, 7.5, "#e2a75c", z=3)                  # COVER1 本体
    band(0, 2.0, 5.5, 7.5, "#e2a75c", z=3)
    band(12.5, 13.8, 3.5, 5.5, "#e2a75c", z=3)                # COVER1 下裙
    band(71.7, 73.0, 3.5, 5.5, "#e2a75c", z=3)
    band(0, 2.0, 2.0, 5.5, CU, ec=None, lw=0, z=3)            # 周边钎焊框
    band(73.0, 75, 2.0, 5.5, CU, ec=None, lw=0, z=3)

    # 喷嘴与射流
    for y in [27, 30, 33, 36, 39, 42, 45, 48]:
        ax.plot([y, y], [5.5, 7.5], color=WATER_IN, lw=1.5, zorder=4)
        ax.add_patch(FancyArrow(y, 5.45, 0, -2.0, width=0.04, head_width=0.7,
                                head_length=0.55, color=WATER_IN, zorder=4,
                                length_includes_head=True))

    # 端口
    ax.add_patch(Rectangle((75, 7.5), 4.0, 3.0, facecolor=FLUID_IN,
                           edgecolor=WATER_IN, lw=1.5, zorder=4))
    ax.add_patch(Rectangle((-4.0, 7.5), 4.0, 3.0, facecolor=FLUID_OUT,
                           edgecolor=WATER_OUT, lw=1.5, zorder=4))
    ax.annotate("", xy=(74.5, 9.0), xytext=(86, 9.0), zorder=5,
                arrowprops=dict(arrowstyle="-|>", color=WATER_IN, lw=2.6))
    ax.annotate("", xy=(-12, 9.0), xytext=(-0.5, 9.0), zorder=5,
                arrowprops=dict(arrowstyle="-|>", color=WATER_OUT, lw=2.6))

    # 主流向
    ax.annotate("", xy=(28, 9.0), xytext=(70, 9.0), zorder=5,
                arrowprops=dict(arrowstyle="-|>", color=WATER_IN, lw=2.0))
    ax.annotate("", xy=(16, 4.2), xytext=(64, 4.2), zorder=5,
                arrowprops=dict(arrowstyle="-|>", color="#2e7d5b", lw=2.0))
    ax.annotate("", xy=(7, 7.4), xytext=(7, 5.6), zorder=5,
                arrowprops=dict(arrowstyle="-|>", color=WATER_OUT, lw=2.2))
    ax.annotate("", xy=(72.4, 5.7), xytext=(72.4, 7.4), zorder=5,
                arrowprops=dict(arrowstyle="-|>", color=WATER_IN, lw=1.8))

    def tag(sym, y, z, color):
        ax.text(y, z, sym, fontsize=11, color="white", ha="center", va="center",
                zorder=6, fontweight="bold",
                bbox=dict(boxstyle="circle,pad=0.18", fc=color, ec="none"))

    tag("①", 88.5, 9.0, WATER_IN)
    tag("②", 49.0, 9.0, WATER_IN)
    tag("③", 37.5, 6.5, WATER_IN)
    tag("④", 24.0, 2.6, "#0b2748")
    tag("⑤", 51.0, 2.6, "#0b2748")
    tag("⑥", 40.0, 5.0, "#2e7d5b")
    tag("⑦", -14.5, 9.0, WATER_OUT)
    tag("⑧", 72.4, 6.5, WATER_IN)

    # 层标注（左侧，与剖面不重叠）
    for z0, z1, txt in [(0, 2.0, "余铜层（底面含 TIM 让位浅腔）"),
                        (2.0, 3.5, "短槽层"),
                        (3.5, 5.5, "回流汇集层"),
                        (5.5, 7.5, "喷嘴段 / 回液窗口"),
                        (7.5, 10.5, "静压箱层（右进左出，中间铜肋隔断）"),
                        (10.5, 12.5, "盖顶")]:
        zm = (z0 + z1) / 2
        ax.text(-20, zm, txt, fontsize=9.5, color="#44566b", va="center",
                ha="right")
        ax.plot([-19.5, -4.5], [zm, zm], color="#ccd6e0", lw=0.6, zorder=0)

    ax.text(37.5, -1.6, "Y 方向：0 ——————————→ 75 mm（进液在 75 侧）",
            fontsize=9, color="#8a97a5", ha="center")
    ax.set_xlim(-64, 97)
    ax.set_ylim(-2.6, 13.4)
    ax.set_aspect(2.1)
    ax.set_axis_off()
    ax.set_title("图 8　流体流通路径（YZ 剖面示意，层界取自 asm_0921.stp 实测；"
                 "板内不含流体实体，此腔即流体域）", fontsize=12.5, pad=8)

    for i, (sym, color, name, desc) in enumerate(STEPS):
        y = 0.94 - i * 0.125
        ax_leg.text(0.005, y, sym, fontsize=11, color="white", ha="center",
                    va="center", fontweight="bold", transform=ax_leg.transAxes,
                    bbox=dict(boxstyle="circle,pad=0.18", fc=color, ec="none"))
        ax_leg.text(0.028, y, f"{name}　", fontsize=11, color=color,
                    va="center", ha="left", fontweight="bold",
                    transform=ax_leg.transAxes)
        ax_leg.text(0.125, y, desc, fontsize=10.5, color="#33404d",
                    va="center", ha="left", transform=ax_leg.transAxes)

    p = OUT / "fig8_flowpath.png"
    fig.savefig(p, dpi=185, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return p


# ---------------- 真实剖面：把 z 向看清 ----------------

# 过喷嘴列的剖切位置：孔轴 X = 22.0 / 25.0 / … / 43.0（die-A）。
# 注意不能用圆柱面的 center() 取轴线——build123d 那里返回的是面 bbox 的最小值，
# 比真实轴线小半个半径（0.25），照它切会正好从两排孔中间穿过，剖面上一个孔都看不到。
SECTION_X = 22.0


def _face_path(face, uv):
    """把剖面上的一个面转成带孔的 matplotlib Path。

    用 `wire @ t` 按弧长等距采样拿到有序点列——直接取 vertices 拿不到绕序，
    而剖面里全是窄槽和小孔，绕序错了就会画成一团乱线。
    """
    from matplotlib.path import Path as MplPath

    verts, codes = [], []
    for wire in [face.outer_wire(), *face.inner_wires()]:
        n = max(80, int(wire.length * 25))
        pts = [uv(wire @ (i / n)) for i in range(n + 1)]
        verts += pts
        codes += [MplPath.MOVETO] + [MplPath.LINETO] * (len(pts) - 2) + \
                 [MplPath.CLOSEPOLY]
    return MplPath(verts, codes)


def _draw_section(ax, parts, plane, uv, lw=0.5):
    from matplotlib.patches import PathPatch

    # 腔内不是铜的地方就是流体域（主流道 bbox：Y 0–75、z 2.0–10.5）。
    # 先铺一层浅蓝底再压铜，剖面才读得出"铜带浮在水里"，否则全是白缝很难看层。
    ax.add_patch(Rectangle((0, 2.0), 75, 8.5, facecolor="#dbeaf6",
                           edgecolor="none", zorder=0))
    for key in ORDER:
        sec = plane.intersect(parts[key])
        if sec is None:
            continue
        color = STYLE[key][0]
        for f in sec.faces():
            ax.add_patch(PathPatch(_face_path(f, uv), facecolor=color,
                                   edgecolor="#5c3a17", lw=lw, zorder=2))


def fig_section(parts) -> Path:
    """图 7：过喷嘴列的真实剖面。左全幅、右局部放大，等比例不拉伸。"""
    from build123d import Plane

    plane = Plane.YZ.offset(SECTION_X)

    def uv(v):
        return (v.Y, v.Z)

    fig, axes = plt.subplots(2, 1, figsize=(13.5, 8.6),
                             gridspec_kw={"height_ratios": [1, 1.5]})

    _draw_section(axes[0], parts, plane, uv, lw=0.35)
    axes[0].set_xlim(-2, 77)
    axes[0].set_ylim(-1, 13.5)
    axes[0].set_title(f"全幅剖面（X = {SECTION_X} mm，过一整列 8 个喷嘴的轴线）"
                      "　等比例，可见 12.5 mm 厚度摊在 75 mm 上必然被压扁",
                      fontsize=11)

    _draw_section(axes[1], parts, plane, uv, lw=0.7)
    axes[1].set_xlim(25.3, 43.5)
    axes[1].set_ylim(1.4, 11.2)
    axes[1].set_title("局部放大（同一剖面，Y 方向截取约 17 mm）"
                      "　自上而下：静压箱 → 喷嘴孔 → 喷距间隙 → 短槽 → 余铜",
                      fontsize=11)

    for ax in axes:
        ax.set_aspect("equal")
        ax.set_axis_off()

    ann = axes[1]
    for y0, y1, z, txt, col in [
        (25.5, 43.3, 9.0, "静压箱（进液侧大腔）", "#1f6fb2"),
        (25.5, 43.3, 6.5, "COVER1 实体段：图中一个个缺口就是喷嘴孔，孔长 = 该段厚度",
         "#6b3f12"),
        (25.5, 43.3, 4.5, "喷距间隙：射流在此段自由发展后打到铜壁", "#1f6fb2"),
        (25.5, 43.3, 2.75, "短槽层：槽与肋交替，废液就近横向离场", "#0f6d52"),
        (25.5, 43.3, 1.0, "余铜层（下方即贴芯片面）", "#6b3f12"),
    ]:
        ann.annotate("", xy=(y0, z), xytext=(y1, z), zorder=6,
                     arrowprops=dict(arrowstyle="-", color=col, lw=0.6, ls=":"))
        ann.text((y0 + y1) / 2, z + 0.16, txt, fontsize=9.5, color=col,
                 ha="center", va="bottom", zorder=7,
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none",
                           alpha=0.82))

    handles = [plt.Line2D([], [], color=STYLE[k][0], lw=7, label=STYLE[k][1])
               for k in ORDER]
    handles.append(plt.Line2D([], [], color="#dbeaf6", lw=7, label="流体域（腔内非铜处）"))
    axes[0].legend(handles=handles, loc="lower left", frameon=False, fontsize=9.5,
                   ncol=4, bbox_to_anchor=(0.0, -0.16))

    fig.suptitle("图 6　过喷嘴列的真实剖面　几何直接取自 asm_0921.stp，非示意",
                 fontsize=13, y=0.99)
    p = OUT / "fig6_section.png"
    fig.savefig(p, dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return p


def fig_cutaway(parts) -> Path:
    """图 8：局部剖切轴测。切一小块出来，用三维看喷嘴与短槽的对位关系。"""
    from build123d import Box

    # 取 die-A 孔阵左下角附近一小块：覆盖约 3×3 个喷嘴 + 下方短槽
    x0, y0, w, d = 20.0, 25.4, 11.0, 11.0
    box = Pos(x0, y0, -1.0) * Box(w, d, 15.0, align=_MIN3)

    fig, ax = plt.subplots(figsize=(9.6, 8.2))
    center = (x0 + w / 2, y0 + d / 2, 6.0)
    for key in ORDER:
        chunk = parts[key] & box
        if chunk is None or chunk.volume < 1e-6:
            continue
        visible, _hidden = chunk.project_to_viewport(
            viewport_origin=(x0 + 46, y0 - 54, 40), viewport_up=(0, 0, 1),
            look_at=center)
        for e in visible:
            a, b = e.start_point(), e.end_point()
            if e.geom_type.name == "LINE":
                ax.plot([a.X, b.X], [a.Y, b.Y], color=STYLE[key][0], lw=0.6)
            else:
                pts = [(v.X, v.Y) for v in e.positions([i / 16 for i in range(17)])]
                ax.plot([q[0] for q in pts], [q[1] for q in pts],
                        color=STYLE[key][0], lw=0.6)
    finish(ax)
    legend(ax, ORDER)
    ax.set_title("图 7　局部剖切轴测（截取约 11 × 11 mm，含 4×4 个喷嘴）\n"
                 "这不是爆炸图：槽齿顶面与喷嘴板之间那道缝，就是真实的喷距间隙",
                 fontsize=12.5, pad=10)
    p = OUT / "fig7_cutaway.png"
    fig.savefig(p, dpi=195, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return p


# ---------------- 托盘级回路原理图 ----------------

SUP = "#1f6fb2"   # 供液
RET = "#c0392b"   # 回液


def fig_tray_circuit() -> Path:
    """图 10：GB300 NVL2 托盘级冷却回路原理，并标出本冷板在其中的位置。

    托盘照片只能看清"单进单出 + 6 个液冷位"，四块 GPU 冷板到底并联还是串联
    在那个分辨率下看不出来。所以图里把可见事实画成实线、把按设计报告口径
    采用的并联拓扑标成推断，不混为一谈。
    """
    from matplotlib.patches import FancyBboxPatch, Rectangle

    fig = plt.figure(figsize=(14.5, 9.4))
    ax = fig.add_axes([0.02, 0.36, 0.96, 0.58])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 56)
    ax.set_axis_off()

    def box(x, y, w, h, fc, ec, txt, fs=10, tc="#12263a", bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6",
                                    facecolor=fc, edgecolor=ec, lw=1.4))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center",
                fontsize=fs, color=tc,
                fontweight="bold" if bold else "normal")

    # 后面板：照片里进液 UQD 在上、出液 UQD 在下，两者同在后面板，不是两侧
    ax.add_patch(Rectangle((88.5, 1.0), 2.0, 52.0, facecolor="#dfe5ea",
                           edgecolor="#9aa7b4", lw=1.2))
    ax.text(89.5, 27, "后\n面\n板", ha="center", va="center", fontsize=9,
            color="#66757f")
    box(91.5, 45.5, 8.0, 6.5, "#d9e9f7", SUP, "进液\nUQD", 9.5, SUP, True)
    box(91.5, 2.5, 8.0, 6.5, "#f9dedb", RET, "出液\nUQD", 9.5, RET, True)

    # 供液干管：从后面板上方沿顶部引到供液歧管
    ax.annotate("", xy=(24.1, 52.0), xytext=(91.0, 52.0),
                arrowprops=dict(arrowstyle="-|>", color=SUP, lw=2.4))
    ax.annotate("", xy=(91.2, 52.0), xytext=(91.2, 45.3),
                arrowprops=dict(arrowstyle="-", color=SUP, lw=2.4))
    ax.text(57, 52.9, "供液干管", ha="center", fontsize=9, color=SUP)

    # 供 / 回歧管
    ax.add_patch(Rectangle((22, 2.5), 4.2, 48.0, facecolor="#cfe4f5",
                           edgecolor=SUP, lw=1.6))
    ax.text(24.1, 1.2, "托盘供液歧管", ha="center", va="top", fontsize=9.5,
            color=SUP)
    ax.add_patch(Rectangle((73.5, 2.5), 4.2, 48.0, facecolor="#f6dcd8",
                           edgecolor=RET, lw=1.6))
    ax.text(75.6, 1.2, "托盘回液歧管", ha="center", va="top", fontsize=9.5,
            color=RET)

    # 回液干管：回液歧管底部 → 后面板下方出液 UQD
    ax.annotate("", xy=(91.0, 5.7), xytext=(77.9, 5.7),
                arrowprops=dict(arrowstyle="-|>", color=RET, lw=2.4))

    # 6 个液冷位：两块 NVL2 板各 1 Grace + 2 GPU
    rows = [
        (43.5, "GPU-1  ·  B300 SXM7", True),
        (36.0, "GPU-2  ·  B300 SXM7", True),
        (28.5, "Grace-1  ·  CPU + 内存", False),
        (18.5, "GPU-3  ·  B300 SXM7", True),
        (11.0, "GPU-4  ·  B300 SXM7", True),
        (3.5, "Grace-2  ·  CPU + 内存", False),
    ]
    for y, label, is_gpu in rows:
        fc = "#f4e0cf" if is_gpu else "#e8eef5"
        ec = "#b3611f" if is_gpu else "#7a8a9a"
        box(34, y, 32, 6.0, fc, ec, label, 10.5, "#5c3a17" if is_gpu else "#33404d",
            is_gpu)
        ax.annotate("", xy=(33.8, y + 3.0), xytext=(26.2, y + 3.0),
                    arrowprops=dict(arrowstyle="-|>", color=SUP, lw=1.7))
        ax.annotate("", xy=(73.3, y + 3.0), xytext=(66.2, y + 3.0),
                    arrowprops=dict(arrowstyle="-|>", color=RET, lw=1.7))

    # 两块 NVL2 板分组
    for y0, h, name in [(27.5, 23.0, "GB300 NVL2 板「1」（近进液端）"),
                        (2.5, 23.0, "GB300 NVL2 板「2」（近出液端）")]:
        ax.add_patch(Rectangle((31.5, y0), 37, h, facecolor="none",
                               edgecolor="#9aa7b4", lw=1.0, ls="--"))
        ax.text(50, y0 + h - 0.8, name, ha="center", va="top", fontsize=9.5,
                color="#66757f")

    ax.text(50, 55.2, "★ 本设计方案 asm_0921 对应下列 4 个 GPU 位中的任意一个"
                      " → 整托盘需 4 块",
            ha="center", fontsize=11.5, color="#b3611f", fontweight="bold")

    ax.text(80.5, 30, "风冷部分\n不在本回路：\nNVMe / OSFP /\nPCIe Riser / BF3 /\n"
                      "CX8 / PDB /\nBMC 与 1G 板\n（托盘仍保留\nFan Bay）",
            fontsize=8.8, color="#66757f", va="center", ha="left")

    # ---- 下半：单块冷板内部流路，把托盘级和板级接起来 ----
    ax2 = fig.add_axes([0.02, 0.03, 0.96, 0.29])
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 22)
    ax2.set_axis_off()
    ax2.add_patch(Rectangle((0.5, 0.5), 99, 21, facecolor="#fbfcfe",
                            edgecolor="#b3611f", lw=1.4, ls="--"))
    ax2.text(50, 19.6, "放大：任意一个 GPU 位内部 —— 本设计方案 asm_0921 的板级流路",
             ha="center", fontsize=11.5, color="#b3611f", fontweight="bold")

    chain = [("①进液口", SUP), ("②静压箱\n分流", SUP), ("③128 孔\n喷射", SUP),
             ("④冲击\n驻点", "#12263a"), ("⑤短槽\n导流", "#0f6d52"),
             ("⑦回流层\n汇集", "#0f6d52"), ("⑧回液窗口\n→出液口", RET)]
    w, gap = 11.5, 2.2
    x = (100 - (len(chain) * w + (len(chain) - 1) * gap)) / 2
    for i, (txt, col) in enumerate(chain):
        xi = x + i * (w + gap)
        ax2.add_patch(FancyBboxPatch((xi, 8.5), w, 6.2,
                                     boxstyle="round,pad=0.4",
                                     facecolor="white", edgecolor=col, lw=1.5))
        ax2.text(xi + w / 2, 11.6, txt, ha="center", va="center", fontsize=9.5,
                 color=col)
        if i < len(chain) - 1:
            ax2.annotate("", xy=(xi + w + gap - 0.3, 11.6), xytext=(xi + w + 0.3, 11.6),
                         arrowprops=dict(arrowstyle="-|>", color="#8a97a5", lw=1.4))

    # 旁路画在链条下方，不穿过任何方框
    x_from = x + 1 * (w + gap) + w / 2
    x_to = x + 5 * (w + gap) + w / 2
    ax2.annotate("", xy=(x_from, 8.3), xytext=(x_from, 6.4),
                 arrowprops=dict(arrowstyle="-", color=SUP, lw=1.5))
    ax2.annotate("", xy=(x_to, 8.3), xytext=(x_to, 6.4),
                 arrowprops=dict(arrowstyle="-|>", color=SUP, lw=1.5))
    ax2.annotate("", xy=(x_to, 6.4), xytext=(x_from, 6.4),
                 arrowprops=dict(arrowstyle="-", color=SUP, lw=1.5))
    ax2.text((x_from + x_to) / 2, 4.2,
             "⑥ HBM 侧腔旁路：进液腔经两个角窗直接下灌左右侧腔，无喷嘴、低速平流，再并入⑦",
             ha="center", fontsize=9.5, color=SUP)

    fig.suptitle("图 10　GB300 NVL2 托盘级冷却回路原理，与本冷板的对应关系",
                 fontsize=13.5, y=0.985)
    p = OUT / "fig10_tray_circuit.png"
    fig.savefig(p, dpi=185, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return p


def fig_orientation() -> Path:
    """图 11：冷板相对 B300 与托盘的摆放，以及建议的进出液通道。

    俯视，芯片面朝下。X=95 为双 die 轴，Y=75 为流向。
    进液边朝后面板，出液不从前方引出，而是沿盖顶中线折返到同一侧。
    """
    from matplotlib.patches import FancyBboxPatch, Rectangle

    fig, ax = plt.subplots(figsize=(13.2, 8.4))
    ax.set_xlim(-18, 118)
    ax.set_ylim(-28, 102)
    ax.set_aspect("equal")
    ax.set_axis_off()

    # 冷板外形 95 x 75，原点左下
    ax.add_patch(Rectangle((0, 0), 95, 75, facecolor="#f4e0cf",
                           edgecolor="#5c3a17", lw=1.6, zorder=2))
    # 两颗 die 与八颗 HBM（浅腔位置，芯片在板下方）
    for x in (19, 49):
        ax.add_patch(Rectangle((x, 23.5), 27, 28, facecolor="#f6d3b0",
                               edgecolor="#b42318", lw=1.1, zorder=3))
    ax.text(32.5, 37.5, "Die-A", ha="center", va="center", fontsize=9,
            color="#b42318", zorder=4)
    ax.text(62.5, 37.5, "Die-B", ha="center", va="center", fontsize=9,
            color="#b42318", zorder=4)
    for x in (5, 79):
        for y in (13.5, 25.5, 37.5, 49.5):
            ax.add_patch(Rectangle((x, y), 11, 10, facecolor="#efe6c9",
                                   edgecolor="#8a6a12", lw=0.7, zorder=3))
    ax.text(10.5, 8.2, "HBM ×4", ha="center", fontsize=8, color="#8a6a12")
    ax.text(84.5, 8.2, "HBM ×4", ha="center", fontsize=8, color="#8a6a12")

    # 现有扁口
    ax.add_patch(Rectangle((37.5, 73.2), 20, 2.6, facecolor="#1f6fb2",
                           edgecolor="#1f6fb2", zorder=5))
    ax.add_patch(Rectangle((37.5, -0.8), 20, 2.6, facecolor="#c0392b",
                           edgecolor="#c0392b", zorder=5))

    # 进液转接块 + 短管，朝后（+Y）
    ax.add_patch(FancyBboxPatch((34, 76), 27, 8, boxstyle="round,pad=0.4",
                                facecolor="#d9e9f7", edgecolor="#1f6fb2", lw=1.3, zorder=4))
    ax.annotate("", xy=(47.5, 90), xytext=(47.5, 84),
                arrowprops=dict(arrowstyle="-|>", color="#1f6fb2", lw=2.4))
    ax.text(47.5, 93.5, "进液  →  后面板供液歧管", ha="center", fontsize=10,
            color="#1f6fb2", fontweight="bold")

    # 出液沿盖顶中线折返
    ax.add_patch(FancyBboxPatch((41.5, 4), 6, 68, boxstyle="round,pad=0.15",
                                facecolor="#f6dcd8", edgecolor="#c0392b", lw=1.2,
                                zorder=4, alpha=0.95))
    ax.annotate("", xy=(44.5, 84), xytext=(44.5, 72),
                arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=2.2))
    ax.annotate("", xy=(62, 88), xytext=(50, 88),
                arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=2.2))
    ax.text(78, 88, "出液  →  后面板回液歧管", ha="left", va="center",
            fontsize=10, color="#c0392b", fontweight="bold")
    ax.text(44.5, 40, "盖顶中线\n回液槽", ha="center", va="center", fontsize=8,
            color="#c0392b", zorder=6,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))

    # 方向标注
    ax.annotate("", xy=(95, -8), xytext=(0, -8),
                arrowprops=dict(arrowstyle="-|>", color="#33404d", lw=1.2))
    ax.text(47.5, -12.5, "X  95 mm  ·  双 die 轴  ·  沿托盘宽度，两颗 GPU 并排",
            ha="center", fontsize=9, color="#33404d")
    ax.annotate("", xy=(-8, 75), xytext=(-8, 0),
                arrowprops=dict(arrowstyle="-|>", color="#33404d", lw=1.2))
    ax.text(-12, 37.5, "Y  75 mm\n流向\n沿托盘进深", ha="center", va="center",
            fontsize=9, color="#33404d", rotation=90)

    ax.text(47.5, -20, "Grace / 托盘前侧", ha="center", fontsize=9, color="#66757f")
    ax.text(47.5, 99, "后面板（歧管与 UQD）", ha="center", fontsize=9, color="#66757f")

    ax.set_title("图 11　摆放方向与进出液通道（俯视，芯片面朝下贴 B300）\n"
                 "进液边朝后面板；出液沿两 die 之间的盖顶中线折返，两根管都从后面板一侧引出",
                 fontsize=12, pad=8)
    p = OUT / "fig11_orientation.png"
    fig.savefig(p, dpi=185, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return p


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    parts = load()
    written = [
        fig_assembly(parts),
        fig_exploded(parts),
        fig_part(parts, "PLATE", 3, "余铜 + 短槽 + 隔离肋 + 周边钎焊框"),
        fig_part(parts, "COVER1", 4, "128 个微射流孔 + 回液窗口 + 下裙"),
        # COVER2 的腔朝下开，必须给仰视，否则双腔与隔腔肋一个都看不见
        fig_part(parts, "COVER2", 5, "双腔静压箱 + 隔腔铜肋 + 进出液侧口",
                 views=(("仰视（腔朝下，此视角才看得见）", BOTTOM),
                        ("由下方看的轴测", ISO_LOW))),
        fig_section(parts),
        fig_cutaway(parts),
        fig_flowpath(),
        fig_tray_circuit(),
        fig_orientation(),
    ]
    for p in written:
        print(f"  {p.relative_to(ROOT)}  {p.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()

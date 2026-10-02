"""预览后端：把顶视图 DXF 光栅化成 PNG。

图形定义复用 drawing.build_doc()，预览图与交付的 DXF 不会分叉。
产出可直接贴进 design/ 下的 HTML 设计报告做审图配图。
"""

from __future__ import annotations

from pathlib import Path

from ..model import Derived, Spec

# 图注是中文，Windows 上优先用雅黑，缺字体会退化成方框而不是报错
_CJK_FONTS = ["Microsoft YaHei", "SimHei", "DengXian", "sans-serif"]


def export(spec: Spec, d: Derived, out_dir: Path, dpi: int = 200) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    from . import drawing

    plt.rcParams["font.sans-serif"] = _CJK_FONTS
    plt.rcParams["axes.unicode_minus"] = False

    out_dir.mkdir(parents=True, exist_ok=True)
    doc = drawing.build_doc(spec, d)

    # 中文图注交给 matplotlib 画，ezdxf 的字体管理器认不到系统中文字体
    doc.layers.get(drawing.NOTE_LAYER).off()

    # 图注放独立子图。塞进同一个 axes 会和 finalize 的等比例约束打架
    # （matplotlib 会直接丢掉手动设的 ylim）。
    fig = plt.figure(figsize=(13, 11))
    ax = fig.add_axes([0.02, 0.28, 0.96, 0.70])
    ax.set_axis_off()

    ctx = RenderContext(doc)
    Frontend(ctx, MatplotlibBackend(ax)).draw_layout(doc.modelspace(), finalize=True)

    note_ax = fig.add_axes([0.02, 0.01, 0.96, 0.25])
    note_ax.set_axis_off()
    for i, text in enumerate(drawing.note_lines(spec, d)):
        note_ax.text(0.0, 1.0 - i * 0.14, text, transform=note_ax.transAxes,
                     fontsize=12, color="#333333", ha="left", va="top")

    path = out_dir / f"{spec.model}_top_view.png"
    fig.savefig(path, dpi=dpi, facecolor="white")
    plt.close(fig)
    return [path]

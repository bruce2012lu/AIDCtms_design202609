# -*- coding: utf-8 -*-
"""SVG 绘图原语：工程尺寸标注、剖面填充、等轴测投影。
所有工程图按 1 SVG 单位 = 1 mm 绘制。"""
import math

FONT = "Arial, Helvetica, sans-serif"
FONT_CN = "'Microsoft YaHei','PingFang SC',sans-serif"

INK = "#0b2748"
BLUE = "#2b6cb0"
TEAL = "#008b7a"
ORANGE = "#c05621"
RED = "#c53030"
GREY = "#607086"
CU = "#d9a06b"
CU_D = "#b97a45"
WATER = "#bee3f8"
FIN = "#38b2ac"


def _asw(sw, span):
    """尺寸线箭头宽度：箭长 = 6×sw，限制在标注跨距的 25% 以内，
    否则短尺寸会被两个箭头填满成蝴蝶结。"""
    return min(sw, abs(span) / 24.0)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


class Canvas:
    """一张 SVG。vb = (minx, miny, w, h) 用户单位。"""

    def __init__(self, vb, label=None, aria="", extra_defs=""):
        self.vb = vb
        self.parts = []
        self.defs = [extra_defs] if extra_defs else []
        self.aria = aria
        self._markers = set()
        self.label = label
        self._bx = []          # 已绘内容的包围盒采样点

    # ---------- 包围盒 ----------
    def _t(self, *pts):
        self._bx.extend(pts)

    def bbox(self):
        if not self._bx:
            return None
        xs = [p[0] for p in self._bx]
        ys = [p[1] for p in self._bx]
        return min(xs), min(ys), max(xs), max(ys)

    def autofit(self, margin=4.0):
        """按已绘内容自动设置 viewBox，避免裁切。"""
        b = self.bbox()
        if b:
            x0, y0, x1, y1 = b
            self.vb = (x0 - margin, y0 - margin,
                       (x1 - x0) + 2 * margin, (y1 - y0) + 2 * margin)
        return self

    # ---------- 基础 ----------
    def add(self, s):
        self.parts.append(s)
        return self

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=0.3, rx=0,
             extra=""):
        self._t((x, y), (x + w, y + h))
        return self.add(
            f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" {extra}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=0.25, extra=""):
        self._t((x1, y1), (x2, y2))
        return self.add(
            f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
            f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def circle(self, cx, cy, r, fill="none", stroke=INK, sw=0.2, extra=""):
        self._t((cx - r, cy - r), (cx + r, cy + r))
        return self.add(
            f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def path(self, d, fill="none", stroke=INK, sw=0.25, extra=""):
        return self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
                        f'stroke-width="{sw}" {extra}/>')

    def poly(self, pts, fill="none", stroke=INK, sw=0.25, extra=""):
        self._t(*pts)
        p = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
        return self.add(f'<polygon points="{p}" fill="{fill}" '
                        f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def polyline(self, pts, stroke=INK, sw=0.3, fill="none", extra=""):
        self._t(*pts)
        p = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
        return self.add(f'<polyline points="{p}" fill="{fill}" '
                        f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def text(self, x, y, s, size=2.6, fill=INK, anchor="start", cn=False,
             weight="normal", extra=""):
        f = FONT_CN if cn else FONT
        # 估算文字占位：中日韩字符按 1.0 em，其它按 0.55 em
        wch = sum(1.0 if ord(ch) > 0x2E80 else 0.55 for ch in str(s))
        w = wch * size
        if anchor == "middle":
            x0, x1 = x - w / 2, x + w / 2
        elif anchor == "end":
            x0, x1 = x - w, x
        else:
            x0, x1 = x, x + w
        self._t((x0, y - size), (x1, y + size * 0.3))
        return self.add(
            f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-family="{f}" '
            f'font-weight="{weight}" {extra}>{esc(s)}</text>')

    # ---------- 标记 ----------
    def _arrow(self, color):
        key = color.replace("#", "")
        mid = f"ar{key}"
        if mid not in self._markers:
            self._markers.add(mid)
            self.defs.append(
                f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" '
                f'markerWidth="6" markerHeight="6" orient="auto-start-reverse" '
                f'markerUnits="strokeWidth">'
                f'<path d="M0 0 L10 5 L0 10 z" fill="{color}"/></marker>')
        return mid

    def arrow(self, x1, y1, x2, y2, color=BLUE, sw=0.35,双向=False,
              dash=None, extra=""):
        m = self._arrow(color)
        self._t((x1, y1), (x2, y2))
        d = f'stroke-dasharray="{dash}" ' if dash else ""
        start = f'marker-start="url(#{m})" ' if 双向 else ""
        return self.add(
            f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
            f'stroke="{color}" stroke-width="{sw}" {d}{start}'
            f'marker-end="url(#{m})" {extra}/>')

    def curve_arrow(self, d, color=BLUE, sw=0.35, dash=None):
        m = self._arrow(color)
        ds = f'stroke-dasharray="{dash}" ' if dash else ""
        return self.add(f'<path d="{d}" fill="none" stroke="{color}" '
                        f'stroke-width="{sw}" {ds}'
                        f'marker-end="url(#{m})"/>')

    # ---------- 图案 ----------
    def hatch(self, pid, color=CU_D, sw=0.18, step=1.2, angle=45):
        if pid not in self._markers:
            self._markers.add(pid)
            self.defs.append(
                f'<pattern id="{pid}" width="{step}" height="{step}" '
                f'patternUnits="userSpaceOnUse" '
                f'patternTransform="rotate({angle})">'
                f'<line x1="0" y1="0" x2="0" y2="{step}" stroke="{color}" '
                f'stroke-width="{sw}"/></pattern>')
        return f"url(#{pid})"

    def grad(self, gid, stops, x1=0, y1=0, x2=1, y2=0, radial=False):
        if gid not in self._markers:
            self._markers.add(gid)
            st = "".join(f'<stop offset="{o}" stop-color="{c}"/>'
                         for o, c in stops)
            if radial:
                self.defs.append(
                    f'<radialGradient id="{gid}" cx="50%" cy="50%" r="60%">'
                    f'{st}</radialGradient>')
            else:
                self.defs.append(
                    f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" '
                    f'x2="{x2}" y2="{y2}">{st}</linearGradient>')
        return f"url(#{gid})"

    # ---------- 工程尺寸标注 ----------
    def dim_h(self, x1, x2, y, label=None, size=2.2, color=INK, ext=1.2,
              off=0, sw=0.18, below=False, tick=True):
        """水平尺寸线。off = 文字相对尺寸线的偏移"""
        if x2 < x1:
            x1, x2 = x2, x1
        self.line(x1, y - ext, x1, y + ext, color, sw)
        self.line(x2, y - ext, x2, y + ext, color, sw)
        self.arrow(x1, y, x2, y, color, _asw(sw, x2 - x1), 双向=True)
        t = label if label is not None else f"{x2-x1:.1f}"
        dy = (size * 1.15) if below else (-size * 0.5)
        self.text((x1 + x2) / 2, y + dy + off, t, size, color, "middle")
        return self

    def dim_v(self, y1, y2, x, label=None, size=2.2, color=INK, ext=1.2,
              off=0, sw=0.18, left=False):
        if y2 < y1:
            y1, y2 = y2, y1
        self.line(x - ext, y1, x + ext, y1, color, sw)
        self.line(x - ext, y2, x + ext, y2, color, sw)
        self.arrow(x, y1, x, y2, color, _asw(sw, y2 - y1), 双向=True)
        t = label if label is not None else f"{y2-y1:.1f}"
        a = "end" if left else "start"
        dx = -(size * 0.6) if left else (size * 0.6)
        self.text(x + dx + off, (y1 + y2) / 2 + size * 0.35, t, size,
                  color, a)
        return self

    def leader(self, x, y, tx, ty, label, size=2.2, color=INK, anchor="start",
               cn=True, sw=0.18):
        """引出标注：从 (x,y) 指向目标，文字在 (tx,ty)"""
        m = self._arrow(color)
        self.add(f'<path d="M{tx:.2f} {ty:.2f} L{(tx+x)/2:.2f} {ty:.2f} '
                 f'L{x:.2f} {y:.2f}" fill="none" stroke="{color}" '
                 f'stroke-width="{sw}" marker-end="url(#{m})"/>')
        dx = -0.8 if anchor == "end" else 0.8
        self.text(tx + dx, ty - 0.8, label, size, color, anchor, cn=cn)
        return self

    def centermark(self, cx, cy, r=2.0, color=GREY, sw=0.15):
        self.line(cx - r, cy, cx + r, cy, color, sw,
                  'stroke-dasharray="1.6 0.6 0.4 0.6"')
        self.line(cx, cy - r, cx, cy + r, color, sw,
                  'stroke-dasharray="1.6 0.6 0.4 0.6"')
        return self

    def section_mark(self, x, y, dirx, label, size=3.0, color=RED):
        """剖切符号"""
        self.line(x, y, x + 4 * dirx, y, color, 0.6)
        self.arrow(x + 4 * dirx, y, x + 4 * dirx, y + 4, color, 0.5)
        self.text(x + 4 * dirx + 1.2 * dirx, y + 1, label, size, color,
                  "middle" if dirx > 0 else "middle", weight="bold")
        return self

    # ---------- 输出 ----------
    def render(self, cls="svgfig"):
        mx, my, w, h = self.vb
        d = "".join(self.defs)
        defs = f"<defs>{d}</defs>" if d else ""
        aria = (f' role="img" aria-label="{esc(self.aria)}"'
                if self.aria else "")
        return (f'<svg viewBox="{mx:.2f} {my:.2f} {w:.2f} {h:.2f}" '
                f'xmlns="http://www.w3.org/2000/svg" class="{cls}"{aria}>'
                f'{defs}{"".join(self.parts)}</svg>')


# ============================================================
# 等轴测投影
# ============================================================
COS30 = math.cos(math.radians(30))
SIN30 = math.sin(math.radians(30))


def iso(x, y, z, scale=1.0):
    """右手系 (x 右前, y 左后, z 上) -> 屏幕坐标（y 向下为正）"""
    sx = (x - y) * COS30 * scale
    sy = ((x + y) * SIN30 - z) * scale
    return sx, sy


def iso_box(c, x, y, z, dx, dy, dz, top, front, side, stroke=INK, sw=0.25,
            scale=1.0, extra=""):
    """画一个等轴测长方体的三个可见面（顶 / 前(x正面) / 侧(y正面)）"""
    P = lambda a, b, cc: iso(a, b, cc, scale)
    # 顶面 z = z+dz
    t = [P(x, y, z + dz), P(x + dx, y, z + dz),
         P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)]
    # 前面 y = y  (朝右下)
    f = [P(x, y, z + dz), P(x + dx, y, z + dz),
         P(x + dx, y, z), P(x, y, z)]
    # 侧面 x = x  (朝左下)
    s = [P(x, y, z + dz), P(x, y + dy, z + dz),
         P(x, y + dy, z), P(x, y, z)]
    c.poly(f, front, stroke, sw, extra=extra)
    c.poly(s, side, stroke, sw, extra=extra)
    c.poly(t, top, stroke, sw, extra=extra)
    return t, f, s

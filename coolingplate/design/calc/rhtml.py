# -*- coding: utf-8 -*-
"""报告 HTML 片段助手。"""

CONF = {
    "H": '<span class="tag">高</span>',
    "M": '<span class="tag tagw">中</span>',
    "L": '<span class="tag tagr">低 / 待冻结</span>',
    "F": '<span class="tag tagb">待冻结</span>',
}


def h2(n, t, anchor):
    return f'<h2 id="{anchor}">{n}　{t}</h2>'


def h3(t):
    return f"<h3>{t}</h3>"


def h4(t):
    return f"<h4>{t}</h4>"


def p(t, cls=None):
    c = f' class="{cls}"' if cls else ""
    return f"<p{c}>{t}</p>"


def lead(t):
    return f'<p class="lead">{t}</p>'


def note(t, kind=""):
    k = f" {kind}" if kind else ""
    return f'<div class="note{k}">{t}</div>'


def ul(items, cls="tight"):
    li = "".join(f"<li>{i}</li>" for i in items)
    return f'<ul class="{cls}">{li}</ul>'


def ol(items, cls="tight"):
    li = "".join(f"<li>{i}</li>" for i in items)
    return f'<ol class="{cls}">{li}</ol>'


def table(headers, rows, cls="", widths=None):
    cl = f' class="{cls}"' if cls else ""
    cg = ""
    if widths:
        cg = "<colgroup>" + "".join(
            f'<col style="width:{w}">' for w in widths) + "</colgroup>"
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = ""
    for r in rows:
        if isinstance(r, str):          # 分组标题行
            body += (f'<tr class="grp"><td colspan="{len(headers)}">'
                     f"{r}</td></tr>")
            continue
        body += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    return (f"<table{cl}>{cg}<thead><tr>{th}</tr></thead>"
            f"<tbody>{body}</tbody></table>")


def cards(items, cols=4):
    """items: [(value, label, cls)]"""
    inner = "".join(
        f'<div class="card {c}"><b>{v}</b>{l}</div>' for v, l, c in items)
    return f'<div class="grid g{cols}">{inner}</div>'


def fig(svg, num, title, caption, cls="svgbox"):
    return (f'<figure class="{cls}">{svg}'
            f'<figcaption><strong>{num}</strong>　{title}'
            f'<span class="cap">{caption}</span></figcaption></figure>')


def imgfig(src, num, title, caption, alt=""):
    return (f'<figure class="pfig"><img src="{src}" alt="{alt or title}">'
            f'<figcaption><strong>{num}</strong>　{title}'
            f'<span class="cap">{caption}</span></figcaption></figure>')


def kv(rows, cls="kv"):
    body = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows)
    return f'<dl class="{cls}">{body}</dl>'


def formula(latexish, result=None, note_=None):
    r = f'<span class="fres">{result}</span>' if result else ""
    n = f'<span class="fnote">{note_}</span>' if note_ else ""
    return f'<div class="formula"><code>{latexish}</code>{r}{n}</div>'


def pill(t, cls=""):
    return f'<span class="pill {cls}">{t}</span>'


def num(v, d=2):
    return f"{v:,.{d}f}"

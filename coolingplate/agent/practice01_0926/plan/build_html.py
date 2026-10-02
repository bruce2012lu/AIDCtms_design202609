# -*- coding: utf-8 -*-
"""把 plan/ 下的 Markdown 生成单文件 HTML：左侧可折叠目录、点击跳转、滚动高亮。

Markdown 是唯一源文件。用法：python plan/build_html.py [文件.md ...]，缺省处理本目录全部 *.md。
"""
from __future__ import annotations

import datetime as _dt
import html
import sys
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode

HERE = Path(__file__).resolve().parent

CSS = r"""
:root{--side:310px;--ink:#1f2d3d;--muted:#5b6b7f;--line:#dde3ea;--accent:#1a6fb5;--bg:#f7f9fb;--hl:#e8f1fb}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:"Microsoft YaHei","PingFang SC","Noto Sans CJK SC",sans-serif;color:var(--ink);background:#fff;line-height:1.75;font-size:15px}
#side{position:fixed;top:0;left:0;bottom:0;width:var(--side);background:var(--bg);border-right:1px solid var(--line);display:flex;flex-direction:column;z-index:20;transition:transform .2s}
#side header{padding:14px 14px 8px;border-bottom:1px solid var(--line)}
#side header .t{font-weight:bold;font-size:14px;line-height:1.4}
#side header .tools{display:flex;gap:6px;margin-top:8px}
#side header button{flex:1;font-size:12px;padding:3px 0;border:1px solid var(--line);background:#fff;border-radius:4px;cursor:pointer;color:var(--muted)}
#side header button:hover{color:var(--accent);border-color:var(--accent)}
#side header input{width:100%;margin-top:8px;padding:4px 8px;font-size:12px;border:1px solid var(--line);border-radius:4px}
#toc{overflow-y:auto;padding:8px 6px 40px;flex:1;font-size:13px}
#toc ul{list-style:none;margin:0;padding-left:12px}
#toc>ul{padding-left:0}
#toc li{margin:1px 0}
#toc .row{display:flex;align-items:flex-start}
#toc .tg{width:18px;flex:0 0 18px;cursor:pointer;color:var(--muted);user-select:none;text-align:center;line-height:22px;font-size:11px}
#toc .tg.empty{cursor:default;visibility:hidden}
#toc a{display:block;flex:1;padding:1px 6px;border-radius:4px;color:var(--ink);text-decoration:none;line-height:22px}
#toc a:hover{background:#eef2f6}
#toc a.active{background:var(--hl);color:var(--accent);font-weight:bold}
#toc li.collapsed>ul{display:none}
#toc li.hide{display:none}
#toc .lv2>.row a{font-weight:600}
#main{margin-left:var(--side);padding:28px 48px 80px;max-width:calc(var(--side) + 1180px)}
#main h1{font-size:26px;border-bottom:3px solid var(--accent);padding-bottom:8px}
#main h2{font-size:21px;margin-top:42px;border-bottom:1px solid var(--line);padding-bottom:6px;color:#16324f}
#main h3{font-size:17px;margin-top:28px;color:#1d4a73}
#main h4{font-size:15px;margin-top:20px}
#main h2,#main h3,#main h4{scroll-margin-top:12px}
blockquote{margin:12px 0;padding:8px 14px;background:#f4f7fa;border-left:4px solid var(--accent);color:var(--muted)}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13.5px;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:6px 9px;vertical-align:top;text-align:left}
th{background:#eef3f8;white-space:nowrap}
tr:nth-child(even) td{background:#fafbfc}
code{background:#f1f3f5;padding:1px 5px;border-radius:3px;font-family:Consolas,"Courier New",monospace;font-size:.9em}
pre{background:#f6f8fa;border:1px solid var(--line);padding:12px 14px;overflow-x:auto;border-radius:6px;line-height:1.5}
pre code{background:none;padding:0}
figure.flow{margin:16px 0;padding:10px;border:1px solid var(--line);border-radius:8px;background:#fff;overflow-x:auto}
figure.flow svg{width:100%;min-width:900px;height:auto;display:block}
figcaption{font-size:12.5px;color:var(--muted);margin-top:6px;text-align:center}
#fab{display:none;position:fixed;left:10px;top:10px;z-index:30;border:1px solid var(--line);background:#fff;border-radius:6px;padding:4px 10px;cursor:pointer}
footer{margin-top:60px;font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:10px}
@media (max-width:980px){#side{transform:translateX(-100%)}body.open #side{transform:none}#main{margin-left:0;padding:48px 18px}#fab{display:block}}
@media print{#side,#fab{display:none}#main{margin-left:0}}
"""

JS = r"""
(function(){
  var toc=document.getElementById('toc');
  toc.addEventListener('click',function(e){
    var t=e.target;
    if(t.classList.contains('tg')&&!t.classList.contains('empty')){
      var li=t.closest('li');li.classList.toggle('collapsed');
      t.textContent=li.classList.contains('collapsed')?'\u25B8':'\u25BE';
    }
    if(t.tagName==='A'&&window.innerWidth<=980){document.body.classList.remove('open');}
  });
  function setAll(collapse){
    toc.querySelectorAll('li.has').forEach(function(li){
      li.classList.toggle('collapsed',collapse);
      li.querySelector(':scope>.row>.tg').textContent=collapse?'\u25B8':'\u25BE';
    });
  }
  document.getElementById('bx').onclick=function(){setAll(false)};
  document.getElementById('bc').onclick=function(){setAll(true)};
  document.getElementById('fab').onclick=function(){document.body.classList.toggle('open')};
  var q=document.getElementById('q');
  q.addEventListener('input',function(){
    var v=q.value.trim().toLowerCase();
    toc.querySelectorAll('li').forEach(function(li){li.classList.remove('hide')});
    if(!v)return;
    toc.querySelectorAll('li').forEach(function(li){
      var hit=li.textContent.toLowerCase().indexOf(v)>=0;
      if(!hit)li.classList.add('hide');
      else if(li.classList.contains('has')){li.classList.remove('collapsed');li.querySelector(':scope>.row>.tg').textContent='\u25BE';}
    });
  });
  var links={};toc.querySelectorAll('a').forEach(function(a){links[decodeURIComponent(a.getAttribute('href').slice(1))]=a});
  var heads=Array.prototype.filter.call(document.querySelectorAll('#main h2[id],#main h3[id],#main h4[id]'),function(h){return links[h.id]});
  var cur=null;
  function activate(id){
    if(cur===id)return;cur=id;
    toc.querySelectorAll('a.active').forEach(function(a){a.classList.remove('active')});
    var a=links[id];if(!a)return;a.classList.add('active');
    var li=a.closest('li');
    while(li){if(li.classList.contains('has')&&li.classList.contains('collapsed')){li.classList.remove('collapsed');li.querySelector(':scope>.row>.tg').textContent='\u25BE';}
      li=li.parentElement.closest('li');}
    var r=a.getBoundingClientRect(),tr=toc.getBoundingClientRect();
    if(r.top<tr.top+40||r.bottom>tr.bottom-40){toc.scrollTop+=r.top-tr.top-tr.height/3;}
  }
  function spy(){
    var y=window.scrollY+80,id=heads.length?heads[0].id:null;
    for(var i=0;i<heads.length;i++){if(heads[i].offsetTop<=y)id=heads[i].id;else break;}
    if(id)activate(id);
  }
  var tick=false;
  window.addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(function(){spy();tick=false;});}});
  spy();
})();
"""


def _toc_html(tokens: list[dict], depth: int = 2) -> str:
    if not tokens:
        return ""
    out = ["<ul>"]
    for t in tokens:
        kids = t.get("children") or []
        cls = f"lv{t['level']}" + (" has" if kids else "")
        if kids and t["level"] >= 3:
            cls += " collapsed"
        arrow = ("\u25B8" if "collapsed" in cls else "\u25BE") if kids else ""
        tg = f'<span class="tg{"" if kids else " empty"}">{arrow}</span>'
        out.append(
            f'<li class="{cls}"><div class="row">{tg}'
            f'<a href="#{html.escape(t["id"])}">{t["name"]}</a></div>'
            f"{_toc_html(kids, depth + 1)}</li>"
        )
    out.append("</ul>")
    return "".join(out)


def build(md_path: Path) -> Path:
    text = md_path.read_text(encoding="utf-8")
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "attr_list", "sane_lists", "toc"],
        extension_configs={"toc": {"slugify": slugify_unicode, "toc_depth": "1-4", "permalink": False}},
        output_format="html5",
    )
    body = md.convert(text)
    tokens = md.toc_tokens
    title = md_path.stem
    if len(tokens) == 1 and tokens[0]["level"] == 1:
        title = html.unescape(tokens[0]["name"])
        tokens = tokens[0].get("children", [])
    stamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<button id="fab">目录</button>
<nav id="side">
<header>
<div class="t">{html.escape(title)}</div>
<div class="tools"><button id="bx">全部展开</button><button id="bc">全部折叠</button></div>
<input id="q" type="search" placeholder="筛选目录…">
</header>
<div id="toc">{_toc_html(tokens)}</div>
</nav>
<main id="main">
{body}
<footer>由 <code>{html.escape(md_path.name)}</code> 经 <code>plan/build_html.py</code> 生成 · {stamp}。Markdown 为唯一源文件，请改 MD 后重新生成。</footer>
</main>
<script>{JS}</script>
</body>
</html>
"""
    out = md_path.with_suffix(".html")
    out.write_text(page, encoding="utf-8")
    return out


def main(argv: list[str]) -> None:
    paths = [Path(a) for a in argv] or sorted(HERE.glob("*.md"))
    for p in paths:
        print(build(p.resolve()))


if __name__ == "__main__":
    main(sys.argv[1:])

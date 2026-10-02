"""内存中读取 PDF（不落盘），打印页数、元数据标题与首页前几行，用于判断候选直链是哪份文档。

用法: python peek.py <pdf_url> [<pdf_url> ...]
"""
import sys

import fitz
import httpx

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}
for u in sys.argv[1:]:
    try:
        r = httpx.get(u, follow_redirects=True, timeout=60, headers=UA)
        if not r.content.startswith(b"%PDF"):
            print(f"== {u}\n   非 PDF status={r.status_code} ctype={r.headers.get('content-type')}")
            continue
        with fitz.open(stream=r.content, filetype="pdf") as d:
            head = " | ".join(d[0].get_text().split("\n")[:6])
            print(f"== {u}\n   pages={d.page_count} bytes={len(r.content)} title={d.metadata.get('title')!r}\n   {head}")
    except Exception as e:  # noqa: BLE001
        print(f"== {u}\n   ERR {e}")

"""探测落地页里的 PDF 直链（只读 GET，不保存文件）。

用法: python probe.py <url> [<url> ...]
"""
import re
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}
for u in sys.argv[1:]:
    try:
        r = httpx.get(u, follow_redirects=True, timeout=40, headers=UA)
        print(f"== {u}\n   status={r.status_code} final={r.url} ctype={r.headers.get('content-type')} len={len(r.content)}")
        if "html" in r.headers.get("content-type", ""):
            links = set(re.findall(r'https?://[^"\'\s<>]+?\.pdf(?:\?[^"\'\s<>]*)?', r.text))
            links |= set(re.findall(r'["\'](/[^"\'\s<>]+?\.pdf)["\']', r.text))
            for x in sorted(links)[:40]:
                print("   pdf:", x)
    except Exception as e:  # noqa: BLE001
        print(f"== {u}\n   ERR {e}")

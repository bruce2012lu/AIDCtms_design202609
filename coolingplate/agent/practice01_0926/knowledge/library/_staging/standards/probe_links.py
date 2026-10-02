"""检索辅助：列出页面中的链接（只读，不下载文件）。用法: python probe_links.py URL [regex]"""
import re
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")
url = sys.argv[1]
pat = re.compile(sys.argv[2], re.I) if len(sys.argv) > 2 else None
r = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60, follow_redirects=True)
print(r.status_code, r.url)
for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.S):
    href, text = m.group(1), re.sub(r"<[^>]+>|\s+", " ", m.group(2)).strip()
    if pat is None or pat.search(href) or pat.search(text):
        print(href, "|", text[:140])

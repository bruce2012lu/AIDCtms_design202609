"""解析落地页，列出疑似 PDF 链接（仅读）。用法: python links.py URL [URL...]"""
import re
import sys
from urllib.parse import urljoin
import httpx

sys.stdout.reconfigure(encoding="utf-8")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 cp-design-librarian/0.1"}
PAT = re.compile(r'(?:href|content)="([^"]+)"', re.I)
KEEP = re.compile(r"(\.pdf|/document|bitstream|retrieve/|download|viewcontent|/files/)", re.I)
for u in sys.argv[1:]:
    try:
        r = httpx.get(u, headers=H, follow_redirects=True, timeout=40)
        print(u, r.status_code, str(r.url), r.headers.get("content-type"))
        seen = []
        for l in PAT.findall(r.text):
            if KEEP.search(l):
                a = urljoin(str(r.url), l.replace("&amp;", "&"))
                if a not in seen:
                    seen.append(a)
        for a in seen[:12]:
            print("   ", a)
    except Exception as e:  # noqa: BLE001
        print(u, "ERR", e)

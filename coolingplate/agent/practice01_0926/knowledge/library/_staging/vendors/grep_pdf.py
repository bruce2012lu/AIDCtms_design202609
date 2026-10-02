"""按页检索 PDF 关键词，输出 页码 | 行文本（供摘录 key_data 时定位）。

用法: python grep_pdf.py <pdf> <regex> [context_lines]
"""
import re
import sys

import fitz

sys.stdout.reconfigure(encoding="utf-8")
pdf, pat = sys.argv[1], re.compile(sys.argv[2], re.I)
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 0
with fitz.open(pdf) as doc:
    for i, page in enumerate(doc, 1):
        lines = page.get_text().splitlines()
        for k, ln in enumerate(lines):
            if pat.search(ln):
                seg = lines[max(0, k - ctx): k + ctx + 1]
                print(f"p.{i} | " + " ⏎ ".join(s.strip() for s in seg))

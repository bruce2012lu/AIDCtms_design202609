import re
import sys

import fitz

sys.stdout.reconfigure(encoding="utf-8")
path, pattern = sys.argv[1], sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 200
with fitz.open(path) as d:
    for i, page in enumerate(d, start=1):
        t = re.sub(r"\s+", " ", page.get_text())
        for m in re.finditer(pattern, t, re.IGNORECASE):
            s = max(0, m.start() - width)
            print(f"p.{i}: ...{t[s:m.end() + width]}...")

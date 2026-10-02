import sys

import fitz

sys.stdout.reconfigure(encoding="utf-8")
path = sys.argv[1]
first, last = int(sys.argv[2]), int(sys.argv[3])
limit = int(sys.argv[4]) if len(sys.argv) > 4 else 100000
with fitz.open(path) as d:
    for i in range(first - 1, min(last, d.page_count)):
        print(f"===== p.{i + 1}")
        print(d[i].get_text()[:limit])

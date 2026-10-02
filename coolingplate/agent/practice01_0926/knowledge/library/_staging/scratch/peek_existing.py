import re
import sys
from pathlib import Path

import fitz

sys.stdout.reconfigure(encoding="utf-8")
root = Path(__file__).resolve().parents[6] / "papers" / "pdfs"
for p in sorted(root.glob("*.pdf")):
    with fitz.open(p) as d:
        first = re.sub(r"\s+", " ", d[0].get_text("text"))[:420]
        doi = re.search(r"10\.\d{4,9}/[^\s\"<>]+", " ".join(d[i].get_text() for i in range(min(2, d.page_count))))
        print(f"== {p.name} | pages={d.page_count} | meta_title={d.metadata.get('title')!r} | doi={doi.group(0) if doi else None}")
        print("   ", first)

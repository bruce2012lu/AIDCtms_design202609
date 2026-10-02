"""按页列出含关键词且含数字的句子。用法: python sent.py <id> <regex> [max]"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
pid, pat = sys.argv[1], re.compile(sys.argv[2], re.I)
cap = int(sys.argv[3]) if len(sys.argv) > 3 else 40
t = (Path(__file__).parent / "txt" / f"{pid}.txt").read_text(encoding="utf-8")
k = 0
for pg in t.split("===== p.")[1:]:
    n = pg.split(" ")[0]
    body = re.sub(r"-\s*\n", "", pg).replace("\n", " ")
    for s in re.split(r"(?<=[.;])\s+", body):
        if pat.search(s) and re.search(r"\d", s) and len(s) < 450:
            print(f"p.{n} | {s.strip()}")
            k += 1
            if k >= cap:
                sys.exit()

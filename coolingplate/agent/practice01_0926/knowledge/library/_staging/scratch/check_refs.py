import json
import re
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
reg = json.loads((LIB / "registry" / "entries.json").read_text(encoding="utf-8"))
ids = {e["id"] for e in reg}
pat = re.compile(r"\b((?:pap|hbk|std|ven|pat|dat|int)-[0-9]{4}-[a-z0-9]+(?:-[a-z0-9]+)*)\b")
for f in sorted(list((LIB / "cards").glob("*.md")) + list((LIB / "reports").glob("*.md"))):
    missing = sorted({m for m in pat.findall(f.read_text(encoding="utf-8")) if m not in ids})
    if missing:
        print(f.name, "MISSING:", missing)
for q in sys.argv[1:]:
    for e in reg:
        blob = json.dumps(e, ensure_ascii=False).lower()
        if q.lower() in blob:
            print(q, "→", e["id"], "|", e["access"]["status"], "|", e["title"][:80])

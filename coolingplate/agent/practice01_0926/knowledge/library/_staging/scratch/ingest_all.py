import json
import sys
import time
from pathlib import Path

LIB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LIB / "tools"))
sys.stdout.reconfigure(encoding="utf-8")
import kb  # noqa: E402

t0 = time.time()
print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in kb.merge(LIB, write=True, replace=True).items()}, ensure_ascii=False))
reg = kb.registry(LIB)
pats = [e["id"] for e in reg if e["type"] == "patent"]
others = [e["id"] for e in reg if e["type"] != "patent"]
r1 = kb.ingest(LIB, others)
r2 = kb.ingest(LIB, pats, figures=False)
for r in (r1, r2):
    for x in r["ingested"]:
        print("OK", x["id"], x["pages"], x["chunks"], x["tables"], x["figures"])
    for x in r["failed"]:
        print("FAIL", x)
print(json.dumps(kb.index(LIB), ensure_ascii=False))
print(json.dumps(kb.stats(LIB), ensure_ascii=False))
print("seconds", round(time.time() - t0))

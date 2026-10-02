import sys
import time
from pathlib import Path

LIB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LIB / "tools"))
sys.stdout.reconfigure(encoding="utf-8")
import kb  # noqa: E402

t0 = time.time()
ids = [e["id"] for e in kb.registry(LIB)
       if e["type"] != "patent" and (LIB / "derived" / e["id"] / "figures").exists()]
res = kb.ingest(LIB, ids, force=True)
for x in res["ingested"]:
    print("OK", x["id"], x["figures"])
for x in res["failed"]:
    print("FAIL", x)
print(kb.index(LIB))
size = sum(p.stat().st_size for p in (LIB / "derived").rglob("*") if p.is_file())
print("derived MB", round(size / 2**20, 1), "seconds", round(time.time() - t0))

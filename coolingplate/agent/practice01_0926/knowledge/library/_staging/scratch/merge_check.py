import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LIB / "tools"))
sys.stdout.reconfigure(encoding="utf-8")
import kb  # noqa: E402

write = "--write" in sys.argv
res = kb.merge(LIB, write=write, replace="--replace" in sys.argv)
print("total", res["total"], "added", len(res["added"]), "replaced", len(res["replaced"]),
      "skipped", len(res["skipped_existing"]), "written", res["written"])
for x in res["invalid"]:
    print("INVALID", x)

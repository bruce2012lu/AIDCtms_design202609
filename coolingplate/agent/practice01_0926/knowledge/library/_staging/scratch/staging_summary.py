import collections
import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
ids = collections.Counter()
for src in sorted((LIB / "_staging").glob("*/entries.json")):
    items = json.loads(src.read_text(encoding="utf-8"))
    acc = collections.Counter(e["access"]["status"] for e in items)
    tl = collections.Counter(e["trust_level"] for e in items)
    bm = sum(1 for e in items if e.get("benchmark_candidate"))
    print(f"{src.parent.name:15s} n={len(items):3d} access={dict(acc)} trust={dict(sorted(tl.items()))} bench={bm}")
    ids.update(e["id"] for e in items)
dups = [k for k, v in ids.items() if v > 1]
print("duplicate ids across topics:", dups)
if "--list" in sys.argv:
    topic = sys.argv[sys.argv.index("--list") + 1]
    for e in json.loads((LIB / "_staging" / topic / "entries.json").read_text(encoding="utf-8")):
        print(f"{e['id']} | {e['trust_level']} | {e['access']['status']} | bm={e.get('benchmark_candidate', False)} | {e['title'][:90]}")

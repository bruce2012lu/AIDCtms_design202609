"""按 plan.json 调用 tools/fetch.py 下载专利公开 PDF，结果写 fetch_results.json。"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
LIB = HERE.parents[1]
FETCH = LIB / "tools" / "fetch.py"

pages = {x["query"]: x for x in json.loads((HERE / "all.json").read_text(encoding="utf-8"))}
pages.update({x["query"]: x for x in json.loads((HERE / "r4.json").read_text(encoding="utf-8"))})
plan = json.loads((HERE / "plan.json").read_text(encoding="utf-8"))
out_path = HERE / "fetch_results.json"
results = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}

for eid, no, pdf_no, _ in plan:
    if not pdf_no or (eid in results and results[eid].get("sha256")):
        continue
    url = pages[pdf_no]["pdf"]
    p = subprocess.run([sys.executable, str(FETCH), "--url", url, "--id", eid,
                        "--category", "patents", "--topic", "patents"],
                       capture_output=True, text=True, encoding="utf-8")
    try:
        results[eid] = json.loads(p.stdout.strip().splitlines()[-1])
        results[eid]["pdf_from"] = pdf_no
    except Exception:  # noqa: BLE001
        results[eid] = {"error": (p.stdout + p.stderr)[-500:], "url": url}
    print(eid, "OK" if results[eid].get("sha256") else results[eid].get("error"))

out_path.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")

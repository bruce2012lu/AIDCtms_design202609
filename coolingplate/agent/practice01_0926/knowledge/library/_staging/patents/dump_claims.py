import json

d = {x["query"]: x for x in json.load(open("all.json", encoding="utf-8")) + json.load(open("r4.json", encoding="utf-8"))}
plan = json.load(open("plan.json", encoding="utf-8"))
with open("claims_dump.txt", "w", encoding="utf-8") as f:
    for eid, no, pdf, _ in plan:
        x = d[no]
        f.write(f"=== {eid} | {no} | {x.get('claims_count')} claims | inv {x.get('inventors')[:3]}\n")
        f.write(f"ABS: {(x.get('abstract') or '')[:700]}\n")
        f.write(f"C1: {(x.get('claim1') or '')[:1600]}\n\n")

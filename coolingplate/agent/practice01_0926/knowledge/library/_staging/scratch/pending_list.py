import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
reg = json.loads((LIB / "registry" / "entries.json").read_text(encoding="utf-8"))
order = {"standard": 0, "handbook": 1, "vendor_doc": 2, "paper": 3, "dataset": 4, "patent": 5}
label = {"standard": "标准规范", "handbook": "手册", "vendor_doc": "厂商文档", "paper": "论文",
         "dataset": "数据集", "patent": "专利"}
status_zh = {"pending_user": "待用户获取（免费/开放，需浏览器）", "paywalled": "付费", "login_required": "需登录/NDA",
             "metadata_only": "仅元数据", "not_found": "未找到"}
out_lines: list[str] = []
print = lambda s="": out_lines.append(s)  # noqa: E731,A001
rows = [e for e in reg if e["access"]["status"] != "downloaded"]
rows.sort(key=lambda e: (order.get(e["type"], 9), ["L1", "L2", "L3", "L4", "L5", "L6"].index(e["trust_level"]), e["id"]))
cur = None
for e in rows:
    if e["type"] != cur:
        cur = e["type"]
        print(f"\n### {label.get(cur, cur)}\n")
        print("| id | 标题 | 可信度 | 状态 | 合法获取途径 |")
        print("|---|---|---|---|---|")
    how = (e["access"].get("how_to_get") or "").replace("|", "/").replace("\n", " ")
    title = e["title"].replace("|", "/")
    print(f"| `{e['id']}` | {title[:90]} | {e['trust_level']} | {status_zh.get(e['access']['status'], e['access']['status'])} | {how[:160]} |")
print(f"\n合计 {len(rows)} 条。")
head = (LIB / "_staging" / "scratch" / "pending_head.md").read_text(encoding="utf-8")
(LIB / "reports" / "待用户获取清单.md").write_text(head + "\n## 全部未下载条目（由登记册生成）\n" + "\n".join(out_lines) + "\n", encoding="utf-8")
sys.stdout.write(f"rows={len(rows)}\n")

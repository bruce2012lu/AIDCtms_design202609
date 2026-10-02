import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
d = Path(r"C:\Users\Administrator\.cursor\projects\d-agents2026-agents2026-agents-AIDCtms-coolingplate-agent-practice01-0926\agent-transcripts\5bbb4fa4-1941-42af-b1df-1b282ffddba8\subagents")
want = sys.argv[1] if len(sys.argv) > 1 else ""
for p in sorted(d.glob("*.jsonl")):
    if want and not p.stem.startswith(want):
        continue
    last = None
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        if m.get("role") == "assistant":
            parts = m.get("message", {}).get("content", [])
            text = "".join(c.get("text", "") for c in parts if isinstance(c, dict) and c.get("type") == "text")
            if text.strip():
                last = text
    print("=" * 20, p.stem[:8])
    print(last)

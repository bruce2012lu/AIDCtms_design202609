"""调用 tools/fetch.py 的 fetch()，仅把 UA 换成如实标识的非浏览器 UA。

部分机构库（HAL 等）的 Anubis 反爬页只拦截浏览器 UA，对如实声明的工具 UA 直接放行；
其余文件头校验、盗版站拒绝、sha256、下载日志逻辑完全沿用 fetch.py。
用法: python fetch_honest_ua.py --url URL --id ID [--ext pdf]
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import fetch  # noqa: E402

fetch.UA = "cp-design-librarian/0.1 (knowledge-base research; python-httpx)"
ap = argparse.ArgumentParser()
ap.add_argument("--url", required=True)
ap.add_argument("--id", required=True)
ap.add_argument("--ext", default="pdf")
a = ap.parse_args()
print(json.dumps(fetch.fetch(a.url, a.id, "papers", a.ext, "papers-jet"), ensure_ascii=False))

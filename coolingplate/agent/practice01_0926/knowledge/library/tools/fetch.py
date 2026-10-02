"""合法公开文件下载 + sha256 登记。

用法:
  python fetch.py --url URL --id pap-1977-martin-impinging-jets --category papers [--ext pdf] [--topic vendors]
  python fetch.py --verify            复核 files/ 下全部文件的 sha256 与下载日志

只下载开放获取论文、官网公开 PDF、公开标准全文、专利公开文本。
付费墙或需登录的不要下载，在条目里写 access.status = paywalled / login_required。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

LIB = Path(__file__).resolve().parents[1]
FILES = LIB / "files"
LOG = LIB / "_staging" / "downloads.log.jsonl"
CATEGORIES = {"papers", "handbooks", "standards", "vendor_docs", "patents", "datasets"}
ID_RE = re.compile(r"^(pap|hbk|std|ven|pat|dat|int)-[0-9]{4}-[a-z0-9]+(-[a-z0-9]+)*$")
DENY = ("sci-hub", "scihub", "libgen", "library.lol", "z-lib", "zlibrary", "1lib", "booksc",
        "annas-archive", "pdfdrive", "dokumen.pub", "vdoc.pub", "ebin.pub", "epdf.pub")
MAX_BYTES = 80 * 1024 * 1024
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 cp-design-librarian/0.1")
MAGIC = {"pdf": b"%PDF", "zip": b"PK", "xlsx": b"PK", "png": b"\x89PNG"}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_pages(path: Path) -> int | None:
    try:
        import fitz
        with fitz.open(path) as doc:
            return doc.page_count
    except Exception:  # noqa: BLE001
        return None


def check_url(url: str) -> None:
    host = (urlparse(url).hostname or "").lower()
    if any(bad in host for bad in DENY):
        raise SystemExit(f"拒绝：{host} 属于盗版或影子图书馆站点")
    if urlparse(url).scheme not in {"http", "https"}:
        raise SystemExit("只接受 http/https")


def fetch(url: str, entry_id: str, category: str, ext: str, topic: str) -> dict:
    if not ID_RE.match(entry_id):
        raise SystemExit(f"id 不合规：{entry_id}")
    if category not in CATEGORIES:
        raise SystemExit(f"category 必须是 {sorted(CATEGORIES)}")
    check_url(url)
    import httpx

    dest_dir = FILES / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{entry_id}.{ext}"
    tmp = dest.with_suffix(dest.suffix + ".part")
    headers = {"User-Agent": UA, "Accept": "*/*"}
    with httpx.Client(follow_redirects=True, timeout=90, headers=headers) as client:
        with client.stream("GET", url) as r:
            final_url = str(r.url)
            check_url(final_url)
            if r.status_code != 200:
                raise SystemExit(f"HTTP {r.status_code}：{final_url}")
            ctype = r.headers.get("content-type", "")
            size = 0
            with tmp.open("wb") as f:
                for chunk in r.iter_bytes():
                    size += len(chunk)
                    if size > MAX_BYTES:
                        f.close()
                        tmp.unlink(missing_ok=True)
                        raise SystemExit("文件超过 80 MB，改为只登记元数据")
                    f.write(chunk)
    head = tmp.read_bytes()[:8]
    want = MAGIC.get(ext)
    if want and not head.startswith(want):
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"文件头不是 {ext}（content-type={ctype}），多半是登录页或拦截页，未保存")
    tmp.replace(dest)
    rec = {
        "id": entry_id,
        "category": category,
        "path": str(dest.relative_to(LIB)).replace("\\", "/"),
        "sha256": sha256_of(dest),
        "bytes": dest.stat().st_size,
        "pages": pdf_pages(dest) if ext == "pdf" else None,
        "source_url": final_url,
        "requested_url": url,
        "content_type": ctype,
        "downloaded_at": date.today().isoformat(),
        "topic": topic,
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def verify() -> dict:
    logged = {}
    if LOG.exists():
        for line in LOG.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                logged[rec["path"]] = rec
    rows = []
    for p in sorted(FILES.rglob("*")):
        if not p.is_file() or p.suffix == ".part":
            continue
        rel = str(p.relative_to(LIB)).replace("\\", "/")
        digest = sha256_of(p)
        rec = logged.get(rel)
        rows.append({"path": rel, "sha256": digest,
                     "logged": bool(rec), "match": bool(rec) and rec["sha256"] == digest})
    return {"files": len(rows), "mismatch": [r for r in rows if r["logged"] and not r["match"]],
            "unlogged": [r["path"] for r in rows if not r["logged"]]}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--id")
    ap.add_argument("--category")
    ap.add_argument("--ext", default="pdf")
    ap.add_argument("--topic", default="")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args(argv)
    if args.verify:
        print(json.dumps(verify(), ensure_ascii=False, indent=2))
        return
    if not (args.url and args.id and args.category):
        ap.error("需要 --url --id --category")
    print(json.dumps(fetch(args.url, args.id, args.category, args.ext, args.topic), ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

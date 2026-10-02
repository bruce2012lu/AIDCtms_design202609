"""Google Patents 公开页解析（只读抓取，输出 JSON）。

用法: python gp_scrape.py out.json NO1 NO2 ...
"""
from __future__ import annotations

import json
import re
import sys
import time

import httpx
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 cp-design-librarian/0.1")


def txt(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)) if el else None


def parse(no: str, client: httpx.Client) -> dict:
    url = f"https://patents.google.com/patent/{no}/en"
    r = client.get(url)
    rec = {"query": no, "url": url, "http": r.status_code}
    if r.status_code != 200:
        return rec
    s = BeautifulSoup(r.text, "html.parser")
    meta = lambda n: (s.find("meta", attrs={"name": n}) or {}).get("content")
    rec["title"] = (meta("DC.title") or "").strip()
    rec["pdf"] = meta("citation_pdf_url")
    rec["pub_no"] = txt(s.find("dd", itemprop="publicationNumber")) or txt(s.find(itemprop="publicationNumber"))
    rec["assignee_original"] = [txt(x) for x in s.find_all("dd", itemprop="assigneeOriginal")]
    rec["assignee_current"] = [txt(x) for x in s.find_all("dd", itemprop="assigneeCurrent")]
    rec["inventors"] = [txt(x) for x in s.find_all("dd", itemprop="inventor")]
    for k in ("priorityDate", "filingDate", "publicationDate"):
        el = s.find("time", itemprop=k)
        rec[k] = txt(el)
    st = s.find(itemprop="legalStatusIfi")
    rec["legal_status"] = txt(st.find(itemprop="status")) if st else None
    rec["expiration"] = None
    for ev in s.find_all(itemprop="events"):
        t = txt(ev.find(itemprop="title")) or ""
        if "expiration" in t.lower() or "Status" in t:
            rec.setdefault("events_status", []).append(f"{txt(ev.find('time'))} {t}")
    rec["events"] = [f"{txt(ev.find('time'))} | {txt(ev.find(itemprop='title'))}"
                     for ev in s.find_all(itemprop="events")][:20]
    ab = s.find("div", class_="abstract") or s.find("section", itemprop="abstract")
    rec["abstract"] = txt(ab)
    claims = s.find("section", itemprop="claims")
    c1 = None
    if claims:
        c1 = claims.find("div", class_="claim") or claims.find(attrs={"num": re.compile("0*1$")})
    rec["claim1"] = txt(c1)[:2500] if c1 else None
    rec["claims_count"] = txt(claims.find(itemprop="count")) if claims else None
    rec["family_pubs"] = sorted({txt(x) for x in s.select("tr[itemprop=docdbFamily] span[itemprop=publicationNumber]")})[:30]
    rec["similar"] = [txt(x) for x in s.select("tr[itemprop=similarDocuments] span[itemprop=publicationNumber]")][:15]
    rec["cited_by"] = [f"{txt(tr.find(itemprop='publicationNumber'))} | {txt(tr.find(itemprop='assigneeOriginal'))} | {txt(tr.find(itemprop='title'))}"
                       for tr in s.select("tr[itemprop=forwardReferencesOrig], tr[itemprop=forwardReferencesFamily]")][:25]
    return rec


def main():
    out_path, nos = sys.argv[1], sys.argv[2:]
    out = []
    with httpx.Client(follow_redirects=True, timeout=60, headers={"User-Agent": UA}) as c:
        for no in nos:
            try:
                out.append(parse(no, c))
            except Exception as e:  # noqa: BLE001
                out.append({"query": no, "error": repr(e)})
            time.sleep(1.0)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    sys.stdout.reconfigure(encoding="utf-8")
    for x in out:
        print(x["query"], x.get("http"), x.get("pub_no"), "|", x.get("title"), "|",
              x.get("assignee_original"), x.get("assignee_current"), "|", x.get("priorityDate"),
              "|", x.get("legal_status"), "| pdf", bool(x.get("pdf")), "c1", bool(x.get("claim1")), x.get("error", ""))


if __name__ == "__main__":
    main()

"""Crossref 书目检索 + Unpaywall OA 查询（papers-jet 检索辅助，仅读网络，输出 JSON）。"""
import json
import sys
import httpx

sys.stdout.reconfigure(encoding="utf-8")
H = {"User-Agent": "cp-design-librarian/0.1 (mailto:kb@example.com)"}
C = httpx.Client(timeout=40, headers=H, follow_redirects=True)


def crossref(q, rows=3):
    r = C.get("https://api.crossref.org/works", params={"query.bibliographic": q, "rows": rows})
    out = []
    for it in r.json()["message"]["items"]:
        out.append({
            "doi": it.get("DOI"),
            "title": (it.get("title") or [""])[0],
            "authors": [f"{a.get('given','')} {a.get('family','')}".strip() for a in it.get("author", [])],
            "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "venue": (it.get("container-title") or [""])[0],
            "vol": it.get("volume"), "issue": it.get("issue"), "page": it.get("page"),
        })
    return out


def unpaywall(doi):
    """OpenAlex 的 OA 定位（数据源含 Unpaywall）；Unpaywall API 要求真实邮箱故不直接调用。"""
    try:
        r = C.get(f"https://api.openalex.org/works/https://doi.org/{doi}")
        if r.status_code != 200:
            return {"err": r.status_code}
        j = r.json()
        locs = [{"url": l.get("pdf_url") or l.get("landing_page_url"), "oa": l.get("is_oa"),
                 "ver": l.get("version"), "lic": l.get("license"),
                 "src": (l.get("source") or {}).get("display_name")}
                for l in (j.get("locations") or []) if l.get("is_oa")]
        return {"is_oa": j.get("open_access", {}).get("is_oa"), "cited": j.get("cited_by_count"), "locs": locs}
    except Exception as e:  # noqa: BLE001
        return {"err": str(e)}


if __name__ == "__main__":
    mode = sys.argv[1]
    for arg in sys.argv[2:]:
        if mode == "q":
            res = crossref(arg)
            for x in res:
                x["oa"] = unpaywall(x["doi"]) if x["doi"] else None
            print(json.dumps({"q": arg, "res": res}, ensure_ascii=False))
        else:
            print(json.dumps({"doi": arg, "oa": unpaywall(arg)}, ensure_ascii=False))

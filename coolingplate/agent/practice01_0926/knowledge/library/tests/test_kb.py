"""kb.py 单元测试。全部在临时目录里跑，不碰真实知识库。

运行：python -m pytest knowledge/library/tests -q
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import date
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
LIB_REAL = HERE.parent
sys.path.insert(0, str(LIB_REAL / "tools"))
import kb  # noqa: E402


def _make_pdf(path: Path) -> None:
    import fitz
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((72, 72), "Confined submerged jet impingement at low Reynolds number.", fontsize=11)
    p1.insert_text((72, 100), "Nu = 1.427 Re^0.5 Pr^0.4 valid for 500 < Re < 2000.", fontsize=11)
    p1.insert_text((72, 128), "微射流冲击冷板 丙二醇水溶液", fontsize=11, fontname="china-s")
    p2 = doc.new_page()
    x0, y0, w, h = 72, 100, 120, 24
    rows = [["Re", "Nu"], ["500", "21.3"], ["1000", "30.2"]]
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            rect = fitz.Rect(x0 + c * w, y0 + r * h, x0 + (c + 1) * w, y0 + (r + 1) * h)
            p2.draw_rect(rect, color=(0, 0, 0), width=0.8)
            p2.insert_text((rect.x0 + 4, rect.y0 + 16), val, fontsize=10)
    p2.insert_text((72, 90), "Table 1 Measured Nusselt numbers", fontsize=10)
    doc.save(path)
    doc.close()


@pytest.fixture()
def lib(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "platform").mkdir(parents=True)
    (root / "agents").mkdir()
    lib = root / "agents" / "kb"
    (lib / "schema").mkdir(parents=True)
    shutil.copy(LIB_REAL / "schema" / "entry.schema.json", lib / "schema" / "entry.schema.json")
    pdf = lib / "files" / "papers" / "pap-2001-test-jet.pdf"
    pdf.parent.mkdir(parents=True)
    _make_pdf(pdf)
    staging = lib / "_staging" / "t"
    staging.mkdir(parents=True)
    entries = [
        {"id": "pap-2001-test-jet", "type": "paper", "title": "Test jet paper", "year": 2001,
         "url": "https://example.org/a", "trust_level": "L2", "stages": [3, 4],
         "access": {"status": "downloaded", "redistributable": False},
         "file": {"path": "files/papers/pap-2001-test-jet.pdf", "sha256": kb.sha256_of(pdf)},
         "benchmark_candidate": True, "last_verified": "2026-10-02", "valid_until": "2030-01-01"},
        {"id": "int-2026-test-report", "type": "internal", "title": "内部报告", "year": 2026,
         "url": "repo:x", "trust_level": "L5", "stages": [4],
         "access": {"status": "metadata_only"}, "summary_zh": "射流雷诺数 478 低于关联式下限",
         "last_verified": "2026-10-02"},
        {"id": "BAD id", "type": "paper", "title": "x", "year": 1, "url": "u", "trust_level": "L2",
         "stages": [1], "access": {"status": "downloaded"}, "last_verified": "2026-10-02"},
    ]
    (staging / "entries.json").write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
    return lib


def test_merge_validates_and_writes(lib: Path) -> None:
    res = kb.merge(lib, write=True)
    assert res["total"] == 2
    assert {"pap-2001-test-jet", "int-2026-test-report"} == set(res["added"])
    assert res["invalid"] and res["invalid"][0]["id"] == "BAD id"
    again = kb.merge(lib, write=True)
    assert again["added"] == [] and len(again["skipped_existing"]) == 2


def test_ingest_extracts_text_table_and_is_incremental(lib: Path) -> None:
    kb.merge(lib, write=True)
    res = kb.ingest(lib)
    assert len(res["ingested"]) == 1 and not res["failed"]
    d = lib / "derived" / "pap-2001-test-jet"
    pages = [json.loads(x) for x in (d / "pages.jsonl").read_text(encoding="utf-8").splitlines()]
    assert pages[0]["page"] == 1 and "Reynolds" in pages[0]["text"]
    tables = json.loads((d / "tables.json").read_text(encoding="utf-8"))
    assert tables, "应识别出第 2 页的表格"
    csv_text = (d / tables[0]["file"]).read_text(encoding="utf-8-sig")
    assert "21.3" in csv_text and tables[0]["page"] == 2
    assert kb.ingest(lib)["unchanged"] == ["pap-2001-test-jet"]


def test_ingest_rejects_tampered_file(lib: Path) -> None:
    kb.merge(lib, write=True)
    pdf = lib / "files" / "papers" / "pap-2001-test-jet.pdf"
    pdf.write_bytes(pdf.read_bytes() + b"\n%tamper")
    res = kb.ingest(lib)
    assert res["failed"] and "sha256" in res["failed"][0]["reason"]
    assert kb.verify(lib)["sha_mismatch"] == ["pap-2001-test-jet"]


def test_search_english_chinese_short_terms_and_filters(lib: Path) -> None:
    kb.merge(lib, write=True)
    kb.ingest(lib)
    kb.index(lib)
    hits = kb.search(lib, "Reynolds impingement")
    assert hits and hits[0]["id"] == "pap-2001-test-jet" and hits[0]["page"] == 1
    zh = kb.search(lib, "丙二醇水溶液")
    assert any(h["id"] == "pap-2001-test-jet" for h in zh)
    meta = kb.search(lib, "雷诺数")
    assert any(h["id"] == "int-2026-test-report" and h["source"] == "metadata" for h in meta)
    assert all(h["trust_level"] == "L2" for h in kb.search(lib, "Reynolds", trust=["L2"]))
    assert kb.search(lib, "Reynolds", trust=["L1"]) == []
    assert kb.search(lib, "雷诺数", stage=3) == []
    reranked = kb.search(lib, "jet impingement Reynolds", rerank=True)
    assert reranked and 0 <= reranked[0]["score"] <= 1.0001


def test_cite_gates(lib: Path) -> None:
    kb.merge(lib, write=True)
    rec = kb.cite(lib, "pap-2001-test-jet", "Table 1 p.2", "Nu", "21.3", used_in="test", role="benchmark")
    assert rec["cid"] == "cit-0001"
    with pytest.raises(SystemExit):
        kb.cite(lib, "pap-0000-none", "p.1", "x", "1")
    with pytest.raises(SystemExit):
        kb.cite(lib, "pap-2001-test-jet", "  ", "x", "1")
    with pytest.raises(SystemExit):
        kb.cite(lib, "int-2026-test-report", "§3", "Re", "478", role="benchmark")
    assert kb.cite(lib, "int-2026-test-report", "§3", "Re", "478", role="value")["trust_level"] == "L5"


def test_verify_flags_expiry_and_dangling(lib: Path) -> None:
    kb.merge(lib, write=True)
    (lib / "registry" / "benchmarks.json").write_text(json.dumps([
        {"bid": "BM-X", "sources": [{"entry_id": "pap-9999-ghost"}]}]), encoding="utf-8")
    res = kb.verify(lib, today=date(2031, 1, 1))
    assert "pap-2001-test-jet" in res["expired"]
    assert res["dangling_benchmarks"] == ["BM-X→pap-9999-ghost"]
    assert res["ok"] is False


def test_figures_deduplicated_and_jpeg(tmp_path: Path) -> None:
    import fitz
    pdf = tmp_path / "img.pdf"
    doc = fitz.open()
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 2400, 300), 0)
    pix.clear_with(200)
    p1 = doc.new_page()
    xref = p1.insert_image(fitz.Rect(50, 50, 450, 100), pixmap=pix)
    p1.insert_text((50, 130), "Fig. 1 Test strip", fontsize=10)
    p2 = doc.new_page()
    p2.insert_image(fitz.Rect(50, 50, 450, 100), xref=xref)
    doc.save(pdf)
    doc.close()
    stats = kb.ingest_pdf(pdf, tmp_path / "out", tables=False)
    figs = json.loads((tmp_path / "out" / "figures.json").read_text(encoding="utf-8"))
    assert stats["figures"] == 1 and figs[0]["page"] == 1
    assert figs[0]["captions_on_page"] and figs[0]["captions_on_page"][0].startswith("Fig. 1")
    from PIL import Image
    with Image.open(tmp_path / "out" / figs[0]["file"]) as im:
        assert im.format == "JPEG" and max(im.size) <= kb.MAX_FIG_PX


def test_long_unbroken_text_is_split() -> None:
    text = "\n".join(f"第{i}行 射流孔速与雷诺数" * 5 for i in range(400))
    chunks = kb._chunks([(1, text)])
    assert len(chunks) > 10
    assert max(len(c["text"]) for c in chunks) <= kb.CHUNK_CHARS + kb.OVERLAP + 1


def test_repo_prefix_resolves(lib: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert kb.resolve(lib, "repo:agents/kb/x.pdf") == (lib / "x.pdf").resolve()
    monkeypatch.chdir(lib)
    assert kb.resolve(Path("."), "repo:agents/kb/x.pdf") == (lib / "x.pdf").resolve()

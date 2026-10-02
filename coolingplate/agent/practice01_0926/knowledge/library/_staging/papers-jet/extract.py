"""用 PyMuPDF 把 files/papers 下本主题 PDF 抽成带页码标记的 txt（写入 _staging/papers-jet/txt/）。"""
import sys
from pathlib import Path
import fitz

sys.stdout.reconfigure(encoding="utf-8")
LIB = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "txt"
OUT.mkdir(exist_ok=True)
for pid in sys.argv[1:]:
    pdf = LIB / "files" / "papers" / f"{pid}.pdf"
    with fitz.open(pdf) as doc:
        parts = [f"\n===== p.{i + 1} =====\n{p.get_text()}" for i, p in enumerate(doc)]
    (OUT / f"{pid}.txt").write_text("".join(parts), encoding="utf-8")
    print(pid, len(parts), "pages", sum(len(x) for x in parts), "chars")

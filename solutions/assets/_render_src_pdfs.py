# -*- coding: utf-8 -*-
import os, glob, fitz

root = r"d:\agents2026\agents2026\agents\AIDCtms\solutions"
out_root = os.path.join(root, "assets", "src_pdf_pages")
os.makedirs(os.path.join(out_root, "ai_ready"), exist_ok=True)
os.makedirs(os.path.join(out_root, "coolchip"), exist_ok=True)

for p in glob.glob(os.path.join(root, "*.pdf")):
    name = os.path.basename(p)
    if "CoolChip" in name or "Vertiv" in name or name.endswith("20250808.pdf"):
        dest, tag = os.path.join(out_root, "coolchip"), "coolchip"
    elif "AI ready" in name or "0808.pdf" in name or "How to get" in name:
        dest, tag = os.path.join(out_root, "ai_ready"), "ai_ready"
    else:
        print("skip", name)
        continue
    doc = fitz.open(p)
    print(f"{tag}: {len(doc)} pages  {name}")
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4), alpha=False)
        fp = os.path.join(dest, f"{tag}_p{i:02d}.png")
        pix.save(fp)
        print(f"  p{i:02d} {pix.width}x{pix.height} {os.path.getsize(fp)}")
    doc.close()

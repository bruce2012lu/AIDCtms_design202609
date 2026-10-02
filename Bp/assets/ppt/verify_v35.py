# -*- coding: utf-8 -*-
"""
v3.5 演示版 —— 精简校验（结构 / 嵌入 / 越界 / 18 组关键数字 / 术语扫描）
运行： python verify_v35.py
不检查 HTML（本轮不修改任何 HTML）。
"""
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
BP_DIR = os.path.dirname(os.path.dirname(HERE))
PPTX = os.path.join(BP_DIR, "算力冷却商业调研报告_v3.5_演示版_20260906.pptx")
RP = os.path.join(BP_DIR, "算力冷却商业调研报告_v3.5_20260906.html")
BP = os.path.join(BP_DIR, "算力冷却系统新业务BP_v2.2_20260906.html")

errors, warnings, oks = [], [], []


def err(m):
    errors.append(m)


def warn(m):
    warnings.append(m)


def ok(m):
    oks.append(m)


# 用户指定的 18 组交叉数字（须同时出现在 PPT 与 v3.5 / BP v2.2）
KEY18 = [
    ("10.36%", ["10.36%"]),
    ("684.75", ["684.75"]),
    ("715", ["715"]),
    ("840 元/kW", ["840"]),
    ("27%–37%", ["27%–37%"]),
    ("10.36%–23.83%", ["10.36%–23.83%"]),
    ("91 万元/MW", ["91 万元/MW"]),
    ("171 万", ["171"]),
    ("49:1", ["49"]),
    ("245 万", ["245"]),
    ("800 万上限", ["800"]),
    ("1,200 万", ["1,200"]),
    ("1,500 万", ["1,500"]),
    ("2027 启动", ["2027"]),
    ("1.76–2.52 倍", ["1.76–2.52"]),
    ("6–8 周", ["6–8 周"]),
    ("< 5 万元", ["5 万元"]),
    ("50–200 kW", ["50–200"]),
]


def check_pptx():
    if not os.path.exists(PPTX):
        err(f"[PPTX] 尚未生成：{PPTX}")
        return None
    from pptx import Presentation
    from pptx.util import Emu
    from lxml import etree

    prs = Presentation(PPTX)
    n = len(prs.slides._sldIdLst)
    if n != 43:
        warn(f"[PPTX] 页数为 {n}，预期 43（v3.3 的 39 + 6 张 3A − 2 张被替换的旧工程页）")
    else:
        ok(f"[PPTX] 可正常打开，共 {n} 页")

    sw, sh = prs.slide_width, prs.slide_height
    ratio = sw / sh
    if abs(ratio - 16 / 9) > 0.01:
        err(f"[PPTX] 比例 {ratio:.4f} 不是 16:9")
    else:
        ok(f"[PPTX] 页面比例 {sw/914400:.4f} × {sh/914400:.4f} in = 16:9")

    texts = []
    imgs = 0
    external = 0
    overflow = []
    bad_font = set()
    NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

    for i, sl in enumerate(prs.slides, 1):
        # 外链图片：r:link 而非 r:embed
        xml = sl._element
        for blip in xml.findall(".//a:blip", NS):
            if blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}link"):
                external += 1
            if blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"):
                imgs += 1
        for shp in sl.shapes:
            try:
                l, t, w, h = shp.left, shp.top, shp.width, shp.height
            except Exception:
                continue
            if None in (l, t, w, h):
                continue
            if l < Emu(-9525) or t < Emu(-9525) or l + w > sw + Emu(9525) \
               or t + h > sh + Emu(9525):
                overflow.append((i, shp.name, l / 914400, t / 914400,
                                 w / 914400, h / 914400))
            if shp.has_text_frame:
                for p in shp.text_frame.paragraphs:
                    for r in p.runs:
                        texts.append(r.text)
                        if r.font.name and r.font.name != "Microsoft YaHei":
                            bad_font.add(r.font.name)
            if shp.has_table:
                for row in shp.table.rows:
                    for cell in row.cells:
                        for p in cell.text_frame.paragraphs:
                            for r in p.runs:
                                texts.append(r.text)
                                if r.font.name and r.font.name != "Microsoft YaHei":
                                    bad_font.add(r.font.name)

    body = "\n".join(texts)
    if "\ufffd" in body:
        err("[PPTX] 疑似中文乱码")
    else:
        ok("[PPTX] 中文无乱码")
    if bad_font:
        warn(f"[PPTX] 出现非 Microsoft YaHei 字体：{sorted(bad_font)}")
    else:
        ok("[PPTX] 全部文本字体为 Microsoft YaHei")
    if overflow:
        for o in overflow:
            err("[PPTX] 第 %d 页形状出框：%s  L%.2f T%.2f W%.2f H%.2f"
                % (o[0], o[1], o[2], o[3], o[4], o[5]))
    else:
        ok("[PPTX] 无形状越出页面边界")
    if external:
        err(f"[PPTX] 存在 {external} 张外链图片")
    else:
        ok(f"[PPTX] 图片全部 r:embed 内嵌（检测到 {imgs} 个 blip）")

    with zipfile.ZipFile(PPTX) as z:
        media = [n for n in z.namelist() if n.startswith("ppt/media/")]
        # 确认无外部目标
        bad_rels = []
        for name in z.namelist():
            if name.endswith(".rels"):
                raw = z.read(name).decode("utf-8", errors="replace")
                if 'TargetMode="External"' in raw and "ppt/slides/" in name:
                    bad_rels.append(name)
        if bad_rels:
            err(f"[PPTX] 幻灯片关系含外链：{bad_rels}")
        else:
            ok("[PPTX] 幻灯片关系无 TargetMode=External")
    ok(f"[PPTX] 打包媒体文件 {len(media)} 个")

    # 版本
    if "v3.5 Integrated" not in body:
        err("[PPTX] 正文未出现版本标识 v3.5 Integrated")
    else:
        ok("[PPTX] 版本标识 v3.5 Integrated 已写入")
    if "v3.3 Evidence-led" in body and "v3.5" not in body:
        err("[PPTX] 仍残留 v3.3 作为唯一版本")

    return body, n


def term_scan(body):
    # PCB 冷板：允许出现在术语纪律句中，禁止作为产品名单独推销
    hits = [m.start() for m in re.finditer("PCB 冷板", body)]
    ok_ctx = 0
    bad_ctx = []
    for pos in hits:
        ctx = body[max(0, pos - 40):pos + 50]
        if "仅在" in ctx or "不称" in ctx or "误称" in ctx or "禁止" in ctx:
            ok_ctx += 1
        else:
            bad_ctx.append(ctx.replace("\n", " "))
    if bad_ctx:
        err("[术语] 「PCB 冷板」出现在非纪律语境：" + " | ".join(bad_ctx[:3]))
    else:
        ok(f"[术语] 「PCB 冷板」仅出现在术语纪律句（{ok_ctx} 处）")

    # 统一认证：必须是否定句
    for m in re.finditer("统一.{0,8}认证", body):
        ctx = body[max(0, m.start() - 24):m.end() + 12]
        if not any(k in ctx for k in ("不存在", "无", "不是", "未", "没有")):
            err(f"[术语] 「统一认证」疑似肯定表述：{ctx!r}")
            break
    else:
        ok("[术语] 「统一认证」均为否定/不存在表述")

    banned = [
        (r"市场份额\s*\d", "市场份额点值"),
        (r"部件.{0,6}占比\s*\d", "部件占比点值"),
        (r"通用毛利率\s*\d", "通用毛利率点值"),
        (r"CDU\s*ASP\s*[:：=]\s*\d", "CDU 静态 ASP 点值"),
        (r"SAM.{0,12}\d+\.?\d*\s*亿", "SAM 亿元点值"),
        (r"MTBF\s*[=＝]\s*\d", "MTBF 点值"),
    ]
    found = []
    for pat, lab in banned:
        if re.search(pat, body):
            found.append(lab)
    # 「零外漏 / 100% 拦截」只允许出现在「不予恢复 / 不表述 / 不等于」纪律句
    for term in ("零外漏", "100% 拦截"):
        for m in re.finditer(re.escape(term), body):
            ctx = body[max(0, m.start() - 80):m.end() + 16]
            if not any(k in ctx for k in ("不予恢复", "不表述", "不等于", "禁止", "已删除")):
                found.append(term)
                break
    if found:
        err("[术语] 检出已撤销伪精确：" + "、".join(found))
    else:
        ok("[术语] 未检出已撤销份额 / ASP / 专利墙 / MTBF / 零外漏点值")


def cross_check(body):
    rp = open(RP, encoding="utf-8").read() if os.path.exists(RP) else ""
    bp = open(BP, encoding="utf-8").read() if os.path.exists(BP) else ""
    for label, toks in KEY18:
        miss = []
        for name, doc in (("PPT", body), ("报告 v3.5", rp), ("BP v2.2", bp)):
            for t in toks:
                if t not in doc:
                    miss.append(f"{name} 缺 {t!r}")
        if miss:
            err(f"[交叉] {label}：{'；'.join(miss)}")
        else:
            ok(f"[交叉] {label}")


def main():
    print("=" * 78)
    out = check_pptx()
    if out is None:
        print("PPTX 不存在，中止。")
        sys.exit(1)
    body, n = out
    term_scan(body)
    cross_check(body)

    print("\n---- OK（%d）----" % len(oks))
    for m in oks:
        print("  OK  ", m)
    if warnings:
        print("\n---- WARN（%d）----" % len(warnings))
        for m in warnings:
            print("  WARN", m)
    if errors:
        print("\n---- ERROR（%d）----" % len(errors))
        for m in errors:
            print("  ERR ", m)
        sys.exit(1)
    print("\n全部检查通过。页数 =", n)


if __name__ == "__main__":
    main()

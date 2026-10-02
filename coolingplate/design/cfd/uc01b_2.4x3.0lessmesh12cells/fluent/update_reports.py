"""Point the 12-cell results reports at one-variable Fluent pictures and embed the png bytes."""
import base64
import os
import re

from PIL import Image, ImageDraw, ImageFont

import build_report_jou as b
import make_capture_jou as m

ROOT = m.ROOT
FONT = r"C:\Windows\Fonts\msyh.ttc"
REPORTS = [
    "UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_300step.html",
    "UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_600step.html",
]
FIG = re.compile(
    r'<figure><img src="figs12cells/(i300|i600)/([^"]+\.png)" alt=""><figcaption>(.*?)</figcaption></figure>',
    re.S,
)
OLD_SCALE = "每张温度图的流体和固体共用一把色标，固定为 313–343 K，本面实际范围写在图注里。速度是另一幅，用本面 0 到最大。"
NEW_SCALE = "每张云图单独成文件，图片嵌在本页里。色标是该切面、该变量自己的范围，不锁定 313–343 K。温度和速度分开。壁面按面值着色。"
OLD_FACE = "切面只取一个网格站，按这个面上的四边形着色，节点取相邻面的平均，不再把不相邻的格子连成新的三角网。"
NEW_FACE = "切面按节点插值，颜色连续。"


def clean_caption(text, field):
    text = text.replace("温度色标与全场相同，固定 313–343 K。", "色标为该面自己的温度范围。")
    for phrase in (
        "左图温度，右图速度。",
        "左图流体与固体共用一把温度色标，右图是速度。",
        "左图流体与固体共用温度色标。",
    ):
        text = text.replace(phrase, "")
    if field == "temperature":
        text = re.sub(r"[； ]*\|V\|max [^。]*。?", "", text)
    else:
        loc = text.split("。")[0] + "。"
        found = re.search(r"\|V\|max [^。；]+", text)
        vel = (found.group(0) + "。") if found else ""
        text = loc + "速度色标为该面自己的范围。" + vel
    return re.sub(r"\s+", " ", text).strip()


def figure(step, stem, field, caption):
    name = m.picture_name(stem, field)
    src = "figs12cells/%s/%s" % (step, name)
    return '<figure><img src="%s" alt=""><figcaption>%s</figcaption></figure>' % (
        src,
        clean_caption(caption, field),
    )


def retarget(html):
    def repl(match):
        step, filename, caption = match.group(1), match.group(2), match.group(3)
        stem = filename[:-4]
        if m.base_of(stem) not in m.SPEC:
            return match.group(0)
        fields = ["temperature"]
        if m.needs_v(stem):
            fields.append("velocity-magnitude")
        return "\n".join(figure(step, stem, field, caption) for field in fields)

    html = FIG.sub(repl, html)
    return html.replace(OLD_SCALE, NEW_SCALE)


def embed_images(html):
    """Put each png inside the html. External src= paths are links and break when the file name changes."""
    missing = []

    def repl(match):
        src = match.group(1)
        if src.startswith("data:"):
            return match.group(0)
        path = os.path.join(ROOT, src.replace("/", os.sep))
        if not os.path.isfile(path):
            missing.append(src)
            return match.group(0)
        data = base64.b64encode(open(path, "rb").read()).decode("ascii")
        return '<img src="data:image/png;base64,%s"' % data

    html = re.sub(r'<img src="([^"]+)"', repl, html)
    return html, missing


def write_report(name, smooth_note):
    path = os.path.join(ROOT, name)
    text = open(path, encoding="utf-8").read()
    updated = retarget(text)
    if smooth_note:
        updated = updated.replace(OLD_FACE, NEW_FACE)
    updated, missing = embed_images(updated)
    if missing:
        raise SystemExit("missing pictures: " + ", ".join(missing[:12]))
    if "data:image/png;base64," not in updated:
        raise SystemExit("no embedded pictures in " + name)
    open(path, "w", encoding="utf-8", newline="\n").write(updated)
    print("updated", name, "bytes", os.path.getsize(path), "images", updated.count("data:image/png;base64,"))


def title_image(path, stem, field):
    image = Image.open(path).convert("RGB")
    band_h = 64
    canvas = Image.new("RGB", (image.width, image.height + band_h), "white")
    canvas.paste(image, (0, band_h))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(FONT, 32)
    label = "%s  %s" % (b.place_text(stem), b.var_text(field))
    draw.text((24, 14), label, fill=(20, 20, 20), font=font)
    canvas.save(path)


def title_step(step):
    folder = os.path.join(ROOT, "figs12cells", step)
    stems = m.html_stems()
    done = 0
    missing = []
    for stem in stems:
        fields = ["temperature"]
        if m.needs_v(stem):
            fields.append("velocity-magnitude")
        for field in fields:
            path = os.path.join(folder, m.picture_name(stem, field))
            if not os.path.exists(path):
                missing.append(os.path.basename(path))
                continue
            title_image(path, stem, field)
            done += 1
    print(step, "titled", done, "missing", len(missing))
    if missing:
        print(" ".join(missing[:12]))
    return missing


def main():
    write_report(REPORTS[1], True)


if __name__ == "__main__":
    main()

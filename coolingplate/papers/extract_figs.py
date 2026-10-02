"""Extract selected paper figures for the survey HTML."""
from pathlib import Path
import fitz
from PIL import Image
import io

OUT = Path("figures")
OUT.mkdir(exist_ok=True)

# (pdf, page_1based, xref_or_None, out_stem, max_w)
# If xref is None, render the full page (for fragmented figures).
JOBS = [
    ("04_ASHRAE_LiquidCooling_Mainstream_WP.pdf", 10, 650, "ashrae_fig1_rth_vs_socket", 1400),
    ("04_ASHRAE_LiquidCooling_Mainstream_WP.pdf", 11, 648, "ashrae_fig2_cooling_difficulty", 1400),
    ("04_ASHRAE_LiquidCooling_Mainstream_WP.pdf", 17, 636, "ashrae_fig4_air_vs_liquid", 1400),
    ("01_MDPI_2021_Hussain_JetImpingement_Review.pdf", 3, 58, "hussain_fig1_jet_regions", 1400),
    ("01_MDPI_2021_Hussain_JetImpingement_Review.pdf", 6, 74, "hussain_fig2_jet_model", 900),
    ("01_MDPI_2021_Hussain_JetImpingement_Review.pdf", 14, 232, "hussain_fig7_HD", 1400),
    ("02_MDPI_2024_SSH_JetImpingement_Review.pdf", 5, None, "ssh_p5_nozzle_shapes", 1400),
    ("02_MDPI_2024_SSH_JetImpingement_Review.pdf", 8, 198, "ssh_fig3_chevron", 1200),
    ("05_ElementSix_Diamond_HeatSpreader_CaseStudy.pdf", 2, 3, "e6_fig1_k_compare", 1200),
    ("05_ElementSix_Diamond_HeatSpreader_CaseStudy.pdf", 3, 17, "e6_fig3_hotspot_vs_power", 1200),
    ("05_ElementSix_Diamond_HeatSpreader_CaseStudy.pdf", 3, 18, "e6_fig4_ir", 1100),
    ("08_arXiv_2604.10941_GenerativeDesign_D2C.pdf", 2, 86, "gb200_fig1_layout_heatflux", 1600),
    ("08_arXiv_2604.10941_GenerativeDesign_D2C.pdf", 4, 90, "gb200_fig2_generative", 1400),
    ("09_arXiv_2608.22787_Generative_2p5D3D.pdf", 18, 524, "gen25d_fig4_temp", 1600),
    ("10_arXiv_2605.20657_CoolingChannel_Multichip.pdf", 3, 265, "multichip_fig1_power", 1400),
    ("10_arXiv_2605.20657_CoolingChannel_Multichip.pdf", 5, 269, "multichip_fig4_opt", 1600),
    ("13_MDPI_2026_ChipLevel_ThermalMgmt_Review.pdf", 8, 300, "chip_fig2_25d3d", 1200),
    ("13_MDPI_2026_ChipLevel_ThermalMgmt_Review.pdf", 11, 346, "chip_fig5_gpu_air_liquid", 1300),
    ("13_MDPI_2026_ChipLevel_ThermalMgmt_Review.pdf", 13, 381, "chip_fig6_embedded_mc", 1100),
    ("13_MDPI_2026_ChipLevel_ThermalMgmt_Review.pdf", 14, 424, "chip_fig8_mmchs", 1300),
    ("13_MDPI_2026_ChipLevel_ThermalMgmt_Review.pdf", 15, 437, "chip_fig9_integrated_mc", 1200),
    ("13_MDPI_2026_ChipLevel_ThermalMgmt_Review.pdf", 15, 460, "chip_fig10_diamond_cu", 1400),
    ("13_MDPI_2026_ChipLevel_ThermalMgmt_Review.pdf", 17, 500, "chip_fig13_mmc", 1200),
    ("13_MDPI_2026_ChipLevel_ThermalMgmt_Review.pdf", 17, 523, "chip_fig14_evolution", 1100),
    ("13_MDPI_2026_ChipLevel_ThermalMgmt_Review.pdf", 22, 615, "chip_fig18_serpentine", 1200),
    ("13_MDPI_2026_ChipLevel_ThermalMgmt_Review.pdf", 23, 631, "chip_fig19_dc_coldplate", 1400),
    ("03_MDPI_2024_Nanofluids_DataCenter_Review.pdf", 2, 111, "nano_fig2_air_liquid", 1300),
    ("03_MDPI_2024_Nanofluids_DataCenter_Review.pdf", 14, 259, "nano_fig5_jet_block", 900),
    ("03_MDPI_2024_Nanofluids_DataCenter_Review.pdf", 22, 479, "nano_fig11_future", 1400),
    ("07_SciOpen_2025_Microchannel_HT_Enhancement.pdf", 2, 2, "sciopen_fig1_cuar", 1100),
    ("07_SciOpen_2025_Microchannel_HT_Enhancement.pdf", 6, 21, "sciopen_fig6_enhance", 1400),
    ("07_SciOpen_2025_Microchannel_HT_Enhancement.pdf", 8, 32, "sciopen_fig8_fmhs", 1400),
    ("14_MDPI_2022_NEPCM_JetImpingement.pdf", 3, 128, "nepcm_fig1_stagnation", 1400),
    ("15_MDPI_2023_MgO_MultiJet_Nanofluid.pdf", 2, 92, "mgo_fig1_nozzle_arr", 1100),
]


def save_pil(im: Image.Image, dest: Path, max_w: int):
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    elif im.mode == "L":
        im = im.convert("RGB")
    if im.width > max_w:
        h = int(im.height * max_w / im.width)
        im = im.resize((max_w, h), Image.Resampling.LANCZOS)
    dest = dest.with_suffix(".jpg")
    im.save(dest, "JPEG", quality=86, optimize=True)
    print(f"  {dest.name:45s} {im.size[0]}x{im.size[1]}  {dest.stat().st_size//1024} KB")
    return dest


def extract_xref(doc, xref):
    raw = doc.extract_image(xref)
    return Image.open(io.BytesIO(raw["image"]))


def render_page(doc, page_idx, zoom=2.0):
    page = doc[page_idx]
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def main():
    for pdf, page, xref, stem, max_w in JOBS:
        path = Path("pdfs") / pdf
        dest = OUT / stem
        print(f"{pdf} p{page} xref={xref}")
        doc = fitz.open(path)
        try:
            if xref is None:
                im = render_page(doc, page - 1, zoom=1.8)
            else:
                try:
                    im = extract_xref(doc, xref)
                except Exception as e:
                    print(f"  xref fail {e}; render page")
                    im = render_page(doc, page - 1, zoom=1.8)
            save_pil(im, dest, max_w)
        finally:
            doc.close()


if __name__ == "__main__":
    main()

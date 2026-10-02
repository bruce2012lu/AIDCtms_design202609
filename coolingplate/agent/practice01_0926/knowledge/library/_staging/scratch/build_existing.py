"""把仓库里已有的 12 份 PDF（除 ASHRAE 白皮书，由 standards 主题登记）和内部报告写成登记条目。"""

import hashlib
import json
import sys
from pathlib import Path

import fitz

sys.stdout.reconfigure(encoding="utf-8")
LIB = Path(__file__).resolve().parents[2]
REPO = LIB.parents[6]
CP = "agents/AIDCtms/coolingplate"
TODAY = "2026-10-02"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def file_block(rel: str) -> dict:
    p = REPO / rel
    blk = {"path": "repo:" + rel, "sha256": sha(p), "bytes": p.stat().st_size, "downloaded_at": "2026-09-07"}
    if p.suffix == ".pdf":
        with fitz.open(p) as d:
            blk["pages"] = d.page_count
    return blk


CCBY = {"status": "downloaded", "license": "CC-BY-4.0（MDPI 开放获取）", "redistributable": True}
ARXIV = {"status": "downloaded", "license": "arXiv 非独占分发许可（版权归作者）", "redistributable": False}

papers = [
    ("pap-2021-hussain-jet-impingement-review", "01_MDPI_2021_Hussain_JetImpingement_Review.pdf",
     "Heat Transfer Augmentation through Different Jet Impingement Techniques: A State-of-the-Art Review",
     ["L. Hussain", "M.M. Khan", "M. Masud", "F. Ahmed", "Z. Rehman", "Ł. Amanowicz", "K. Rajski"],
     2021, "Energies 14(20):6458", {"doi": "10.3390/en14206458"}, "L2", [2, 3, 4],
     ["jet impingement", "review", "H/D", "nozzle geometry"],
     "射流强化换热综述：自由射流/驻点/壁面射流三区、H/D 与 S/D 影响、靶面强化、纳米流体与 PCM。v2.0 报告图 5-3/5-4 的 H/D 窗即引自本文 Fig.1/Fig.7。综述性质，不直接给本项目可复现的基准数据。", CCBY),
    ("pap-2024-xu-special-shaped-hole-jet-review", "02_MDPI_2024_SSH_JetImpingement_Review.pdf",
     "A Review of Flow Field and Heat Transfer Characteristics of Jet Impingement from Special-Shaped Holes",
     ["L. Xu", "N. Hu", "H. Lin", "L. Xi", "Y. Li", "J. Gao"], 2024, "Energies 17(17):4510",
     {"doi": "10.3390/en17174510"}, "L2", [2, 3], ["jet impingement", "nozzle shape", "review"],
     "异形孔（椭圆、十字、旋流、V 形等）射流流场与换热综述，用于孔形选型参考。", CCBY),
    ("pap-2024-sun-nanofluids-datacenter-review", "03_MDPI_2024_Nanofluids_DataCenter_Review.pdf",
     "The Applications and Challenges of Nanofluids as Coolants in Data Centers: A Review",
     ["L. Sun", "J. Geng", "K. Dong", "Q. Sun"], 2024, "Energies 17(13):3151",
     {"doi": "10.3390/en17133151"}, "L2", [2], ["nanofluid", "coolant", "data center"],
     "纳米流体在数据中心的稳定性、污垢、磨损与电导率问题。支持“工质不采用纳米流体、采用 PG25”的选型判断。", CCBY),
    ("ven-0000-elementsix-diamond-heat-spreader", "05_ElementSix_Diamond_HeatSpreader_CaseStudy.pdf",
     "Diamond heat spreaders for high power density semiconductor chips (case study)", [], 0,
     "Element Six 案例", {}, "L4", [2], ["diamond", "heat spreader", "hotspot"],
     "厂商案例：金属化金刚石均热片降低热点温度。营销性质，数值不作基准。",
     {"status": "downloaded", "license": "厂商公开资料，版权保留", "redistributable": False}),
    ("pap-2025-liu-microchannel-enhancement-review", "07_SciOpen_2025_Microchannel_HT_Enhancement.pdf",
     "微通道散热器传热增强研究进展", ["刘雨薇", "陈昌辉", "刘金涛"], 2025,
     "实验技术与管理 42(10)", {"doi": "10.16791/j.cnki.sjg.2025.10.009"}, "L2", [2, 3],
     ["microchannel", "review", "中文"], "中文微通道强化换热综述（结构强化、基材、两相）。v2.0 图 6-2 盖板 + 微通道封合结构引自本文 Fig.8。",
     {"status": "downloaded", "license": "期刊开放获取页面下载，版权归期刊", "redistributable": False}),
    ("pap-2026-liu-generative-design-d2c", "08_arXiv_2604.10941_GenerativeDesign_D2C.pdf",
     "Generative Design for Direct-to-Chip Liquid Cooling for Data Centers", ["Z. Liu"], 2026,
     "IISE Annual Conference 2026 / arXiv", {"arxiv": "2604.10941"}, "L4", [3, 5],
     ["generative design", "D2C", "GB200 power map"],
     "非均匀热图下的冷板流道生成式设计。v2.0 图 2-2 GB200 模组热流分布引自本文 Fig.1。", ARXIV),
    ("pap-2026-acquah-generative-2p5d-3d", "09_arXiv_2608.22787_Generative_2p5D3D.pdf",
     "Generative Design of Liquid-Cooling Channels for Thermal Management of 2.5D and 3D Integrated Advanced Packaging",
     ["M. Acquah", "Z. Liu"], 2026, "arXiv", {"arxiv": "2608.22787"}, "L4", [3, 5],
     ["generative design", "2.5D", "3D packaging"], "2.5D/3D 封装液冷流道生成式设计，2 GPU + 1 CPU 热源布局。", ARXIV),
    ("pap-2026-acquah-cooling-channel-multichip", "10_arXiv_2605.20657_CoolingChannel_Multichip.pdf",
     "Cooling Channel Design Optimization for High Power Multi-Chip Packages", ["M. Acquah", "Z. Liu"], 2026,
     "ASME IDETC/CIE 2026 DETC2026-195024 / arXiv", {"arxiv": "2605.20657"}, "L4", [3, 5],
     ["channel optimization", "multi-chip"], "高功率多芯片封装流道优化：歧管/树状/平行通道对比框架。", ARXIV),
    ("pap-2026-energies-chip-level-thermal-review", "13_MDPI_2026_ChipLevel_ThermalMgmt_Review.pdf",
     "Advanced Chip-Level Thermal Management Technologies for High-Power Integrated Processors: A Review",
     [], 2026, "Energies 19(14):3304", {"doi": "10.3390/en19143304"}, "L2", [2, 3],
     ["chip-level cooling", "embedded microchannel", "review"],
     "高功率处理器芯片级热管理综述：近结冷却、嵌入式微通道、歧管微通道（MMC）、3D 封装。", CCBY),
    ("pap-2022-mohaghegh-nepcm-jet", "14_MDPI_2022_NEPCM_JetImpingement.pdf",
     "Jet Impingement Cooling Enhanced with Nano-Encapsulated PCM",
     ["M.R. Mohaghegh", "S.H. Tasnim", "A.A. Aliabadi", "S. Mahmud"], 2022, "Energies 15(3):1034",
     {"doi": "10.3390/en15031034"}, "L2", [3], ["jet impingement", "NEPCM"], "纳米胶囊 PCM 浆料单射流冲击数值研究，含驻点区物理描述。工质路线不同，仅作机理参考。", CCBY),
    ("pap-2023-tang-mgo-multijet", "15_MDPI_2023_MgO_MultiJet_Nanofluid.pdf",
     "Experimental and Numerical Investigation of Flow Structure and Heat Transfer Behavior of Multiple Jet Impingement Using MgO-Water Nanofluids",
     ["T.L. Tang", "H. Salleh", "M.I. Sadiq", "M.A. Mohd Sabri", "M.I.M. Ahmad", "W.A.W. Ghopa"], 2023,
     "Materials 16(11):3942", {"doi": "10.3390/ma16113942"}, "L2", [3, 5, 7],
     ["multi-jet", "experiment", "CFD validation", "nanofluid"],
     "多孔射流实验 + CFD 对比（含水基线），可作 CFD 方法学参考；几何为毫米级多孔，与本项目尺度不同。", CCBY),
]

internal = [
    ("int-2026-cpdesign-b300-report-v2-0", "references/NVIDIA_B300_微通道冲击换热冷板设计报告_v2.0_20260914new.html",
     "NVIDIA B300 微通道+冲击换热冷板设计报告 v2.0", 2026, "2026-09-14",
     "水基线：DP-A 1100 W / DP-B 1400 W，216 孔 D0.50，Sx×Sy = 3.0×2.4 mm，H = 2.0 mm，整板 2.0 L/min，Re_D = 478，壳–进液 0.0326–0.0366 °C/W，板内 3.5–5.5 kPa（含 3–5 kPa 静压箱估值）。"),
    ("int-2026-cpdesign-b300-report-v2-1-pg25", "references/NVIDIA_B300_微通道冲击换热冷板设计报告_v2.1_PG25_20260929.html",
     "NVIDIA B300 微通道冲击换热冷板设计报告 v2.1 · PG25", 2026, "2026-09-29",
     "PG25 40 °C，1400 W，冷却液温升 6 °C → 模组 3.512 L/min；PG25 物性 ρ 1022、cp 3900、μ 1.15e-3、k 0.452、Pr 9.92（未附手册页码）；孔口 K = 1.8；HBM Nu = max(4, 1.86 Gz^1/3)。"),
    ("int-2026-cpdesign-grace-report-v1-0", "references/NVIDIA_Grace_GB300_冷板详细设计报告_v1.0_20260926.html",
     "NVIDIA Grace GB300 冷板详细设计报告 v1.0", 2026, "2026-09-26", "Grace 300 W（含内存），水 0.55 L/min，平行微通道 48×0.40×1.20 mm。"),
    ("int-2026-cpdesign-grace-report-v1-1-pg25", "references/NVIDIA_Grace_GB300_冷板详细设计报告_v1.1_PG25_20260929.html",
     "NVIDIA Grace GB300 冷板详细设计报告 v1.1 · PG25", 2026, "2026-09-29", "Grace PG25 0.8 L/min 原分配表，6 °C 设计流量 0.753 L/min。"),
    ("int-2026-cpdesign-grace-boundary-ref", "references/参考_GB300_Grace_CPU与液冷边界_20260926.html",
     "参考 · GB300 Grace CPU 与液冷边界", 2026, "2026-09-26", "Lenovo LP2357 摘录：Grace TDP 300 W 含内存，LPDDR5X 480 GB/颗。"),
    ("int-2026-cpdesign-uc01-wall-jet", "references/UC01_壁面射流与三槽流路说明.html",
     "UC01 壁面射流与三槽流路说明", 2026, "2026-09-26", "UC-01 单元胞壁面射流与三槽流路说明。"),
    ("int-2026-cpdesign-tech-survey-v1-3", "references/AI算力芯片液冷冷板技术调查分析报告_v1.3_20260907.html",
     "AI 算力芯片液冷冷板技术调查分析报告 v1.3", 2026, "2026-09-07", "技术调查：射流三区、H/D 与 S/D 设计窗、微通道强化、行业热阻标尺。"),
    ("int-2026-cpdesign-patent-analysis-v1-4", "references/AI算力芯片液冷冷板专利分析报告_v1.4_20260907.html",
     "AI 算力芯片液冷冷板专利分析报告 v1.4", 2026, "2026-09-07", "专利分析：方案 A 权项结构、已公开杂交架构、规避要点。"),
]

entries = []
for (eid, fname, title, authors, year, venue, ident, trust, stages, topics, summary, access) in papers:
    entries.append({
        "id": eid, "type": "paper" if eid.startswith("pap") else "vendor_doc", "title": title,
        "authors": authors, "year": year, "venue": venue, "identifiers": ident,
        "url": f"https://doi.org/{ident['doi']}" if "doi" in ident else (
            f"https://arxiv.org/abs/{ident['arxiv']}" if "arxiv" in ident else "https://www.e6.com/"),
        "language": "zh" if "liu-microchannel" in eid else "en",
        "access": access, "file": file_block(f"{CP}/papers/pdfs/{fname}"),
        "trust_level": trust, "trust_reason": "MDPI/期刊同行评审" if trust == "L2" else "预印本/会议或厂商资料",
        "stages": stages, "topics": topics, "summary_zh": summary, "benchmark_candidate": False,
        "related_internal": ["int-2026-cpdesign-tech-survey-v1-3"], "retrieved_by": "existing-corpus-2026-09-07",
        "last_verified": TODAY, "valid_until": "2028-12-31", "status": "active",
    })
for (eid, rel, title, year, d, summary) in internal:
    entries.append({
        "id": eid, "type": "internal", "title": title, "org": "cp-design 项目组", "year": year,
        "venue": f"内部报告 {d}", "url": "repo:" + f"{CP}/agent/practice01_0926/{rel}", "language": "zh",
        "access": {"status": "downloaded", "license": "内部文件", "redistributable": False,
                   "copyright_note": "内部设计评审文档，非 NVIDIA/Lenovo ICD"},
        "file": {**file_block(f"{CP}/agent/practice01_0926/{rel}"), "downloaded_at": d},
        "trust_level": "L5", "trust_reason": "内部报告/算例，未经外部权威来源全面核对（见 reports/内部数值对照）",
        "stages": [1, 2, 3, 4, 5, 6], "topics": ["internal", "B300" if "b300" in eid else "Grace"],
        "summary_zh": summary, "benchmark_candidate": False, "retrieved_by": "existing-corpus",
        "last_verified": TODAY, "valid_until": "2027-03-31", "status": "active",
    })
out = LIB / "_staging" / "existing" / "entries.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), out)

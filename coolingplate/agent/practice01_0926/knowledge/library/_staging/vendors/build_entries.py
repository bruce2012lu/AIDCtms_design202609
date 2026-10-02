"""生成 _staging/vendors/entries.json：条目元数据在此手工维护，file 块从下载日志按 id 取最新记录自动回填，最后按 schema 校验。

用法: python build_entries.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

sys.stdout.reconfigure(encoding="utf-8")
LIB = Path(__file__).resolve().parents[2]
LOG = LIB / "_staging" / "downloads.log.jsonl"
SCHEMA = LIB / "schema" / "entry.schema.json"
OUT = Path(__file__).with_name("entries.json")
TODAY = "2026-10-02"
BY = "subagent-vendors"
PG25_REPORT = "W/docs/knowledge/PG25物性溯源与推荐_20261002.md"

VENDOR_PUBLIC = {"license": "厂商公开文档（版权保留）", "redistributable": False,
                 "copyright_note": "仅供内部研究引用，不随仓库分发"}


def kd(quantity, value, locator, unit=None, condition=None, vf="fulltext"):
    d = {"quantity": quantity, "value": value, "locator": locator, "verified_from": vf}
    if unit:
        d["unit"] = unit
    if condition:
        d["condition"] = condition
    return d


E: list[dict] = []

# ---------------- NVIDIA ----------------
E.append({
    "id": "ven-2025-nvidia-blackwell-ultra-datasheet", "type": "vendor_doc",
    "title": "NVIDIA Blackwell Ultra Datasheet (GB300 NVL72 / HGX B300)",
    "title_zh": "NVIDIA Blackwell Ultra 产品数据表（GB300 NVL72 / HGX B300）",
    "org": "NVIDIA", "year": 2025, "venue": "NVIDIA datasheet",
    "url": "https://resources.nvidia.com/en-us-blackwell-architecture/blackwell-ultra-datasheet",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "NVIDIA 官方产品数据表（NVIDIA DAM CDN 原件）",
    "stages": [1, 2, 3], "topics": ["vendors", "nvidia", "b300", "gb300", "tdp"],
    "summary_zh": "Blackwell Ultra 官方规格表。第5页技术规格表给出单 GPU 最大 TDP：GB300 NVL72 形态可配置至 1,400 W，HGX B300 形态可配置至 1,100 W——正对应本项目 1400 W 基线 / 1100 W 校核两个工况。无冷却液参数。",
    "key_data": [
        kd("B300 单 GPU 最大 TDP（GB300 NVL72 形态）", "Configurable up to 1,400", "p.5 Technical Specifications 表", "W"),
        kd("B300 单 GPU 最大 TDP（HGX B300 形态）", "Configurable up to 1,100", "p.5 Technical Specifications 表", "W"),
        kd("GB300 NVL72 冷却方式", "fully liquid-cooled, rack-scale", "p.2"),
        kd("单 GPU HBM3E 容量（GB300 / HGX）", "279 / 270", "p.5", "GB"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
    "notes": "与 Lenovo LP2357 中 'NVIDIA SXM B300 DLC TGP 1100W' 不一致：NVIDIA 给的是可配置上限，OEM 可能按 1100 W 出货配置；热设计基线应按 NVIDIA 1400 W 上限。",
})
E.append({
    "id": "ven-2025-nvidia-blackwell-architecture-brief", "type": "vendor_doc",
    "title": "NVIDIA Blackwell Architecture Technical Brief (V2.1, updated for Blackwell Ultra GB300)",
    "title_zh": "NVIDIA Blackwell 架构技术简报 V2.1（含 GB300/HGX B300）",
    "org": "NVIDIA", "year": 2025, "venue": "NVIDIA technical brief",
    "url": "https://resources.nvidia.com/en-us-blackwell-architecture/blackwell-ultra-datasheet",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "NVIDIA 官方技术简报",
    "stages": [1, 2], "topics": ["vendors", "nvidia", "gb300", "gb200", "hgx"],
    "summary_zh": "Blackwell 架构白皮书式简报，含 GB300/GB200 NVL72 系统规格对照（Table 2，第13页）与 HGX B300/B200 规格（第25–26页，HGX B300 TDP 1100 W、B200 1000 W）。冷却仅定性描述（液冷、能效）。",
    "key_data": [
        kd("HGX B300 单 GPU 最大 TDP", 1100, "p.26 HGX 规格表", "W"),
        kd("HGX B200 单 GPU 最大 TDP", 1000, "p.26 HGX 规格表", "W"),
        kd("NVL72 机架构成", "18 compute trays（每盘 4 GPU + 2 Grace）+ 9 NVLink switch trays", "p.13 Table 2"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2025-nvidia-dgx-gb300-datasheet", "type": "vendor_doc",
    "title": "NVIDIA DGX GB300 Datasheet",
    "title_zh": "NVIDIA DGX GB300 数据表",
    "org": "NVIDIA", "year": 2025, "venue": "NVIDIA datasheet (4448275, Oct25)",
    "url": "https://resources.nvidia.com/en-us-dgx-systems/dgx-gb300-datasheet",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "NVIDIA 官方产品数据表",
    "stages": [1, 2], "topics": ["vendors", "nvidia", "dgx", "gb300"],
    "summary_zh": "DGX GB300 整机柜规格（72 Blackwell Ultra + 36 Grace，100% 液冷、MGX 机架）。不含 TDP、冷却液、流量等热设计数据，主要用于确认系统构成。",
    "key_data": [
        kd("冷却方式", "rack-scale, 100% liquid-cooled design", "p.1"),
        kd("GPU / CPU 数量", "72x Blackwell Ultra GPUs, 36x Grace CPUs", "p.3 Technical Specifications"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
    "notes": "'100% liquid-cooled' 是营销口径；同一代产品 SuperPOD RA 与 Lenovo/HPE 文档均写混合冷却（约 90% 液 / 10% 风）。",
})
E.append({
    "id": "ven-2025-nvidia-dgx-gb200-datasheet", "type": "vendor_doc",
    "title": "NVIDIA DGX GB200 Datasheet",
    "title_zh": "NVIDIA DGX GB200 数据表",
    "org": "NVIDIA", "year": 2025, "venue": "NVIDIA datasheet",
    "url": "https://resources.nvidia.com/en-us-dgx-systems/dgx-gb300-datasheet",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "NVIDIA 官方产品数据表",
    "stages": [1, 2], "topics": ["vendors", "nvidia", "dgx", "gb200"],
    "summary_zh": "DGX GB200 整机柜规格，作为 GB300 前代对照。无热设计数值。",
    "key_data": [kd("冷却方式", "liquid-cooled, rack-scale design", "p.1")],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
    "notes": "落地页为 DGX 系列资料中心，PDF 来自 NVIDIA DAM CDN（2025-10 修订版）。",
})
E.append({
    "id": "ven-2025-nvidia-dgx-gb-rack-user-guide", "type": "vendor_doc",
    "title": "NVIDIA DGX GB Rack Scale Systems User Guide (GB200 / GB300)",
    "title_zh": "NVIDIA DGX GB 机架级系统用户指南（GB200/GB300）",
    "org": "NVIDIA", "year": 2025, "venue": "docs.nvidia.com",
    "url": "https://docs.nvidia.com/dgx/dgxgb200-user-guide/",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "NVIDIA 官方用户手册",
    "stages": [1, 2, 8], "topics": ["vendors", "nvidia", "dgx", "gb300", "leak-detection", "manifold"],
    "summary_zh": "DGX GB200/GB300 机架用户手册：计算盘经机架歧管→CPU/GPU 冷板液冷，其余器件风冷；泄漏检测与 Mission Control 健康监测。公开版不含供液温度/流量/压降表。",
    "key_data": [
        kd("机架功耗", "approximately 120", "p.17 Power", "kW"),
        kd("电源架", "8 个电源架，每架 6×5.5 kW PSU，33 kW/架，N+N", "p.17"),
        kd("冷却拓扑", "liquid runs up and down the rack through manifolds, then through cold plates attached to CPUs and GPUs; rest air cooled", "p.9 Compute Tray"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
    "notes": "冷却液规格（温度、流量、水质）NVIDIA 公开文档未给出，需走 NVIDIA 合作伙伴渠道（见 ven-0000-nvidia-gb300-thermal-design-guide）。",
})
E.append({
    "id": "ven-2025-nvidia-dgx-superpod-gb300-ra", "type": "vendor_doc",
    "title": "NVIDIA DGX SuperPOD: Next Generation Scalable Infrastructure for AI Factories (Reference Architecture, DGX GB300)",
    "title_zh": "NVIDIA DGX SuperPOD（DGX GB300）参考架构",
    "org": "NVIDIA", "year": 2025, "venue": "docs.nvidia.com",
    "url": "https://docs.nvidia.com/pdf/dgx-spod-gb300-ra.pdf",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "NVIDIA 官方参考架构",
    "stages": [1, 8], "topics": ["vendors", "nvidia", "superpod", "gb300", "facility"],
    "summary_zh": "SuperPOD GB300 参考架构：以 8 台 DGX GB300 为一个 SU，每 SU 热设计功率 1.2 MW；混合冷却（GPU/CPU 直接液冷，其余风冷）；数据中心设计指导由 NVIDIA 基础设施团队提供（未公开）。",
    "key_data": [
        kd("每 SU（8 机架）TDP", 1.2, "p.5", "MW"),
        kd("冷却方式", "hybrid: direct liquid cooling for GPUs/CPUs, air for other components", "p.5, p.8"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2025-nvidia-nvl72-ai-factory-gb300-ra", "type": "vendor_doc",
    "title": "NVIDIA NVL72 AI Factory with GB300 NVL72 – Dual-Plane Networking Architecture (Enterprise Reference Architecture)",
    "title_zh": "NVIDIA NVL72 AI 工厂企业参考架构（GB300 NVL72）",
    "org": "NVIDIA", "year": 2025, "venue": "docs.nvidia.com Enterprise RA",
    "url": "https://docs.nvidia.com/enterprise-reference-architectures/nvl72-ai-factory/latest/components.html",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "NVIDIA 官方企业参考架构",
    "stages": [1, 8], "topics": ["vendors", "nvidia", "gb300", "rack-power"],
    "summary_zh": "GB300 NVL72 企业参考架构：MGX 液冷机架、盘级与机架级漏液检测、8×33 kW 电源架、满机架最高 142 kW。",
    "key_data": [
        kd("满机架功率需求", "up to 142", "p.8", "kW"),
        kd("漏液检测", "Integrated tray-level and rack-level liquid leakage detection", "p.8"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2026-nvidia-dgx-b300-dc-best-practices", "type": "vendor_doc",
    "title": "Data Center Best Practices with DGX B300 (Version 1.0)",
    "title_zh": "DGX B300 数据中心最佳实践 v1.0",
    "org": "NVIDIA", "year": 2026, "venue": "docs.nvidia.com",
    "url": "https://docs.nvidia.com/dgx-pdf/data-center-best-practices-with-dgx-b300-v1.pdf",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "NVIDIA 官方数据中心部署指南",
    "stages": [1], "topics": ["vendors", "nvidia", "dgx-b300", "air-cooling", "rdhx"],
    "summary_zh": "DGX B300（HGX B300 8 卡，风冷）机房部署：单机 14.5–15 kW，峰值 19–19.7 kW；高密 4 台/柜需主动背板换热器。仅作 1100 W 风冷形态的对照，不含液冷冷板数据。",
    "key_data": [
        kd("单机估算功率（DC 母排 / AC PDU）", "14.5 / 15", "p.7 规格表", "kW", "25 °C 送风"),
        kd("单机峰值功率", "19 / 19.7", "p.7 规格表", "kW"),
        kd("高密机柜（4 台）", "58 kW 平均 / 76 kW 峰值，主动背板换热器", "p.8"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2024-nvidia-ocp-mgx-rack-tray-spec", "type": "vendor_doc",
    "title": "MGX Accelerated Computing Rack and Trays Specification, Revision 1.1",
    "title_zh": "MGX 加速计算机架与托盘规范 Rev 1.1（NVIDIA 贡献给 OCP，GB200/GB300 NVL72 机架基础）",
    "authors": ["NVIDIA"], "org": "NVIDIA / Open Compute Project", "year": 2024,
    "venue": "OCP Server Project contribution（Effective 2024-08-29；Rev 1.1 于 2025-04-23 提交）",
    "url": "https://www.opencompute.org/documents/mgx-accelerated-computing-rack-and-trays-specification-1-1-pdf-1",
    "language": "en",
    "access": {"status": "pending_user", "license": "OCP OWFa1.0 Final Specification Agreement（附录除外）",
               "redistributable": False,
               "how_to_get": "opencompute.org 对脚本返回 403（反爬），请用浏览器打开落地页下载 PDF 后放入 files/vendor_docs/ 并跑 fetch.py --verify 登记；OCP 规范免费公开。"},
    "trust_level": "L3", "trust_reason": "NVIDIA 撰写、OCP 发布的正式规范；§11 为机架液冷需求（整机柜级，非单 GPU）",
    "stages": [1, 2, 3, 4, 6, 8], "topics": ["vendors", "nvidia", "ocp", "mgx", "gb200", "uqd", "wetted-materials"],
    "summary_zh": "GB200/GB300 NVL72 所用 MGX 机架/托盘的公开机械与热规范。§11 给出机架级液冷需求：目标持续流量≤130 LPM、单节点（1 对 UQD）压差约 10 psid、机架 120 kW、液体取热比 85%、最高工作压力 5 bar、最低爆破压力 15 bar、过滤 25/50 µm；§12 给出 PG/水基工质的许用浸润材料清单（铜 CDA110 等、316L、EPDM 过氧化物硫化、BCuP 钎料；禁用铝、锌、铅、非不锈钢等）。§10 为 UQD-04/UQDB-04 盲插浮动机构。",
    "key_data": [
        kd("机架目标持续流量", "up to 130", "§11 Rack and Tray Thermal Requirements", "LPM", "120 kW 机架"),
        kd("单节点压差（1 对 UQD，目标流量下）", "~10", "§11", "psid"),
        kd("机架液体取热比", 85, "§11", "%"),
        kd("最高工作压力（表压）", "5 bar (72 psig)", "§11"),
        kd("最低爆破压力（表压）", "15 bar (217 psig)", "§11"),
        kd("过滤精度", "25 µm and 50 µm", "§11", "µm"),
        kd("许用/禁用浸润材料", "允许 Cu CDA110/CDA1020/CDA1220、黄铜(<15%Zn)、316L 等不锈钢、Ti Gr2、EPDM(过氧化物硫化)、BCuP-2..5 钎料；禁用 Al、Zn、Pb、非不锈钢、PVC/CPVC 等", "§12 Approved Wetted Materials List for PG/water-based fluids"),
        kd("UQD 预紧弹簧", "18–14 lbs @ 35 psi", "§10.1"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
    "notes": "数值通过 WebFetch 读取 opencompute.org 官方 PDF 全文核对（verified_from=fulltext），但本地未存档；待用户手动下载后补 file 块。注意这是 GB200（120 kW）时代的规范值，GB300 需以 OEM/NVIDIA 更新为准。",
})
E.append({
    "id": "ven-2024-nvidia-ocp-gb200-nvl72-blog", "type": "vendor_doc",
    "title": "NVIDIA Contributes NVIDIA GB200 NVL72 Designs to Open Compute Project",
    "title_zh": "NVIDIA 向 OCP 贡献 GB200 NVL72 设计（技术博客）",
    "org": "NVIDIA", "year": 2024, "venue": "NVIDIA Technical Blog",
    "url": "https://developer.nvidia.com/blog/nvidia-contributes-nvidia-gb200-nvl72-designs-to-open-compute-project/",
    "language": "en", "access": {"status": "metadata_only", **VENDOR_PUBLIC},
    "trust_level": "L4", "trust_reason": "厂商技术博客，定性说明为主",
    "stages": [1, 2], "topics": ["vendors", "nvidia", "ocp", "gb200", "manifold"],
    "summary_zh": "说明 GB200 NVL72 向 OCP 贡献的机架/托盘/液冷内容：机架需 120 kW 冷却能力，采用增强型盲插液冷歧管与浮动盲插托盘接口，1RU 液冷计算/交换托盘。指向 MGX 规范全文（ven-2024-nvidia-ocp-mgx-rack-tray-spec）。",
    "key_data": [
        kd("机架冷却能力", 120, "博客正文 'To efficiently manage the 120 KW cooling capacity'", "kW", vf="landing_page"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2025-nvidia-blackwell-ultra-blog", "type": "vendor_doc",
    "title": "Inside NVIDIA Blackwell Ultra: The Chip Powering the AI Factory Era",
    "title_zh": "深入 NVIDIA Blackwell Ultra（技术博客）",
    "org": "NVIDIA", "year": 2025, "venue": "NVIDIA Technical Blog",
    "url": "https://developer.nvidia.com/blog/inside-nvidia-blackwell-ultra-the-chip-powering-the-ai-factory-era/",
    "language": "en", "access": {"status": "metadata_only", **VENDOR_PUBLIC},
    "trust_level": "L4", "trust_reason": "厂商技术博客；数值与官方数据表一致",
    "stages": [1, 2, 3], "topics": ["vendors", "nvidia", "b300", "tgp"],
    "summary_zh": "Hopper/Blackwell/Blackwell Ultra 代际对比表：最大功耗（TGP）分别为 700 W / 1,200 W / 1,400 W；双 die、288 GB HBM3E。",
    "key_data": [
        kd("Max power (TGP)：Hopper / Blackwell / Blackwell Ultra", "700 / 1,200 / 1,400", "博客对比表 'Max power (TGP)' 行", "W", vf="landing_page"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-0000-nvidia-gb300-thermal-design-guide", "type": "vendor_doc",
    "title": "NVIDIA GB300 NVL72 / B300 compute tray thermal & liquid-cooling design guide (partner-only; exact title unverified)",
    "title_zh": "NVIDIA GB300/B300 热设计与液冷设计指南（合作伙伴限定，确切标题未核实）",
    "org": "NVIDIA", "year": 0, "venue": "NVIDIA Partner Portal / NDA",
    "url": "https://www.nvidia.com/en-us/about-nvidia/partners/",
    "language": "en",
    "access": {"status": "login_required", "redistributable": False,
               "how_to_get": "通过 NVIDIA NPN 合作伙伴门户或 OEM/ODM（如 Lenovo、HPE、Supermicro、Foxconn/Quanta）在 NDA 下获取 GB300 Thermal Design Guide / MGX 液冷设计文档；也可向 NVIDIA Infrastructure Specialist 团队申请数据中心设计指导（SuperPOD RA p.8 提及）。"},
    "trust_level": "L3", "trust_reason": "若获得即为芯片厂商一手热设计规范（冷板接口、TIM、热阻目标、流量/压降预算）",
    "stages": [1, 2, 3, 4, 5, 6, 7], "topics": ["vendors", "nvidia", "gb300", "b300", "tdg", "nda"],
    "summary_zh": "公开渠道未找到 GB300/B300 的冷板级热设计数据（每 GPU 冷板流量、允许压降、TCASE/TJ 限值、热阻目标、安装力等）。这些通常只在 NVIDIA 合作伙伴 NDA 文档中。仅登记，待用户获取。",
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY,
    "notes": "year=0000 表示未知；标题为描述性占位，获取后按原文标题更正并改 id。",
})

# ---------------- Lenovo ----------------
E.append({
    "id": "ven-2025-lenovo-gb300-nvl72-product-guide", "type": "vendor_doc",
    "title": "Lenovo NVIDIA GB300 NVL72 Rack Scale AI Product Guide (LP2357)",
    "title_zh": "联想 NVIDIA GB300 NVL72 机架级 AI 产品指南（LP2357）",
    "org": "Lenovo", "year": 2025, "venue": "Lenovo Press LP2357",
    "url": "https://lenovopress.lenovo.com/lp2357-lenovo-nvidia-gb300-nvl72-rack-scale-ai",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "OEM 官方产品指南（Lenovo Press 公开 PDF）",
    "stages": [1, 2, 3, 4, 8], "topics": ["vendors", "lenovo", "gb300", "flow-rate", "pressure-drop", "pg25", "supply-temperature"],
    "summary_zh": "目前能公开拿到的最完整 GB300 NVL72 液冷参数来源。Table 27 给出机架级供液温度–所需流量–机架压降对照（25→45 °C：59→177 LPM，2.3→18.4 psi）；工作水温 2–50 °C（ASHRAE W45）；支持 DI 水（推荐）与 PG25；机架 135 kW TDP、峰值 155 kW，约 90% 液 / 10% 风；歧管 304L/316L、UQDB04、至 CDU 1\" FD83 BSPP、QD 处静压 30 psi；B300 DLC TGP 1100 W、Grace TDP 300 W。",
    "key_data": [
        kd("机架所需流量 @ 供液 25 °C", 59, "p.38 Table 27", "LPM"),
        kd("机架所需流量 @ 30 °C", 71, "p.38 Table 27", "LPM"),
        kd("机架所需流量 @ 35 °C", 89, "p.38 Table 27", "LPM"),
        kd("机架所需流量 @ 40 °C", 119, "p.38 Table 27", "LPM"),
        kd("机架所需流量 @ 45 °C", 177, "p.38 Table 27", "LPM"),
        kd("机架压降 @ 25/30/35/40/45 °C", "2.3 / 3.2 / 4.9 / 8.5 / 18.4", "p.38 Table 27", "psi"),
        kd("工作水温范围", "2–50 °C (ASHRAE W45 compliant)", "p.13 规格表；p.38"),
        kd("允许进水温度", "as high as 45 °C", "p.24 Cooling"),
        kd("工质", "DI water (recommended) 或 PG25", "p.24 Cooling"),
        kd("机架 TDP / 峰值", "135 / 155", "p.2, p.24", "kW"),
        kd("液/风取热比", "≈90% liquid / 10% air", "p.2, p.24"),
        kd("NVIDIA SXM B300 DLC TGP", 1100, "p.19 Table 10", "W"),
        kd("Grace CPU TDP（含内存）", 300, "p.11, p.18", "W"),
        kd("歧管材料 / QD / 至 CDU 接口 / QD 处静压", "304L 或 316L 奥氏体不锈钢 / UQDB04 / 1\" FD83 BSPP / 30 psi", "p.27 Table 18"),
        kd("非运行存放温度（PG25 充注）", "10–70 °C", "p.38"),
    ],
    "benchmark_candidate": False,
    "benchmark_note": "Table 27 是机架级流量–压降规格点，可用于一维机架水力模型趋势校核，但不是冷板实测数据。",
    "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
    "notes": "Table 27 紧随其后有一句 'Standard specifications of the Lenovo GB300 NVL Switch Tray'，排版上表与交换盘说明相邻，但表头明确为 Required Rack Flow / Rack Pressure Drop，按机架级理解。流量随供液温度升高而增大（恒定芯片温度裕量），表未注明工质（DI 或 PG25）——需向 Lenovo 确认。TGP 1100 W 与 NVIDIA 1400 W 上限不一致，见 ven-2025-nvidia-blackwell-ultra-datasheet。",
})
E.append({
    "id": "ven-2025-lenovo-gb300-nvl72-config-guide", "type": "vendor_doc",
    "title": "Lenovo NVIDIA GB300 NVL72 System Configuration Guide",
    "title_zh": "联想 NVIDIA GB300 NVL72 系统配置指南",
    "org": "Lenovo", "year": 2025, "venue": "Lenovo Docs (pubs.lenovo.com)",
    "url": "https://pubs.lenovo.com/gb300-nvl72/server_specifications_environmental",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "OEM 官方配置/维护手册",
    "stages": [1, 3, 4, 8], "topics": ["vendors", "lenovo", "gb300", "flow-rate", "pg25"],
    "summary_zh": "与 LP2357 同源的环境与水力规格（p.15），可交叉核对：同一流量–压降表、W45 2–50 °C、PG25 充注非运行温度 10–70 °C；系统冷却为两条液冷回路 + 8 个 40×56 mm 双转子风扇。",
    "key_data": [
        kd("机架流量 @ 25/30/35/40/45 °C", "59 / 71 / 89 / 119 / 177", "p.15 Water requirements", "LPM"),
        kd("机架压降 @ 25/30/35/40/45 °C", "2.3 / 3.2 / 4.9 / 8.5 / 18.4", "p.15", "psi"),
        kd("工作水温", "2–50 °C (ASHRAE W45)", "p.15"),
        kd("Grace TDP", "up to 300", "p.12", "W"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2024-lenovo-neptune-dwc-standards", "type": "vendor_doc",
    "title": "Lenovo Neptune Direct Water-Cooling Standards (LP2018)",
    "title_zh": "联想 Neptune 直接水冷标准（含水质要求，LP2018）",
    "authors": ["Matthew Ziegler", "Vinod Kamath", "Jerrod Buterbaugh", "Stuart Smith"], "org": "Lenovo", "year": 2024,
    "venue": "Lenovo Press LP2018 (Planning / Implementation)",
    "url": "https://lenovopress.lenovo.com/lp2018-lenovo-neptune-direct-water-cooling-standards",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "OEM 官方水冷实施标准，Lenovo 产品保修依据",
    "stages": [1, 2, 6, 7, 8], "topics": ["vendors", "lenovo", "neptune", "water-quality", "filtration", "materials", "tiers"],
    "summary_zh": "Lenovo 液冷水质与系统标准：金/银/铜三档（FWS 40–45/27–32/17 °C，TCS 45–50/32–37/≤25 °C）；二次侧水须无菌（<100 CFU/mL）、50 µm 在线过滤（≈288 目）、缓蚀+杀菌；浸润材料限铜合金（无铅、<15% Zn）与不锈钢，铜须钎焊、不锈钢 TIG/MIG 焊，禁锡焊与生料带；EPDM 软管（过氧化物硫化）；首选 DI 水，PG25 可用但压降更大；FWS 机械系统最大工作压力常见 10 bar。附 Nalco 加药与季度细菌检测流程。",
    "key_data": [
        kd("冷却分级（金/银/铜）FWS 温度", "40–45 / 27–32 / 17", "p.3 Table 1", "°C"),
        kd("冷却分级 TCS 二次侧温度", "45–50 / 32–37 / ≤25", "p.3 Table 1", "°C"),
        kd("细菌限值", "<100", "p.16 Water Quality；p.23", "CFU/mL"),
        kd("在线过滤精度", "50 µm (≈288 mesh)", "p.16 Water Quality", "µm"),
        kd("去离子后电阻率", ">1 MΩ·cm（排放前 >0.1 MΩ·cm / 电导 <10 mS/cm）", "p.16"),
        kd("唑类缓蚀剂目标浓度", 100, "p.20–24 加药步骤", "ppm"),
        kd("铜合金要求", "lead-free, <15% zinc；铜用钎焊；不锈钢 TIG/MIG 焊、不得钎焊；禁锡焊、禁特氟龙生料带", "p.14–15"),
        kd("FWS 机械系统常见最大工作压力", "10 bar (145 psi)", "p.26"),
        kd("参考方案流量（SD650-N V3 HPC）", "~135 lpm @ 45 °C to DLC", "p.7 Solution 2", "LPM"),
        kd("参考方案流量（Silver, W32）", "~70 lpm/rack @ 36 °C", "p.9", "LPM"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
    "notes": "未给出 pH、电导率的运行限值数字（仅要求'监测并维持'），需配合 Nalco TRASAR 或冷却液厂商规格；Lenovo 其他产品文档的 water_quality_requirement 页面均引用本文。",
})
E.append({
    "id": "ven-2024-lenovo-sc777-v4-product-guide", "type": "vendor_doc",
    "title": "Lenovo ThinkSystem SC777 V4 Neptune Server Product Guide (LP2048, GB200 NVL4)",
    "title_zh": "联想 ThinkSystem SC777 V4 Neptune 服务器产品指南（GB200 NVL4，LP2048）",
    "org": "Lenovo", "year": 2024, "venue": "Lenovo Press LP2048",
    "url": "https://lenovopress.lenovo.com/lp2048-thinksystem-sc777-v4",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "OEM 官方产品指南",
    "stages": [1, 3, 4, 8], "topics": ["vendors", "lenovo", "gb200", "nvl4", "flow-rate", "pressure-drop"],
    "summary_zh": "GB200 NVL4（2 Grace + 4 B200）水冷托盘：B200 TGP 1200 W；给出按 CDU 供水温度（S45/S40/S32/S27）的每托盘流量与机箱压降表（bar，1–8 托盘 × 1–4 PCS），是公开资料中少见的 Blackwell 托盘级流量–温度–压降数据。工作水温 2–45 °C（ASHRAE S45，原 W45）。",
    "key_data": [
        kd("B200 TGP（GB200 NVL4）", 1200, "p.18 Table 5", "W"),
        kd("每托盘流量 @ 45/40/32/27 °C", "7.0 / 6.0 / 4.8 / 4.4", "p.53 Water flow rates", "LPM"),
        kd("N1380 机箱压降（8 托盘 + 4 PCS）@ 45 °C", 0.93, "p.52 Table 27", "bar"),
        kd("N1380 机箱压降（8 托盘 + 4 PCS）@ 40 °C", 0.70, "p.52 Table 28", "bar"),
        kd("工作水温", "2–45 °C (ASHRAE S45, formerly W45)", "p.14"),
        kd("工质与过滤", "treated DI water；<100 CFU/mL；50 µm in-line filter", "p.27, p.52"),
        kd("泄漏检测", "氦质谱检漏 ASTM E499 + 氮气复检", "p.27"),
    ],
    "benchmark_candidate": False,
    "benchmark_note": "托盘级流量–压降表可作一维网络模型的量级校核（含 CPU/GPU/内存/驱动器多支路），非单冷板数据。",
    "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2023-lenovo-sd650-n-v3-product-guide", "type": "vendor_doc",
    "title": "Lenovo ThinkSystem SD650-N V3 Neptune DWC Server Product Guide (LP1834, withdrawn product)",
    "title_zh": "联想 ThinkSystem SD650-N V3 Neptune 水冷服务器产品指南（H100，LP1834）",
    "org": "Lenovo", "year": 2023, "venue": "Lenovo Press LP1834",
    "url": "https://lenovopress.lenovo.com/lp1834-thinksystem-sd650-n-v3-neptune-dwc-server",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "OEM 官方产品指南（已停产产品，参数仍有效）",
    "stages": [1, 3, 4], "topics": ["vendors", "lenovo", "h100", "flow-rate"],
    "summary_zh": "HGX H100 4-GPU 水冷托盘（GPU 700 W）：45 °C 进水 5 lpm/托盘，40 °C 进水 4 lpm/托盘；最大压力 4.4 bar；50 µm 过滤。作为上一代 GPU 冷板流量量级参照。",
    "key_data": [
        kd("每托盘流量 @ ≤45 °C", 5, "p.64 Water requirements", "LPM", "CPU≤400 W，GPU≤700 W ×4"),
        kd("每托盘流量 @ ≤40 °C", 4, "p.64", "LPM"),
        kd("最大压力", 4.4, "p.64", "bar"),
        kd("工作水温", "2–45 °C (ASHRAE W45)", "p.13"),
        kd("过滤", "50 micron (≈288 mesh)", "p.65"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})

# ---------------- OEM 其他 ----------------
E.append({
    "id": "ven-2025-hpe-gb300-nvl72-quickspecs", "type": "vendor_doc",
    "title": "NVIDIA GB300 NVL72 by HPE QuickSpecs (a50009244enw)",
    "title_zh": "HPE NVIDIA GB300 NVL72 QuickSpecs",
    "org": "HPE", "year": 2025, "venue": "HPE QuickSpecs",
    "url": "https://www.hpe.com/us/en/collaterals/collateral.a50009244enw.html",
    "language": "en", "access": {"status": "metadata_only", **VENDOR_PUBLIC,
                                  "how_to_get": "落地页为 HTML，可在页面内导出 PDF。"},
    "trust_level": "L3", "trust_reason": "OEM 官方规格书",
    "stages": [1, 8], "topics": ["vendors", "hpe", "gb300", "cdu"],
    "summary_zh": "HPE 版 GB300 NVL72：机架 TDP 132 kW 名义、EDPp 约 155 kW；列间 CDU 1.3 MW、最多带 8 机架；支持顶部/地板下二次侧供液。",
    "key_data": [
        kd("机架 TDP / 峰值 EDP", "132 nominal / ~155", "QuickSpecs 正文", "kW", vf="landing_page"),
        kd("列间 CDU 能力", "1.3 MW，最多 8 机架", "QuickSpecs CDU 节", vf="landing_page"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2025-supermicro-gb300-nvl72-datasheet", "type": "vendor_doc",
    "title": "Supermicro NVIDIA GB300 NVL72 Datasheet (SRS-GB300-NVL72)",
    "title_zh": "Supermicro GB300 NVL72 数据表",
    "org": "Supermicro", "year": 2025, "venue": "Supermicro datasheet",
    "url": "https://www.supermicro.com/en/products/system/gpu/48u/srs-gb300-nvl72",
    "language": "en",
    "access": {"status": "pending_user", "redistributable": False,
               "how_to_get": "supermicro.com 对脚本返回 403，请用浏览器下载 https://www.supermicro.com/datasheet/datasheet_SuperCluster_GB300_NVL72.pdf"},
    "trust_level": "L3", "trust_reason": "OEM 官方数据表",
    "stages": [1, 2, 8], "topics": ["vendors", "supermicro", "gb300", "cdu"],
    "summary_zh": "Supermicro GB300 NVL72 液冷选项：机架内 CDU 250 kW（N+1 泵）、列间 CDU 1.8 MW（最多 8 机架）、液–气边柜 CDU 200 kW。未公开机架流量/供液温度。",
    "key_data": [
        kd("CDU 选项", "In-rack 250 kW；In-row 1.8 MW（≤8 racks）；L2A sidecar 200 kW", "数据表 Liquid-Cooling Options（搜索引擎摘录）", vf="secondary"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})

# ---------------- Dow 冷却液 ----------------
E.append({
    "id": "hbk-2008-dow-dowfrost-engineering-guide", "type": "handbook",
    "title": "Engineering and Operating Guide for DOWFROST and DOWFROST HD Inhibited Propylene Glycol-based Heat Transfer Fluids (Form No. 180-01286-0208)",
    "title_zh": "DOWFROST / DOWFROST HD 抑制型丙二醇传热液工程与运行指南",
    "org": "The Dow Chemical Company", "year": 2008, "venue": "Dow Form No. 180-01286-0208 (Published February 2008)",
    "url": "https://www.dow.com/documents/180/180-01286-01-engineering-and-operating-guide-for-dowfrost-and-dowfrost-hd.pdf",
    "language": "en",
    "access": {"status": "pending_user", "license": "厂商公开文档（版权保留）", "redistributable": False,
               "how_to_get": "dow.com 对脚本返回 403（Akamai 反爬）。用浏览器打开该 URL 或 https://engage.dow.com/DOWFROSTEngGuide 下载后放入 files/handbooks/hbk-2008-dow-dowfrost-engineering-guide.pdf 并运行 fetch.py --verify。"},
    "trust_level": "L3", "trust_reason": "厂商测量/整理的物性表（非独立第三方），工业界广泛引用；按 L3 使用并与 ASHRAE Handbook 交叉核对",
    "stages": [3, 4, 5], "topics": ["vendors", "dow", "coolant", "propylene-glycol", "properties"],
    "summary_zh": "经典丙二醇水溶液物性手册：按体积浓度 0–90%（10% 步长）与温度给出密度、黏度、导热系数、比热、蒸气压表（英制/SI 各一），以及 30/40/50% PG 管内压降图。注意没有 25% 列，PG25 需在 20%/30% 间插值——Dow 另有专门的 DOWFROST LC 25 数据（见 hbk-2023-dow-dowfrost-lc-engineering-guide）。",
    "key_data": [
        kd("密度表位置（SI）", "Table 10（DOWFROST）/ Table 12（HD）", "pp.18–21 Density", vf="fulltext"),
        kd("黏度表位置（SI, mPa·s）", "Table 14 / Table 16", "pp.22–25 Viscosity"),
        kd("导热系数表位置（SI, W/m·K）", "Table 18 / Table 20", "pp.26–29 Thermal Conductivity"),
        kd("比热表位置（SI, kJ/kg·K）", "Table 22 / Table 24", "pp.30–33 Specific Heat"),
        kd("蒸气压表（kPa）", "Table 26", "p.34"),
        kd("管内压降图（SI）", "Figure 2 (30%) / Figure 4 (40%) / Figure 6 (50%)", "p.36 起 Pressure Drop"),
        kd("最低推荐浓度", "25% glycol（低于 25–30% 缓蚀不足、<25% 有细菌风险）", "p.9 Fluid Concentration；Table 4 注"),
        kd("稀释水质", "Cl⁻ ≤25 ppm, SO₄²⁻ ≤25 ppm, 总硬度 ≤100 ppm (CaCO₃)", "p.10 Table 5"),
        kd("膜系数关联式", "Sieder–Tate: Nu = 0.027 Re^0.8 Pr^0.33 (μ/μw)^0.14，Re ≥ 10,000", "p.17 Film coefficients"),
    ],
    "formulas": [{"name": "Sieder–Tate 湍流膜系数", "latex": "Nu=0.027\\,Re^{0.8}Pr^{0.33}(\\mu/\\mu_w)^{0.14}",
                  "validity": "充分发展湍流，Re ≥ 10,000（冷板微通道/射流区通常不适用）", "locator": "p.17"}],
    "benchmark_candidate": False, "related_internal": [PG25_REPORT],
    "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2028-10-02",
    "notes": "通过 WebFetch 读取 dow.com 官方 PDF 全文核对页码与表号（verified_from=fulltext），本地未存档。经 WebFetch 抽取的表格行列有错位，具体数值请在拿到原 PDF 后再读，勿直接引用本条目中的任何物性数字（本条目也未写入数值）。",
})
E.append({
    "id": "hbk-2023-dow-dowfrost-lc-engineering-guide", "type": "handbook",
    "title": "DOWFROST LC Inhibited Propylene Glycol-Based Heat Transfer Fluid – Heat management and corrosion protection in liquid cooled data center applications: Engineering and Operating Guide (Form No. 176-01641-01-0623)",
    "title_zh": "DOWFROST LC（PG25/PG55 数据中心冷板专用）工程与运行指南",
    "org": "The Dow Chemical Company", "year": 2023, "venue": "Dow Form No. 176-01641-01-0623 S2D",
    "url": "https://www.dow.com/en-us/market/mkt-electronics/sub-elec-data-center-cooling.html",
    "language": "en",
    "access": {"status": "pending_user", "license": "厂商公开文档（版权保留）", "redistributable": False,
               "how_to_get": "Dow 数据中心冷却页面列有 'DOWFROST LC: Engineering and Operating Guide' 下载入口，但 dow.com 对脚本 403。请用浏览器从 Dow 官网下载（务必确认版本号 0623 或更新），放入 files/handbooks/ 后 --verify。Dow 授权经销商（glycolsales.com.au、chemworld.com）有副本，但非 Dow 官网，未下载。"},
    "trust_level": "L3", "trust_reason": "冷却液厂商针对 PG25 预混液（DOWFROST LC 25）给出的物性表与运维限值；厂商测量数据",
    "stages": [1, 3, 4, 5, 7, 8], "topics": ["vendors", "dow", "pg25", "coolant", "properties", "water-quality", "filtration"],
    "summary_zh": "本项目最直接的 PG25 厂商资料：Table 2 给出 DOWFROST LC 25 在 −5~80 °C（5 °C 步长）的密度、比热、导热系数、黏度、蒸气压；Table 1 典型规格（25 vol%、冰点 −10 °C、pH 8.0–10.5、电导 >2000 µS/cm）；Table 5 稀释水要求；Table 8 在用液验收指标；§4.5 旁路过滤 25 µm；运行浓度 24–27 vol%。",
    "key_data": [
        kd("PG 浓度 / 冰点", "25 vol% / −10 °C", "Table 1", vf="secondary"),
        kd("pH（新液/在用）", "8.0–10.5", "Table 1；Table 8；§5.4", vf="secondary"),
        kd("电导率", ">2,000", "Table 1；§2.6", "µS/cm", vf="secondary"),
        kd("导热系数 / 比热 @ 50 °C", "0.485 W/m·K / 3.94 kJ/kg·K", "Table 1", vf="secondary"),
        kd("黏度 @ 20 / 50 °C", "2.8 / 1.3", "Table 1", "mPa·s", vf="secondary"),
        kd("LC 25 物性 @ 25 °C（ρ, cp, k, μ）", "1030.3 kg/m³, 3.88 kJ/kg·K, 0.462 W/m·K, 2.39 mPa·s", "Table 2（0623 版）", vf="secondary"),
        kd("LC 25 物性 @ 40 °C（ρ, cp, k, μ）", "1022.5 kg/m³, 3.92 kJ/kg·K, 0.476 W/m·K, 1.58 mPa·s", "Table 2（0623 版）", vf="secondary"),
        kd("稀释水要求", "Cl⁻ <25 mg/L；电导 <50 µS/cm；5 < pH < 9", "Table 5", vf="secondary"),
        kd("旁路过滤孔径", 25, "§4.5 Bypass filters", "µm", vf="secondary"),
        kd("运行浓度允许范围", "24–27 vol% PG（LC 25）", "§2.5", vf="secondary"),
        kd("在用液 Cu / Fe 上限", "<2 ppm / <2 ppm", "Table 8", vf="secondary"),
    ],
    "benchmark_candidate": False, "related_internal": [PG25_REPORT],
    "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-10-02",
    "notes": "【版本差异，重要】两份经销商副本的 Table 2 数值不同：Form 176-01641-01-0222（2022-02，chemworld.com 副本）@40 °C 为 ρ=1024.4、μ=1.39 mPa·s；0623 版（2023-06，glycolsales.com.au 副本）@40 °C 为 ρ=1022.5、μ=1.58 mPa·s（k、cp 一致）。黏度相差约 14%，直接影响压降计算。以 Dow 官网当前版为准，取得原件后把 verified_from 改为 fulltext。所有数值均来自经销商副本全文，故标 secondary。",
})
E.append({
    "id": "ven-2023-dow-dowfrost-lc-tds", "type": "vendor_doc",
    "title": "DOWFROST LC Heat Transfer Fluid Technical Data Sheet (Form No. 180-01627-01-0523)",
    "title_zh": "DOWFROST LC 传热液技术数据表",
    "org": "The Dow Chemical Company", "year": 2023, "venue": "Dow TDS Form No. 180-01627-01-0523 S2D",
    "url": "https://www.dow.com/en-us/pdp.dowfrost-lc-25-heat-transfer-fluid.497419z.html",
    "language": "en",
    "access": {"status": "pending_user", "license": "厂商公开文档（版权保留）", "redistributable": False,
               "how_to_get": "Dow 产品页 Technical Content 标签下载（浏览器；脚本 403）。ChemPoint（Dow 授权分销商）也提供 TDS 下载。"},
    "trust_level": "L3", "trust_reason": "冷却液厂商官方 TDS",
    "stages": [1, 3, 4], "topics": ["vendors", "dow", "pg25", "coolant"],
    "summary_zh": "DOWFROST LC 25/55 四页 TDS：用途为数据中心直触芯片液冷；LC 25 = 25 vol% PG，冰点 −10 °C，推荐使用温度 −10~90 °C，不得再稀释；典型规格同工程指南 Table 1。",
    "key_data": [
        kd("使用温度范围（LC 25）", "−10 °C ~ 90 °C", "p.1", vf="secondary"),
        kd("典型物性 @ 50 °C", "k 0.485 W/m·K；cp 3.94 kJ/kg·K", "p.1 Typical Product Specifications", vf="secondary"),
        kd("沸点", "101.4 °C @ 760 mmHg", "p.1", vf="secondary"),
        kd("体积膨胀（−40→90 °C）", "5.2 %", "p.1", vf="secondary"),
    ],
    "benchmark_candidate": False, "related_internal": [PG25_REPORT],
    "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-10-02",
})
E.append({
    "id": "hbk-0000-dow-dowtherm-sr1-engineering-guide", "type": "handbook",
    "title": "Engineering and Operating Guide for DOWTHERM SR-1 and DOWTHERM 4000 Inhibited Ethylene Glycol-based Heat Transfer Fluids (Form No. 180-1190)",
    "title_zh": "DOWTHERM SR-1 / 4000 乙二醇传热液工程与运行指南（可选，EG 对照）",
    "org": "The Dow Chemical Company", "year": 0, "venue": "Dow Form No. 180-1190",
    "url": "https://www.dow.com/en-us/pdp.dowtherm-sr-1-heat-transfer-fluid.html",
    "language": "en",
    "access": {"status": "pending_user", "redistributable": False,
               "how_to_get": "Dow 官网产品页（浏览器）下载；180-01286 指南 p.4 指明可向 Dow 索取此 Form。"},
    "trust_level": "L3", "trust_reason": "厂商物性手册",
    "stages": [3, 4, 5], "topics": ["vendors", "dow", "ethylene-glycol", "properties"],
    "summary_zh": "乙二醇（EG25 等）水溶液物性手册，用于国内厂商常用 EG25 工质的对照（超聚变/曙光等以 25% 乙二醇为主）。仅登记。",
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY,
})

# ---------------- 冷板 / CDU 厂商 ----------------
E.append({
    "id": "ven-2026-jetcool-product-catalog", "type": "vendor_doc",
    "title": "JetCool Product Catalog (SmartPlate / SmartLid / SmartSense CDU)",
    "title_zh": "JetCool 产品目录（微对流射流冷板 SmartPlate 等）",
    "org": "JetCool Technologies (Flex)", "year": 2026, "venue": "JetCool 官方目录（HubSpot 文件托管）",
    "url": "https://jetcool.com/smartplate-cold-plate/",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L4", "trust_reason": "厂商营销目录，性能数字为厂商声明，少数引用第三方测试但未附原始数据",
    "stages": [2, 3], "topics": ["vendors", "jetcool", "jet-impingement", "cold-plate", "microconvective"],
    "summary_zh": "与本项目技术路线最接近的商用产品：微对流（阵列射流冲击）冷板 SmartPlate，宣称冷却 GB200 级超级芯片 >3,400 W（热测试载具）、较微通道热阻低 25%（B200 第三方测试，MV Concept Lab Europe 2024）、热阻优 3–5 倍；SmartLid 直触封装 >3,500 W；可用 60 °C 进液。附 CDU 规格（160/300 kW，280/400 LPM，可用压头 28/22 psi，PG25）。",
    "key_data": [
        kd("SmartPlate 冷却能力（GB200 TTV）", ">3,400", "p.10 脚注 2", "W"),
        kd("相对微通道总热阻改善（B200 第三方测试）", "up to 25%", "p.10 脚注 3"),
        kd("相对微通道热阻", "3–5× better", "p.10"),
        kd("可用进液温度", "60 °C", "p.11"),
        kd("机架 CDU：容量 / 流量 / 可用压头", "160 kW, 280 LPM, 28 psi；300 kW, 400 LPM, 22 psi（PG25）", "p.13"),
        kd("设计流量比", "1 LPM/kW 与 1.5 LPM/kW 两种热负荷工况", "p.14"),
    ],
    "benchmark_candidate": False,
    "benchmark_note": "无可复现的几何/流量/热阻曲线；第三方测试报告（MV Concept Lab）若可获得才有验证价值。",
    "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2025-jetcool-smartplate-system-datasheet", "type": "vendor_doc",
    "title": "JetCool SmartPlate System Datasheet (Dell PowerEdge self-contained liquid cooling)",
    "title_zh": "JetCool SmartPlate 系统数据表",
    "org": "JetCool Technologies (Flex)", "year": 2025, "venue": "JetCool datasheet",
    "url": "https://jetcool.com/smartplate-cold-plate/",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "厂商产品数据表",
    "stages": [2], "topics": ["vendors", "jetcool", "jet-impingement"],
    "summary_zh": "自含式射流冷板系统（服务器内泵+散热器）：1U 850 W / 2U 1,200 W TDP，工质 PG25 或水基。与 GB300 设施水冷场景不同，仅作射流冷板产品形态参考。",
    "key_data": [
        kd("TDP 能力", "850 W (1U) / 1,200 W (2U)", "p.2 Physical Specifications", vf="fulltext"),
        kd("工质", "PG25; water-based coolants", "p.2"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2022-jetcool-smartplate-whitepaper", "type": "vendor_doc",
    "title": "Drive Faster Compute Sustainably with Microconvective Cooling (JetCool SmartPlate launch white paper)",
    "title_zh": "JetCool 微对流冷却 SmartPlate 白皮书",
    "org": "JetCool Technologies", "year": 2022, "venue": "JetCool white paper（经 Data Center Frontier 分发）",
    "url": "https://jetcool.com/post/third-party-testing-data/",
    "language": "en",
    "access": {"status": "metadata_only", "redistributable": False,
               "how_to_get": "jetcool.com 资源页填表下载；Data Center Frontier 托管副本：base.imgix.net/files/base/ebm/datacenterfrontier/document/2022/09/1663627554131-jetcool_smartplatelaunchwhitepaper.pdf（第三方托管，未下载）。"},
    "trust_level": "L4", "trust_reason": "厂商白皮书",
    "stages": [3, 7], "topics": ["vendors", "jetcool", "jet-impingement", "pg25"],
    "summary_zh": "阵列喷嘴直接冲击封装盖（冷板底即封装盖）；Intel Xeon 8268 + PG25 对比某品牌铜微通道冷板，热阻降低 3 倍且泵功更低；含 TDP–流量图（Fig.11）。",
    "key_data": [
        kd("相对铜微通道冷板热阻", "3X reduction（Xeon Platinum 8268，PG25）", "Fig.9 附近正文", vf="secondary"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY,
})
E.append({
    "id": "ven-2026-coolit-chx2000-product-sheet", "type": "vendor_doc",
    "title": "CoolIT CHx2000 Coolant Distribution Unit Product Sheet (V7)",
    "title_zh": "CoolIT CHx2000 列间 CDU 产品单页",
    "org": "CoolIT Systems", "year": 2026, "venue": "CoolIT product sheet",
    "url": "https://www.coolitsystems.com/cdu-product/chx2000/",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "厂商产品单页 + 官网规格",
    "stages": [2, 4, 8, 9], "topics": ["vendors", "coolit", "cdu", "filtration"],
    "summary_zh": "2 MW 列间 CDU，宣称可带 12 台 GB300 NVL72；PDF 以图形为主，数值主要来自官网与新闻稿：5 °C ATD 下 2000 kW、2125 LPM @ 35 psi、1.2 LPM/kW 设计流量比、集成 25 µm 过滤、不锈钢管路、4\" 卡箍接口、Redfish 群控 20 台。",
    "key_data": [
        kd("每 CDU 支持机架", "12x GB300 NVL72", "PDF p.1"),
        kd("冷却能力", "2000 kW @ 5 °C ATD", "官网产品页", vf="landing_page"),
        kd("流量 @ 外部压头", "2125 LPM @ 35 psi", "官网产品页", vf="landing_page"),
        kd("设计流量比", 1.2, "2025-04-15 新闻稿", "LPM/kW", vf="landing_page"),
        kd("二次侧过滤", "integrated 25-micron", "2025-04-15 新闻稿", "µm", vf="landing_page"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
    "notes": "完整规格表需在官网填表获取（邮件发送），属 pending_user 级别的补充材料。",
})
E.append({
    "id": "ven-2026-vertiv-coolchip-cdu-family-datasheet", "type": "vendor_doc",
    "title": "Vertiv CoolChip CDU Family Data Sheet (SL-80005, 05/26)",
    "title_zh": "Vertiv CoolChip CDU 系列数据表",
    "org": "Vertiv", "year": 2026, "venue": "Vertiv data sheet SL-80005",
    "url": "https://www.vertiv.com/globalassets/shared/vertiv-coolchip-cdu-family-data-sheet-sl-80005.pdf",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "厂商官方数据表",
    "stages": [2, 4, 8, 9], "topics": ["vendors", "vertiv", "cdu", "filtration", "control"],
    "summary_zh": "CoolChip CDU 600/1350/2300 kW（4 °C ATD）；二次侧可用处理水或 PG 混合液；二次侧过滤 25 µm 或 50 µm，一次侧 500 µm；支持 W45；二次侧供液温度控制 ±1 °C，压差或流量两种控制模式（对⑨孪生在环控制的执行器边界有用）。",
    "key_data": [
        kd("名义冷量", "600 / 1350 / 2300 kW @ 4 °C ATD", "p.2 规格表"),
        kd("二次侧过滤", "25 µ or 50 µ", "p.2", "µm"),
        kd("一次侧过滤", "500 µ", "p.2", "µm"),
        kd("供液温度控制精度", "±1 °C", "p.1"),
        kd("控制模式", "differential pressure 或 flow rate", "p.1"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2026-vertiv-xdu1350-application-planning-guide", "type": "vendor_doc",
    "title": "Vertiv XDU1350 Coolant Distribution Unit Application and Planning Guide (XDU1350B, SL-71309)",
    "title_zh": "Vertiv XDU1350 CDU 应用与规划指南",
    "org": "Vertiv", "year": 2026, "venue": "Vertiv SL-71309 Rev B",
    "url": "https://www.vertiv.com/494484/globalassets/shared/vertiv-liebert-xdu1350-coolant-distribution-unit_application-and-planning-guide_sl-71309.pdf",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "厂商官方应用规划手册",
    "stages": [2, 4, 8, 9], "topics": ["vendors", "vertiv", "cdu", "filtration", "pressure"],
    "summary_zh": "Vertiv 参考设计中 GB300 常用的 XDU1350：二次侧流量 1200 L/min @ 2.5 bar（双泵）、1800 L/min @ 2.0 bar（三泵）；二次侧供液 10–52 °C 带露点控制；直触芯片应用要求二次侧回水 50 µm 过滤，可选 25 µm 出厂过滤；一次侧至少 500 µm/35 目；一次侧最高 10 bar，二次侧 3–6 bar；带 pH、电导率（0–10,000 µS/cm）、浊度在线监测选项。",
    "key_data": [
        kd("二次侧流量（双泵）", "1200 L/min @ 36 psi (2.5 bar) external", "p.15", "L/min"),
        kd("二次侧流量（三泵）", "1800 L/min @ 29 psi (2.0 bar)", "p.15", "L/min"),
        kd("二次侧供液温度范围", "10–52 °C（露点控制）", "p.19 XDU1350 Specifications"),
        kd("二次侧过滤（直触芯片）", "required 50 µm on secondary return；factory option 25 µm", "p.17, p.23", "µm"),
        kd("一次侧过滤", "≥500 µm / 35 mesh", "p.22", "µm"),
        kd("最高工作压力（一次 / 二次）", "10 bar / 3–6 bar", "p.21"),
        kd("流体品质监测选项", "pH + 电导率(0–10,000 µS/cm) + 浊度", "p.17"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2026-motivair-cdu-brochure", "type": "vendor_doc",
    "title": "Motivair by Schneider Electric – Coolant Distribution Units (CDU) Brochure (January 2026)",
    "title_zh": "Motivair（施耐德）CDU 产品手册",
    "org": "Motivair (Schneider Electric)", "year": 2026, "venue": "Motivair brochure",
    "url": "https://www.motivaircorp.com/products/CDU/",
    "language": "en",
    "access": {"status": "pending_user", "redistributable": False,
               "how_to_get": "motivaircorp.com 对脚本返回 403 并重定向，请用浏览器从产品页 BROCHURES AND MANUALS 下载。"},
    "trust_level": "L3", "trust_reason": "厂商产品手册",
    "stages": [2, 4, 8], "topics": ["vendors", "motivair", "schneider", "cdu", "pg25"],
    "summary_zh": "MCDU-4U ~ MCDU-60（至 2.35 MW）/ MCDU-70（2.5 MW）；额定冷量以 25% PG 二次侧供/回 113/149 °F（45/65 °C）与 112/122 °F 等工况给出；施耐德 GB300 参考设计 RD111 采用 Motivair 液–液 CDU。",
    "key_data": [
        kd("额定工况示例", "一次侧 90 °F 供水；二次侧 25% PG 供/回 113/149 °F", "技术规格表（搜索引擎摘录）", vf="secondary"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2025-envicool-coolinside-full-chain-liquid-cooling", "type": "vendor_doc",
    "title": "Envicool Coolinside Full Chain Liquid Cooling Solution (brochure, 2025-09)",
    "title_zh": "英维克 Coolinside 全链条液冷解决方案（英文版手册）",
    "org": "Envicool（英维克，002837.SZ）", "year": 2025, "venue": "英维克官网资料下载",
    "url": "https://www.envicool.com/download.html",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L3", "trust_reason": "国内厂商官方产品手册（规格表部分）；性能宣称部分按 L4 看待",
    "stages": [2, 4, 8], "topics": ["vendors", "envicool", "cdu", "cold-plate", "coolant", "china"],
    "summary_zh": "国内头部液冷厂商全链条产品：GPU 冷板单芯片最高 1200 W、各支路流量偏差 ≤10%、GPU 间温差 ≤2 °C；列间 CDU 300–2500 kW（额定流量 450–3700 L/min），一次侧 32 °C / 二次侧 36 °C 供液，25 µm 过滤可选；机架内 CDU 40–160 kW，二次侧 PG25 40/35 °C；自研 SoluKing 冷却液 SK-E50-B 物性（pH 8.2–9.1、电导 2400–3400 µS/cm、冰点 −40 °C）。",
    "key_data": [
        kd("GPU 冷板单芯片能力", "up to 1200", "p.3 GPU cold plate module", "W"),
        kd("支路流量偏差 / GPU 间温差", "≤10% / ≤2 °C", "p.3"),
        kd("列间 CDU 额定冷量–流量", "300/600/800/1400/2500 kW ↔ 450/900/1000/1200/3700 L/min", "p.8 Technical Specification"),
        kd("列间 CDU 设计供液温度（一次/二次）", "32 / 36 °C", "p.8"),
        kd("二次侧过滤", "25 µm ultra dense filter（列间）；机架内 50 µm 可选", "p.8", "µm"),
        kd("机架内液液 CDU", "40/80/160 kW；二次侧 PG25 供液 40/35 °C；流量 60/99/160 L/min", "p.8"),
        kd("SoluKing SK-E50-B 冷却液", "pH 8.2–9.1；电导 2400–3400 µS/cm；冰点 −40 °C；cp@20 °C 3.19 kJ/kg·K", "p.10"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-2022-xfusion-cold-plate-server-reliability-whitepaper", "type": "vendor_doc",
    "title": "Cold-Plate Liquid-cooled Server Reliability White Paper",
    "title_zh": "冷板式液冷服务器可靠性白皮书（超聚变，英文版）",
    "org": "xFusion（超聚变）/ ODCC", "year": 2022, "venue": "xFusion 官网；ODCC 2022",
    "url": "https://www.xfusion.com/backapi/video/en/file/upload/202210/13/150820101.pdf",
    "language": "en", "access": {"status": "downloaded", **VENDOR_PUBLIC},
    "trust_level": "L4", "trust_reason": "厂商/产业联盟白皮书",
    "stages": [1, 2, 7], "topics": ["vendors", "xfusion", "reliability", "leak-detection", "china"],
    "summary_zh": "国内冷板液冷服务器可靠性：三级防漏（节点/机柜/机房）、>80% 热量经冷板带走、供水 25–28 °C 方案；二次侧工质为乙二醇溶液；材料兼容与腐蚀、防堵讨论。可用于⑦样件试验的可靠性项目清单参考。",
    "key_data": [
        kd("方案供水温度", "25–28 °C", "p.12"),
        kd("二次侧工质", "ethylene glycol solution", "p.19"),
    ],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY, "valid_until": "2027-04-02",
})
E.append({
    "id": "ven-0000-shenling-liquid-cdu", "type": "vendor_doc",
    "title": "申菱环境 液冷CDU 产品页",
    "title_zh": "申菱环境液冷 CDU",
    "org": "广东申菱环境系统股份有限公司", "year": 0, "venue": "shenling.com 产品页",
    "url": "https://www.shenling.com/products/%E6%B6%B2%E5%86%B7cdu/",
    "language": "zh", "access": {"status": "metadata_only", "redistributable": False,
                                  "how_to_get": "官网未提供 PDF 规格书，需联系申菱（4008-330-888 / sl@shenling.com）索取。"},
    "trust_level": "L4", "trust_reason": "厂商产品页，营销口径",
    "stages": [2], "topics": ["vendors", "shenling", "cdu", "china"],
    "summary_zh": "冷量 200–1800 kW，支持 ≤140 kW 高密机柜，全变频，兼容冷板/浸没/喷淋。无详细参数。",
    "key_data": [kd("冷量范围 / 机柜密度", "200–1800 kW / ≤140 kW", "产品特点 1", vf="landing_page")],
    "benchmark_candidate": False, "retrieved_by": BY, "last_verified": TODAY,
})


def load_log() -> dict:
    recs = {}
    for line in LOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            recs[r["id"]] = r
    return recs


def main() -> None:
    log = load_log()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    ids = set()
    for e in E:
        assert e["id"] not in ids, f"重复 id {e['id']}"
        ids.add(e["id"])
        if e["access"]["status"] == "downloaded":
            r = log.get(e["id"])
            assert r, f"{e['id']} 标为 downloaded 但日志无记录"
            p = LIB / r["path"]
            assert p.exists(), f"{p} 不存在"
            e["file"] = {k: r[k] for k in ("path", "sha256", "bytes", "pages", "source_url", "downloaded_at")}
        # schema 要求 year 必填：与 id 中年份一致，未知年份（0000）记 0
        e["year"] = int(e["id"].split("-")[1])
        jsonschema.validate(e, schema)
    OUT.write_text(json.dumps(E, ensure_ascii=False, indent=2), encoding="utf-8")
    n_dl = sum(e["access"]["status"] == "downloaded" for e in E)
    print(f"写出 {OUT}：{len(E)} 条，已下载 {n_dl} 条")


if __name__ == "__main__":
    main()

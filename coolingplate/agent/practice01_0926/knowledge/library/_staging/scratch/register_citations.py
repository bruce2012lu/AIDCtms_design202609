"""把内部数值对照里用到的外部出处登记进 registry/citations.json。只运行一次；重复运行前先删除该文件。"""

import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LIB / "tools"))
sys.stdout.reconfigure(encoding="utf-8")
import kb  # noqa: E402

V20 = "references/NVIDIA_B300_…_v2.0_20260914new.html"
V21 = "references/NVIDIA_B300_…_v2.1_PG25_20260929.html"
GR = "references/参考_GB300_Grace_CPU与液冷边界_20260926.html"
C = [
    ("ven-2025-nvidia-blackwell-ultra-datasheet", "p.5 技术规格表", "Max TDP GB300 NVL72", "1400", "W", V20 + " DP-B", "limit", "NVIDIA 一手；HGX B300 为 1100 W"),
    ("ven-2025-lenovo-gb300-nvl72-product-guide", "p.19 GPU 规格表", "B300 SXM DLC TGP（Lenovo）", "1100", "W", V20 + " DP-A", "limit", "Lenovo 口径"),
    ("ven-2025-lenovo-gb300-nvl72-product-guide", "p.2；p.24", "GB300 NVL72 rack TDP / peak", "135 / 155", "kW", V20 + " §2.2", "value", ""),
    ("ven-2025-lenovo-gb300-nvl72-product-guide", "p.2；p.24", "液冷热捕获比例", "约 90", "%", V20 + " §2.2", "value", ""),
    ("ven-2025-lenovo-gb300-nvl72-product-guide", "p.38 Table 27", "供液 25–45 °C 对应整柜流量", "59–177", "L/min", V21 + " §6", "value", "工质未注明"),
    ("ven-2025-lenovo-gb300-nvl72-product-guide", "p.38 Table 27", "整柜压降", "2.3–18.4 psi（15.9–126.9 kPa）", "psi", V20 + " §2.2", "value", ""),
    ("ven-2025-lenovo-gb300-nvl72-product-guide", "p.24", "工质", "DI 水（推荐）或 PG25", "-", V21 + " 封面", "value", ""),
    ("std-2023-ocp-oai-liquid-cooling-guidelines", "§1.3", "推荐冷却液温升 / 比流量", "7.5–12 °C；1.25–2.0 L/(min·kW)；典型 10 °C = 1.5", "°C", V21 + " §1", "limit", "按 PG25 物性换算"),
    ("ven-2022-nvidia-h100-pcie-product-brief", "p.10 Table 5", "HBM 热鉴定温度（H100 代理值）", "95", "°C", V21 + " 封面说明", "limit", "不是 B300 数据"),
    ("ven-2022-nvidia-h100-pcie-product-brief", "p.10 Table 5", "GPU T_AVG 热鉴定温度（H100 代理值）", "87", "°C", V20 + " §1.3 Tj,max=90 的最接近公开值", "limit", "内部 90 °C 无出处"),
    ("std-2023-ocp-oai-oam-base-spec-r2", "§7.6.3", "TIM 面积热阻（参考设计）", "0.1", "°C·cm²/W", V20 + " §5.3 R_TIM2 下限", "property", ""),
    ("ven-2023-meta-ocp-liquid-cooling-ai-platforms", "分析边界条件列表", "TIM 面积热阻（分析假设）", "0.2", "°C·cm²/W", V20 + " §5.3 R_TIM2 上限", "property", ""),
    ("std-2023-ocp-oai-liquid-cooling-guidelines", "§6.3.3", "1 kW OAM 单冷板壳–进液热阻（TTV）", "0.014–0.019", "°C/W", V20 + " §1.3 热阻目标 < 0.025–0.028", "benchmark", "几何未公开，仅量级"),
    ("dat-2023-nist-water-isobar-1atm", "表行 T=40.0000", "水 40 °C ρ / cp / μ / k", "992.216 / 4179.41 / 6.52729e-4 / 0.628486", "SI", V20 + " §3.2 水基线物性", "property", "内部 k=0.631 偏高 0.4 %"),
    ("dat-0000-cda-c11000-properties", "Physical Properties 表", "C11000 导热率 20 °C", "226 Btu/(ft·h·°F) ≈ 391", "W/(m·K)", V20 + " 附录 A k_Cu=390", "property", ""),
    ("hbk-2026-cda-copper-tube-handbook", "p.15", "热水（≤ 60 °C）铜管流速上限", "5 ft/s ≈ 1.52", "m/s", V21 + " 孔速上限 2.0 m/s", "limit", "管道而非短孔，量级参照"),
    ("std-2019-ashrae-water-cooled-servers", "PDF p.25", "TCS 绝对过滤精度", "最细流道的 1/7–1/10", "-", "cad/coldplate/rules.py 过滤 ≤ 孔径 1/10", "limit", ""),
    ("std-2019-ashrae-water-cooled-servers", "PDF p.24", "TCS 水质（pH、Cl、电导率等）", "见 cards/tables CSV", "-", "⑥⑦ 运维规范", "limit", "水基 TCS；PG25 另见 OCP"),
    ("pap-2021-wei-microjet-correlations-feed-drain", "Eq.(19) p.11", "交替进排液微射流 Nu_f 关联式", "见卡片", "-", "tools/correlations.py wei；oned.py 交叉核对", "formula", "H/L、Pr 域外"),
    ("pap-2009-whelan-nozzle-geometry-jet-array", "Eq.(2) p.10", "Robinson & Schnitzler 受限淹没阵列 Nu_L", "见卡片", "-", "tools/correlations.py rs", "formula", "转引"),
    ("pap-2008-celik-gci-procedure", "Eq.(1)–(7) PDF p.5–7；Table 1 p.9", "GCI 五步法", "见卡片", "-", "tools/gci.py", "formula", ""),
    ("pap-2021-wei-microjet-correlations-feed-drain", "Table 1 p.3", "Martin 1977 阵列式有效域（转述）", "2000 < Re < 100000；2 ≤ H/D ≤ 12；Re 指数 0.67", "-", V20 + " §9.4 Martin 不采用", "limit", "Martin 原文付费"),
]
done = 0
for (eid, loc, qty, val, unit, used, role, note) in C:
    rec = kb.cite(LIB, eid, loc, qty, val, unit, used, role, note)
    done += 1
    print(rec["cid"], eid, qty)
print("registered", done)

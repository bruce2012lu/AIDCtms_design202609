# vendors 主题检索日志（2026-10-02，subagent-vendors）

产出：`entries.json` 33 条（已下载 20，pending_user 7，login_required 1，metadata_only 5）。
所有下载走 `tools/fetch.py`，`fetch.py --verify` 结果：mismatch 0、unlogged 0。

## 辅助脚本（本目录）
- `grep_pdf.py`：按页检索 PDF 关键词，用于给 key_data 定 locator。
- `probe.py`：只读 GET 落地页，列出其中 PDF 直链（用于 NVIDIA resources 页面 → DAM CDN 原件）。
- `peek.py`：内存读取候选 PDF 的页数/标题/首页（不落盘），用于辨认 NVIDIA DAM 上的无名链接。
- `build_entries.py`：条目元数据 + 从下载日志自动回填 file 块 + jsonschema 校验 → `entries.json`。改条目请改它再重跑。

## 检索关键词与站点
| 方向 | 关键词（节选） | 站点 | 结果 |
|---|---|---|---|
| NVIDIA | DGX GB300 user guide liquid cooling supply temperature flow；DGX SuperPOD GB300 RA；Blackwell Ultra datasheet 1,400 W；GB300 thermal design guide | docs.nvidia.com、resources.nvidia.com、developer.nvidia.com、dam-cdn.nvd.orangelogic.com | 下载 8 份；冷却液温度/流量/压降在 NVIDIA 公开文档中**没有**，只有 TDP 与"液冷+风冷混合"定性描述 |
| NVIDIA@OCP | MGX Accelerated Computing Rack and Tray Specification；GB200 NVL72 OCP contribution | opencompute.org、NVIDIA 博客 | MGX 规范 §11 有机架级液冷需求（130 LPM、5 bar、25/50 µm 等），全文经 WebFetch 核对；脚本下载 403 |
| Lenovo | GB300 NVL72 environmental specifications；Neptune water quality；SC777 V4 / SD650-N V3 product guide | lenovopress.lenovo.com、pubs.lenovo.com | 下载 5 份；GB300 流量–温度–压降表、W45、水质/过滤/材料标准都在这里 |
| Dow | DOWFROST engineering and operating guide 180-01286；DOWFROST LC 25 TDS；DOWFROST LC engineering guide | dow.com、engage.dow.com | dow.com 全站对脚本 403；180-01286 全文经 WebFetch 从 dow.com 读到；LC 指南/TDS 只在经销商副本中读到 |
| CDU/冷板 | CoolIT CHx2000；Vertiv CoolChip / XDU1350；Motivair CDU；JetCool microconvective；Boyd cold plate；Asetek | coolitsystems.com、vertiv.com、motivaircorp.com、jetcool.com（HubSpot 托管） | 下载 CoolIT 1、Vertiv 2、JetCool 2；Motivair 403；Boyd 仅管式冷板（相关性低，未登记）；Asetek 未找到数据中心冷板 PDF |
| 国内 | 英维克 冷板 CDU 白皮书；曙光数创 冷板 白皮书；高澜 CDU；申菱 液冷CDU；冷板式液冷服务器可靠性白皮书 | envicool.com、xfusion.com、shenling.com | 下载英维克、超聚变各 1；申菱只有产品页；高澜只有投资者问答（未登记）；曙光未找到官网 PDF |
| OEM 对照 | HPE GB300 QuickSpecs；Supermicro GB300 datasheet | hpe.com、supermicro.com | HPE 落地页登记；Supermicro 403 → pending_user |

## 失败与处理
- **403 反爬**：dow.com、opencompute.org、supermicro.com、motivaircorp.com 对 httpx 返回 403。没有绕过，标 `pending_user`，how_to_get 写浏览器手动下载路径。
- **Vertiv 旧链接 404**：`/49e61b/...xdu1350b-sl-71309.pdf` 404，换 `/494484/globalassets/shared/...sl-71309.pdf` 成功（实际重定向到 `/4a3315/`）。
- **NVIDIA DAM 偶发 SSL EOF**：重试成功。
- **id 年份更正**：先按猜测年份下载后，用 PDF 版权年/版本号核对，以下 8 份以正确 id 重新下载并删除旧文件（下载日志里旧 id 的记录保留，属历史，--verify 不受影响）：dgx-b300-dc-best-practices→2026、vertiv-coolchip→2026、vertiv-xdu1350→2026、blackwell-architecture-brief→2025、dgx-gb200-datasheet→2025、coolit-chx2000→2026、jetcool-product-catalog→2026、jetcool-smartplate-system-datasheet→2025。
- **CoolIT 产品单页**几乎全是图片，数值改从官网/新闻稿取（verified_from=landing_page）。

## verified_from 口径
- `fulltext`：本地已下载 PDF 用 fitz 抽文本核对；或 WebFetch 读到**官方域名**上的 PDF 全文（OCP MGX 规范、Dow 180-01286），这两条在 notes 里注明"本地未存档"。
- `secondary`：只在经销商副本或搜索引擎摘录中读到（Dow LC 指南/TDS、Supermicro、Motivair、JetCool 2022 白皮书）。
- `landing_page`：官网 HTML 页面（NVIDIA 博客、HPE QuickSpecs、CoolIT 产品页、申菱）。

## 给 PG25 物性报告作者的提醒（不改那份报告，只提示）
- DOWFROST LC 工程指南存在两版 Table 2：Form 176-01641-01-**0222** 与 **0623**。@40 °C：ρ 1024.4 vs 1022.5 kg/m³，μ 1.39 vs 1.58 mPa·s（k、cp 一致）。黏度差约 14%，会直接影响压降。请以 Dow 官网当前版为准。
- 经典 DOWFROST 指南（180-01286）浓度只有 10% 步长，没有 25% 列，PG25 要插值；且该指南是 DOWFROST（磷酸氢二钾缓蚀）而非 LC 配方，物性接近但缓蚀剂不同。
- WebFetch 抽出来的 180-01286 表格行列有错位，条目里刻意没写任何物性数字，只给表号/页码。

## 关键发现与冲突
1. **B300 功耗口径冲突**：NVIDIA Blackwell Ultra 数据表 p.5 —— GB300 NVL72 形态"可配置至 1,400 W"，HGX B300"可配置至 1,100 W"；Lenovo LP2357 p.19 Table 10 —— "NVIDIA SXM B300 DLC TGP 1100W"（GB300 NVL72 产品）。热设计基线应取 NVIDIA 1400 W 上限，Lenovo 值可能是其出货配置。
2. **机架功率口径**：NVIDIA DGX GB 用户指南 ≈120 kW；HPE 132 kW 名义 / 155 kW 峰；Lenovo 135 kW TDP / 155 kW 峰；NVIDIA NVL72 AI Factory RA 最高 142 kW；OCP MGX 规范按 120 kW、85% 液体取热。
3. **GB300 机架流量**：只有 Lenovo 公开（59/71/89/119/177 LPM @ 25/30/35/40/45 °C，压降 2.3→18.4 psi），未注明工质；OCP MGX（GB200 时代）为"最高 130 LPM"。单 GPU 冷板流量与允许压降在公开资料中**找不到**。
4. **过滤精度**：OCP MGX 25/50 µm；Lenovo 50 µm（≈288 目）；Vertiv 直触芯片要求 50 µm、可选 25 µm；CoolIT 25 µm；Dow LC 旁路过滤 25 µm；英维克 25 µm（列间）。对微射流喷嘴最小孔径的设计约束很重要（⑥）。
5. **"100% 液冷"**是 NVIDIA 数据表的营销口径，技术文档均为混合冷却（约 90% 液 / 10% 风）。

## 未覆盖 / 建议后续
- NVIDIA GB300/B300 热设计指南（NDA）、OCP MGX 规范更新版（是否有 GB300 修订）。
- CoolIT CHx2000 完整规格表（官网填表邮件发送）。
- JetCool 与 MV Concept Lab 的 B200 第三方测试报告（若公开，可能是本项目唯一接近"射流冷板实测"的厂商数据）。
- 曙光数创、高澜、申菱的正式产品手册（官网无公开 PDF，需联系厂商）。
- CAICT《算力中心冷板式液冷发展》（2024-05）、ODCC 各白皮书属研究机构/联盟，不在 vendors 范围，建议由 standards/reports 主题登记。

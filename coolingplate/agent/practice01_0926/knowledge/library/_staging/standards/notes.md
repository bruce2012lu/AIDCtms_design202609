# standards 检索日志（知识库 v0.1）

- 日期：2026-10-02
- 执行：kb-v0.1-standards-subagent
- 产出：`entries.json`（35 条，schema 校验 0 错误）；`files/standards/` 新增 6 个 PDF（sha256 已写入 `_staging/downloads.log.jsonl`，`fetch.py --verify` 无不一致）
- 辅助：`probe_links.py`（只列链接，不下载）；`fulltext_webfetch/`（OCP 7 份文件经 WebFetch 提取的全文文本快照，供核对 locator）

## 统计

| 状态 | 数量 |
|---|---|
| downloaded | 7（6 新下载 + 1 仓库已有 ASHRAE 主流化白皮书，仅登记引用） |
| pending_user | 15（OCP 7 份免费但需浏览器过 Cloudflare；ODCC 3；GB/T 48023；GB 50174；运营商白皮书；OCP 水基 Base Spec；UQD） |
| paywalled | 10 |
| login_required | 3（JEDEC JESD51-1/-12/-14） |

## 检索过程与结论

1. **OCP**：opencompute.org 的 `/documents/`、`/wiki/` 对脚本（httpx，换 Chrome/curl/wget UA）一律返回 Cloudflare challenge 403，`fetch.py` 无法落盘。WebFetch 工具可取回 PDF 全文文本，故 OCP 条目的 key_data 标记 `verified_from=fulltext`（依据官方 URL 的全文文本，页码取自文内 PAGE 标记），`access.status=pending_user`，等用户浏览器下载后补 `file` 块。未使用任何第三方镜像（hansenfluid、scribd、sgpjbg 等均排除）。rackcdn CDN（OCP 官方静态存储）只检索到 Rev2 会议幻灯片的地址，未找到各 PDF 的直接 CDN 链接。
2. **ASHRAE TC9.9**：tpc.ashrae.org Documents 页可直接下载，取得 2019 Water-Cooled Servers、2024 Resiliency 公告、2026 TCS Coolant Integrity 公告（新发现，直接涉及 PG25）。2021 主流化白皮书仓库已有，未重复下载。付费：Liquid Cooling Guidelines 2nd ed.、Thermal Guidelines 5th ed.、Datacom Encyclopedia（S 等级出处）、Handbook Fundamentals Ch.31（2021/2025 均为第 31 章，已在官方目录确认）。
3. **ASME/GUM**：V&V 20-2009(R2021)、PTC 19.1-2018(R2024) 付费登记；JCGM 100:2008 从 BIPM 官网下载并核对 §5.1.2 Eq.(10)、§6.3.3、G.4.1 Eq.(G.2b) 位置。
4. **JEDEC**：JESD51-1/-12/-14 页面写明 "Free download. Registration or login required."，未绕过登录下载，登记 login_required。检索引擎返回了 JESD51-14 官方 PDF 片段（Δθ≥0.5 K/W 等），标记为 `secondary`、待核对。
5. **国内**：
   - 新发现国标 **GB/T 48023-2026《数据中心冷板式液冷系统技术规范》**（2026-07-30 发布，2027-02-01 实施），openstd 有"在线预览/下载"，但需人工验证码。
   - 用户提示的 "YD/T 3982 间接冷板式" 有误：冷板服务器系统为 **YD/T 3980-2021**；**YD/T 3982-2021** 是冷却液体标准。另有 YD/T 6049-2024（整机柜）、YD/T 6358-2025（冷板式液冷数据中心）。
   - ODCC：检索到 ODCC-2023-05007（冷板服务器可靠性测试规范）、ODCC-2024-02006（非水冷板）、ODCC-2023-02004（白皮书）的编号，仅见于转载站（五八文库，已排除），官网需注册 → pending_user。
   - 中国信通院两份报告官网 PDF 已下载。
   - 三大运营商白皮书未找到运营商官网原件，网上只有第三方转载 → pending_user，未下载。
   - T/CIE 液冷团标：本轮未检索到明确条目，未登记。

## 已发现的口径冲突（下游使用需注意）

- **PG25 浓度口径**：OCP Base Spec 规定 25–28 wt%（≈24.5–27.5 vol%）；OCP 2022 指南为 24.5–29.5 vol%；ASHRAE 2026 公告写"名义 25 vol%"。
- **IEC 62368-1 压力试验倍数**：OCP Rev2/资格白皮书按第 3 版写 3× 正常工作压力；ASHRAE 2026 公告按第 4 版写 1.5× 额定最大工作压力。
- **W 等级 vs S 等级**：W17–W+ 定义的是设施水（FWS）；冷板入口（TCS）应看 S 等级（30–50 °C），S 分档具体值仅有二手来源，须订阅 Datacom Encyclopedia 核对。
- **过滤**：OCP 指南 <5 µm 旁路；Deschutes CDU 主路 25–44 µm + 旁路 0.2 µm；ASHRAE 规则为最小流道 1/7–1/10（或 2X–10X）。B300 微射流冷板需按最小喷孔/流道尺寸反推。
- **OCP PG25 指南 2026-07 起处于修订中**，正式要求以 PG25 Base Spec v1.0.0 为准。

## 红线自查

- 未从 bzxz、标准分享网、doc88、道客巴巴、百度文库、五八文库、scribd 等下载任何文件。
- 未安装 Python 包；只在 `files/standards/` 与 `_staging/standards/` 写入（`fetch.py` 按设计向 `_staging/downloads.log.jsonl` 追加日志）。
- 未修改已有文件，未 git commit/push。

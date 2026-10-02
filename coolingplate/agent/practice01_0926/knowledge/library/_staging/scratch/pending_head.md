# 待用户获取清单

日期：2026-10-02。下列条目没有下载全文：付费、需登录 / NDA、或站点拦截脚本（Cloudflare 403）而需要浏览器手动下载。本轮没有绕过任何拦截，也没有使用影子图书馆。

拿到文件后：放到 `files/<类型>/<id>.<扩展名>`，在条目里把 `access.status` 改为 `downloaded` 并补 `file` 块（`python tools/fetch.py --verify` 可列出未登记文件及其 sha256），然后 `kb.py ingest --id <id>` 与 `kb.py index`。付费件 `redistributable=false`，不入 git。

## 优先清单（按对当前设计结论的影响排序）

| 序 | 条目 id | 内容 | 为什么急 | 获取途径 | 费用 |
|---|---|---|---|---|---|
| 1 | `ven-0000-nvidia-gb300-thermal-design-guide` | NVIDIA GB300/B300 热设计指南（NDA） | 封装外形、die/HBM 坐标、power map、Tj、单板流量与允许压降全在这里；内部热阻预算的 Tj 90 °C、R_pkg 都无公开出处 | NVIDIA 合作伙伴门户，或经 Lenovo/HPE/Supermicro 在 NDA 下获取 | NDA |
| 2 | `hbk-2023-dow-dowfrost-lc-engineering-guide` | Dow DOWFROST LC 工程与运行指南（0623 或更新版） | PG25 粘度：内部 1.15 mPa·s，经销商副本 1.39–1.58 mPa·s，差 17–27 % | dow.com 数据中心冷却页面，浏览器下载 | 免费 |
| 3 | `std-2022-ocp-pg25-guidelines`、`std-2026-ocp-pg25-base-spec` | OCP PG25 指南与 PG25 Base Spec v1.0.0 | 浓度 wt%/vol% 基准、过滤、材料兼容、铜腐蚀验收 | opencompute.org 落地页，浏览器下载 | 免费 |
| 4 | `pap-2017-rattner-jet-array-extraction-ports` | Rattner 2017 J. Heat Transfer，低 Re 穿插抽液口射流阵列通用关联式 | Re 20–500、Pr 1–100，覆盖本项目工况最好；可能成为一维射流主关联式 | ASME Digital Collection 单篇购买或机构订阅 | 付费（价格以页面为准） |
| 5 | `hbk-2025-ashrae-fundamentals-ch31` | ASHRAE Handbook—Fundamentals 第 31 章（二次冷却剂物性） | PG 水溶液物性的 L1 权威表 | 购买 2021/2025 版，或高校 Knovel | 付费 |
| 6 | `pap-2001-li-garimella-prandtl-jet` | Li & Garimella 2001 IJHMT，Pr 效应与通用关联式 | PG25 的 Pr 修正指数（本库暂用 0.44，符号待核） | 开放副本需浏览器下载（Purdue e-Pubs 403） | 免费 |
| 7 | `std-2022-ocp-coldplate-dev-qualification` | OCP 冷板开发与资格认证白皮书 | ⑦ 样件试验大纲；冷板入口流速 < 1.5 m/s（对照项目 2.0 m/s 孔速上限） | opencompute.org，浏览器 | 免费 |
| 8 | `std-2023-ocp-oai-liquid-cooling-guidelines`、`std-2023-ocp-oai-oam-base-spec-r2`、`ven-2023-meta-ocp-liquid-cooling-ai-platforms` | OCP OAI 液冷指南、OAM r2.0、Meta 液冷实践 | 内部 v2.1 的 7.5–12 °C、1.5 L/(min·kW) 与 TIM2 0.1–0.2 °C·cm²/W 的原件（本轮已经官方域名全文核对，未落盘） | opencompute.org，浏览器 | 免费 |
| 9 | `std-2009-asme-vv20` | ASME V&V 20-2009 (R2021) | ⑤ CFD 验证与确认的正式标准 | asme.org 购买 | 付费 |
| 10 | `pap-2006-lee-garimella-developing-microchannel`、`pap-2005-lee-garimella-rect-microchannel-ht` | 矩形微通道热发展区换热 | 替换 HBM 一维 Nu = max(4, 1.86 Gz^{1/3}) | 开放副本需浏览器下载 | 免费 |
| 11 | `std-2010-jedec-jesd51-14` 等 JESD51 | JEDEC 热测试（瞬态双界面法 RθJC） | ⑦ TTV 与封装热阻测量 | jedec.org 免费注册后下载 | 免费注册 |
| 12 | `std-2026-sac-gbt48023-coldplate`、`std-2021-ccsa-ydt3980-coldplate-server`、`std-2021-ccsa-ydt3982-coolant` | GB/T 48023-2026 冷板式液冷系统；YD/T 3980 冷板服务器；YD/T 3982 冷却液 | 国内验收口径 | openstd.samr.gov.cn 预览/下载（需人工验证码）；YD/T 经人民邮电出版社或 CCSA 购买 | 国标免费预览；行标付费 |
| 13 | `pap-2002-qu-mudawar-microchannel` | Qu & Mudawar 2002 微通道实验 + 数值 | HBM / Grace 微通道的经典验证算例 | Elsevier 单篇或机构订阅 | 付费 |
| 14 | `dat-2024-grant-frontier-hpc-facility-data` | Frontier 设施运行数据 XLSX（CC BY 4.0） | ⑧⑨ 唯一公开大规模液冷运行数据 | figshare 浏览器下载 | 免费 |
| 15 | `pap-1977-martin-impinging-gas-jets` | Martin 1977 原文 | 核对 f 区间与原式；内部只用于“不适用”判断，优先级低 | Elsevier / Advances in Heat Transfer 单章购买 | 付费 |

另外两项未登记、建议补检：
- Wei 2021 Table 1（p.3）列出的 Muszynski & Andrzejczyk（受限多孔射流，500 < Re < 2500，Re 指数 0.65）——低 Re 关联式候选，原始文献信息待查。
- 疑似中电科十四所“静压腔 + 射流孔 / 回液孔阵列”专利（只在二手站看到摘要），与本项目结构高度相关，需到 CNIPA 核对号码后登记。

HAL 下载说明：`papers-jet` 子任务对 HAL 用了“如实声明身份的工具 UA”（`_staging/papers-jet/fetch_honest_ua.py`），没有绕过验证码或登录。是否接受这种做法请确认；不接受则删除对应文件并改为 pending_user。

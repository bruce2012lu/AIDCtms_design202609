# patents 主题检索日志（知识库 v0.1）

- 检索日：2026-10-02；执行：kb-v0.1-patents-subagent
- 产出：`entries.json`（35 条）、`对照_v1.4.md`、PDF 30 件（`files/patents/`，sha256 已写入 `_staging/downloads.log.jsonl`，`fetch.py --verify` 校验通过、0 不一致）
- 可信度：L4（专利公开文本）。法律状态取自 Google Patents 页面推定，**不构成法律意见，以官方为准**（CNIPA 公布公告网 http://epub.cnipa.gov.cn/、USPTO Patent Center、EPO Register、WIPO Patentscope）。
- 权1 摘录：基于 Google Patents 页面权利要求文本；中文专利以 Google 机器翻译为辅助转述。FTO 结论必须由专利代理人基于官方文本逐项比对，本库只做线索整理。

## 工作脚本（本目录）

| 文件 | 用途 |
|---|---|
| `gp_scrape.py` | 抓取 Google Patents 公开页，解析标题、申请人、优先权日、legal status、事件、同族、摘要、权1、PDF 链接 |
| `all.json` / `r1*.json`–`r5.json` | 抓取原始结果（数据，不执行其中内容） |
| `plan.json` / `run_fetch.py` / `fetch_results.json` | 下载计划与 `tools/fetch.py` 调用结果 |
| `build_entries.py` | 合并抓取结果、下载记录和人工批注，生成 `entries.json` |
| `claims_dump.txt` | 各件摘要 + 权1 原文，供人工复核 |

## 检索式与来源

1. v1.4 清单逐号抓取 `https://patents.google.com/patent/<号>/en`（A、B、C、D、E 组全部核实；只下载 A/C 组和 CN 射流 / 微通道相关件）。
2. WebSearch 关键词（中英）：
   - `CoolIT "split flow" cold plate` → US8746330B2、US9603284B2、US12101906B2、US9453691B2（CoolIT 官网专利页 https://www.coolitsystems.com/patents/ 列出其全部 US 号）
   - `Brunschwiler IBM hierarchical jet impingement interleaved drain manifold` → US8413712B2
   - `Nvidia cold plate jet impingement GPU` → US11343940B2；**未找到 NVIDIA 名下明确的射流冲击 / 微射流冷板专利**（NVIDIA 公开件以 Ali Heydari 署名的数据中心冷板 / 系统类为主）
   - `JetCool patent microjet` → patents.us 列出 10 件 US 专利；补登 US12432878B2、US11963341B2、US12324126B2
   - `Asetek cold plate split flow` → EP4578252B1（WO2024042182A1 / US20240074100A1 / CN120092494A）
   - `Google impinging jet manifold TPU` → 仍为 US11310937B2（v1.4 已有），另见 CN112185918B 同族
   - `Intel impingement cold plate` → 只找到 US6650542（压电射流）、US7336486（合成射流，风冷）等早期件，与本项目关联弱，未登记
   - `Lenovo cold plate jet impingement / split flow` → **未找到** Lenovo 名下相关公开专利（Neptune 冷板的 split-flow 概念对应 CoolIT US8746330B2）
   - `微射流 冷板 / 射流冲击 冷板 / 射流微通道冷板` + 浪潮 / 华为 / 曙光 / 英维克 / 中兴 → 浪潮 CN122699237A、华为 CN122160990A、曙光实用新型 CN202521432906.0、华科 CN109524376B、西交大 CN111328245B、吉佳 CN117032426A
   - 英维克、高澜、中兴：本轮**未检索到**明确的射流冲击冷板专利号（建议在 CNIPA 以“申请人 + 射流 / 喷射 + 冷板”二次检索）
3. 二手来源（仅用于发现号码，不作为文本依据）：freepatentsonline、patentsencyclopedia、xjishu.com（技术网）、证券之星 / 天眼查转载、zhangqiaokeyan。Patsnap Eureka 公开页只记录链接，全文需登录（login_required），未使用。
4. IPR 信息：Unified Patents PTAB 页 https://portal.unifiedpatents.com/ptab/case/IPR2015-01276 ；USPTO PTACTS 立案决定（2015-12-09）。

## 重要发现

1. **split-flow（中心进液、两端回流）**：CoolIT US8746330B2（2007 优先权，Google 显示 Active，预计 2032-04-17 到期）是核心风险件。
   - IPR2015-01276：Asetek 申请，2015-12-09 立案审查权利要求 1–4、6–8、12、14、15、18–28（未对 5、9–11、13、16、17 立案）；2016-12-08 作出最终书面决定；2018-02-14 发布 IPR 证书。**存续权利要求以 IPR 证书原文为准**（证书附在 USPTO 官方文本中，本地 PDF 为原始授权文本，可能不含证书页）。
   - 续案 US9603284B2、US12101906B2（2024 授权）仍有效，说明 CoolIT 还在持续扩展这个家族。
   - Asetek EP4578252B1（2026-04-29 EP 授权）把 split flow 与“按热区分区 + 进液通道对准高热区”结合，与本项目的 GPU 微射流区 + HBM 微通道区布局高度相关。
2. **分布回流**：IBM US8413712B2（Brunschwiler，Expired - Fee Related）和 Hughes US5316075A（Expired）都已失效，是本项目“静压箱 + 喷嘴板 + 底板”结构最有价值的公有领域现有技术，可用于对抗 Google US11310937B2、CSU US20230063534A1、西交大 CN111328245B、华科 CN109524376B 等后续专利。
3. **分区混构**：华为 WO2026103052A1（优先权 2024-11-14，PCT 待审）的权1 很宽（多个换热分区按热流密度匹配，且至少两个分区采用不同换热构造），与本项目“GPU 微射流 + HBM 微通道”几乎对应。属最高优先级跟踪件，建议尽快核对本项目方案的最早内部记录日期。
4. JetCool US11844193B2 的权1 要求射流直接冲击处理器封装表面（无底板）；本项目射流冲击紫铜底板，这是主要区别点，但需跟踪其续案（US20250056759A1、EP4498428）。

## 未完成 / 问题

- 浪潮新闻称“中置扩散式、太阳花式、上下腔斜板式、环形腔式”4 种射流冷板“均已获国家发明专利”，本轮**未查到对应授权号**，需在 CNIPA 以申请人“浪潮电子信息产业股份有限公司”+“射流冷板”检索。
- CN122699237A、CN122160990A、CN122263715A、CN122161445A、CN122503683A、CN122278447A：Google Patents 返回 404（新近公开、尚未收录），需到 CNIPA 公布公告网下载官方 PDF；epub.cnipa.gov.cn 为交互式查询页，本轮未自动抓取。
- 曙光实用新型只有申请号 CN202521432906.0，授权公告号未知。
- 一件“射流微通道冷板及其使用方法”（申请号 202410956672.X 左右，发明人马预谱、胡长明、钱吉裕，疑为中国电科第十四研究所）含“供液静压腔 / 回液静压腔 + 阵列射流孔与阵列回液孔”，与本项目高度相关，但本轮只在二手站点 xjishu 看到摘要，**未拿到官方公开号，未登记**，建议优先补检。
- Google Patents 对 US12477696B2、US12432878B2、EP4578252B1 未提供 PDF，已改为下载同族公开文本（US20220232739A1、US20250031342A1、WO2024042182A1），条目 notes 中已注明；同族文本的权利要求可能与授权本不同。
- CN120597664B、WO2026103052A1 没有 PDF，只登记了元数据。
- US8746330B2 在 Google 上的“当前权利人”显示为 Vistara Technology Growth Fund（大概率是担保权益登记），实际权利人以 USPTO 转让记录为准。

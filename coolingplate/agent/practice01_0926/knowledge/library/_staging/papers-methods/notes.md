# papers-methods 检索日志（2026-10-02）

主题：CFD 验证方法（GCI/V&V）、PG 水溶液物性来源、数据中心液冷数字孪生与控制、中文文献。
产出：`entries.json`（33 条，其中 20 条已下载全文）；生成脚本 `build.py`（从 `../downloads.log.jsonl` 回填 file 块）。
全部下载经 `tools/fetch.py`；`fetch.py --verify` 结果：mismatch=0，unlogged=0。

## 检索途径
- Crossref `query.bibliographic` 解析 DOI；OpenAlex `works/doi:` 判断 OA 状态与合法 OA 位置。
- Unpaywall：`email=kb@example.com` 被拒绝（HTTP 422 “Please use your own email address”），改用 OpenAlex。
- WebSearch / WebFetch：官方落地页、机构库、arXiv、NeurIPS、OSTI、NREL、Linköping ECP、化工学报官网。
- arXiv API：作者与期刊 DOI 核对。

## 关键结果
1. **Celik 2008 GCI**：ASME Digital Collection 期刊页与 PDF 均被 Cloudflare 拦截（403）；找到 ASME 官网自托管的 `JFENumAccuracy.pdf`（asme.org，15 页 = 1993 政策十条 + 2008 程序稿），合法下载。已抽取 Eq.(1)–(7)、附录 A，并用独立实现复算 Table 1（p=1.537/0.752/1.508，GCI=2.17%/1.07%/0.47%，与原表一致）。
2. **NASA**：NPARC 教程保存为 HTML（公式是 GIF 图片，未本地化）；NASA TMR 的 Summary of Uncertainty Procedure（2018）下载自 tmbwg.github.io（TMR 迁移地址），给出 p 的低/高限幅与振荡分支。
3. **Eça & Hoekstra 2014**：出版商 closed access；共同作者机构 MARIN 官网公开托管排版版 PDF，已下载，标 redistributable=false。
4. **Roache 1994/1997、Oberkampf & Roy 2010**：OpenAlex closed，仅登记 paywalled。
5. **PG 物性**：Sun & Teja 2004 付费，但 NIST TRC ThermoML 提供全部点值 XML（已下载为数据集）；Melinder 2007 KTH 博士论文 DiVA 开放全文（已下载）；Deng & Zhang（IJT 2021，arXiv 预印本已下载）导热系数；蒋晓煜等 2024《化工学报》MDSC 比热（已下载）；Khattab（Arabian J Chem，CC BY-NC-ND）ScienceDirect 对脚本 403，登记 metadata_only；Bohne 1984 经 Crossref 核实是 **乙二醇**-水，不是丙二醇。
6. **数字孪生/控制**：ExaDigiT（arXiv 2410.05133）、Modelica 会议 Part 1/Part 2（CC BY 4.0）、Jadhav & Liu 2026（arXiv 2603.01198）、Sun 2024 Scientific Data（Frontier 数据集论文）、Lazic 2018 NeurIPS MPC、Chen 2020 TCPMT 深度显式 MPC（A*STAR 机构库接受稿）、Fu 2019 Modelica Buildings 数据中心包（OSTI 接受稿）、NREL Asetek RackCDU（2014）与 Aquila 固定冷板（2019）技术报告。
7. **中文**：《化工学报》官网开放 PDF，下载 3 篇（刘帆 2024 歧管射流微通道、杨磊 2026 液冷综述、蒋晓煜 2024 比热）；唐永乐 2022《制冷》仅元数据（第三方导航页）。

## 失败 / 拦截
- ASME Digital Collection：Cloudflare 403（期刊页、PDF 都是）。
- ScienceDirect（Khattab）：403。
- OpenReview（Cam 2025 PINN）：403。
- figshare（Frontier HPC & Facility Data.xlsx，CC BY 4.0，20 MB）：`ndownloader.figshare.com` 返回 202，`figshare.com/ndownloader` 返回 403（机器人防护）→ pending_user。
- escholarship.org（Fu 2019）：403，改走 OSTI purl 成功。
- cjche.cip.com.cn（2003 年 1,2-丙二醇水溶液超额体积/粘度/热容）：SSL EOF + WebFetch 超时，未登记（作者未核实）。

## 下载日志说明
- `downloads.log.jsonl` 中有一条 `pap-2026-unknown-frontier-dt-cooling-opt` 记录：首次下载时第一作者未确认，随后以正确 id `pap-2026-jadhav-frontier-dt-cooling-opt` 重新下载（sha256 相同 b84351bf…），并删除了 unknown 文件。该陈旧日志行未删除（不修改已有文件），汇总时请忽略。
- `pap-0000-*` 两条 NASA 网页/文档：下载时年份未定，id 用 0000；条目 year 字段分别为 2021（页面最后更新）与 2018（文档落款）。

## 未做 / 留给后续
- ASME V&V 20 由其他智能体负责，未登记。
- Dow/ASHRAE 手册由其他智能体负责。
- 未改动 W\docs\ 下的 PG25 报告。
- 知网/万方/维普需登录，未系统检索“微射流冷板 实验”“液冷 CDU 建模”“冷板 GCI”的付费中文文献；可在机构账号下补检。
- 可补：GB200/GB300 机柜实测热特性公开资料（本轮未找到同行评审/实验室来源）；POD/Galerkin 冷板 ROM 的 arXiv 文献（只登记了 Curl & Hu 2026）。

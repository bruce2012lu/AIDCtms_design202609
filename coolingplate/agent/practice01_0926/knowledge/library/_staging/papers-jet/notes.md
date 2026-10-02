# papers-jet 检索日志（2026-10-02）

## 结果
- 登记 34 条（entries.json）：已下载 10、开放获取但需用户在浏览器下载 7（pending_user）、付费 17（paywalled，含 1 本书、1 项标准）。
- 下载全部通过 `tools/fetch.py` 的 `fetch()`（文件头校验、sha256、写入 downloads.log.jsonl）。

## 方法
1. Crossref `query.bibliographic` 核对标题、作者、卷期、DOI（脚本：`lookup.py`）。
2. OA 定位：Unpaywall API 拒绝 `kb@example.com`（HTTP 422，要求真实邮箱），未擅自使用他人邮箱；改用 OpenAlex `locations`（数据源含 Unpaywall）。
3. WebSearch 查找机构库与作者主页版本：Purdue e-Pubs（CTRC）、MIT Lienhard 主页、KU Leuven Lirias、TCD TARA、Penn State ScholarSphere、s-pack.org（Tiwei Wei 实验室主页，Purdue）。
4. 全文用 PyMuPDF 抽取（`extract.py` → `txt/`）；排版有歧义的公式渲染为 PNG 后人工核对（`img_*.png`）。

## 合法来源说明
- HAL（hal-00511424）有 Anubis 反爬页，只拦浏览器 UA。`fetch_honest_ua.py` 仅把 fetch.py 的 UA 换成如实标明身份的工具 UA，其余校验逻辑不变；未绕过任何验证码或登录。
- s-pack.org 是作者（Tiwei Wei）实验室主页的论文张贴页，部分 PDF 为出版社排版版（带 IEEE/Elsevier 版权），已全部标为 redistributable=false。
- 没有使用任何影子图书馆；docslib.org、kiphub 等聚合站检索中出现过，但未采用。

## 被拦截 / 失败
| 来源 | 现象 | 处理 |
|---|---|---|
| docs.lib.purdue.edu（Li&Garimella 2001、Lee&Garimella 2005/2006、Rau&Garimella 2013） | 浏览器 UA 和诚实 UA 都返回 HTTP 403 | pending_user；关联式取自 WebSearch 抓到的全文文本（负号丢失，已标注待核） |
| tara.tcd.ie（Whelan 2012） | 403 | pending_user |
| scholarsphere.psu.edu（Hobby 2020） | 返回 HTML 中间页 / SSL EOF | pending_user |
| tandfonline.com（Natarajan 2007，OpenAlex 标 OA） | 403 | pending_user |
| mdpi.com（Fluids 2019） | 403 | 改用 s-pack.org 副本（CC-BY） |
| Lienhard 1995 | 扫描 PDF，无文字层 | 已下载，公式未提取，需 OCR |

## 已核对的关键事实
- Wei 2022 Eq.(19)(20)：p.11，页面图像核对；Eq.(20) 中“0.37 (H/L) 0.15”按 (H/L)^0.15 解读，存在歧义。
- Robinson & Schnitzler 2007 关联式：Whelan 2009 录用稿 p.10 Eq.(1)(2)，页面图像核对；Nu_L 以加热面 L_c=D/2=15.75 mm 定义。
- Martin 1977 适用范围：Wei 2022 Table 1 p.3 列 2000<Re<100000、2≤H/D≤12、指数 0.67；f 范围 0.004~0.04 与公式本体来自 Incropera 教科书转引，未对照原文。
- Li & Garimella 2001 Table 1：Liquids Eq.(8) 系数 1.409、Re^0.497、Pr^0.444、l/d 0.058、D_e/d 0.272（符号缺失）。
- Lee & Garimella 2006 Eq.(12)(13) 系数取得，符号缺失。

## 待办
- 用户在浏览器下载 7 篇 pending_user，放入 files/papers/<id>.pdf 后补 sha256，并核对 Li&Garimella、Lee&Garimella 公式的正负号。
- 数字化 Wei 2022 Fig.14/15、Whelan 2009 Fig.3/4 中的实测点。
- Lienhard 1995 做 OCR。

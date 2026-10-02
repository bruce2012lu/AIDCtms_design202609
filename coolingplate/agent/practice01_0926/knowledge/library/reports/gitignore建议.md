# .gitignore 建议（未落地，需人工确认）

日期：2026-10-02。本轮没有创建或修改任何 `.gitignore`，也没有 git commit。

## 为什么要加

- 远端 `origin = https://github.com/bruce2012lu/agents2026.git` 的可见性未知。若是公开仓库，提交厂商受限文档、arXiv 全文或付费标准就构成再分发。
- `files/` 里厂商 PDF 与手册都是“官网公开、版权保留”，公开下载不等于允许再分发。
- 体积：本轮下载约 100 个文件，单个最大约 20 MB 级（CDA 手册 22.6 MB）。`derived/` 里的图片会再放大体积。
- 现状提醒：`agents/AIDCtms/coolingplate/papers/pdfs/` 下 12 份 PDF 已被 git 跟踪（`git ls-files` 可见）。其中 7 份 MDPI CC-BY 可以保留；3 份 arXiv、1 份 Element Six、1 份 SciOpen 中文期刊版权不明，若仓库公开，建议用 `git rm --cached` 移出跟踪（由人执行）。

## 建议内容

写到 `agents/AIDCtms/coolingplate/agent/practice01_0926/knowledge/library/.gitignore`：

```gitignore
# 原件与派生物默认不入库（版权与体积）
files/**
derived/**
index/
_staging/**/txt/
_staging/scratch/
*.part

# 允许入库的开放许可原件：逐个放行（CC-BY、美国政府作品、专利公开文本）
!files/
!files/*/
!files/patents/*.pdf
!files/datasets/dat-2023-nist-water-isobar-1atm.txt
# 例：!files/papers/pap-2021-wei-microjet-correlations-feed-drain.pdf   （确认为 CC-BY 后再加）
```

保留入库：`schema/`、`registry/`（登记册、引用、基准，只含元数据与 sha256）、`cards/`（本库自写的摘要卡片，引用的公式和少量数据点属合理引用）、`reports/`、`tools/`、`tests/`、`知识库架构_v0.1.md`、`README.md`、`_staging/*/entries.json` 与 `notes.md`。

`registry/entries.json` 记了每个文件的 sha256 与 source_url，所以原件不入库也能在另一台机器上用 `fetch.py` 按原地址重新下载并校验一致。

## 专利是否放行

专利公开文本属于公开政府文件，再分发一般没有版权障碍（个别国家对图片另有规定）。30 份左右 PDF 体积可接受。若担心仓库体积，也可以一并忽略，只留 `registry/` 里的号码与链接。

## 付费资料

用户合法购买或登录下载的标准、手册（ASHRAE、ASME、JEDEC、IIR 等）只放本机 `files/`，**绝不入库**。登记时 `access.redistributable=false`，上面的规则会自动忽略。

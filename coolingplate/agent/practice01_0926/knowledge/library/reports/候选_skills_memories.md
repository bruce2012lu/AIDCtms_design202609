# 候选 skills 与 memories（candidate，未落地）

日期：2026-10-02。按平台约定：本轮不写正式 memory、不安装或暂存 skill。下面全部是草案，采纳需人工确认。skill 走第①道闸门（先进 `platform/shared/skills/_staging/`，确认后登记 `_meta/skill-registry.json`）；memory 写入 `memory/semantic/` 时需带 `confidence / valid_until / last_verified`。

## 候选 skills

### 1. `kb-ingest`（建议：cp-design 私有技能 `skills/kb-ingest/SKILL.md`）

- 触发：要把一篇论文、手册、标准、厂商文档或专利放进冷板知识库时。
- 步骤：判断合法可得性 → `tools/fetch.py` 下载（或只登记 pending_user）→ 在 `_staging/<主题>/entries.json` 写条目（必须有 trust_level、stages、locator）→ `kb.py merge --write` → `kb.py ingest --id` → `kb.py index` → 写 `cards/<id>.md`。
- 红线：不用影子图书馆；付费件只登记；key_data 必须对照原页写 locator，`verified_from` 如实填写。
- 理由：本轮 5 个检索子任务都在重复这套流程，固化后可减少格式漂移。

### 2. `kb-cite`（建议：cp-design 私有技能）

- 触发：一维工具、CFD 边界条件、设计报告要写入任何外部数值或公式时。
- 步骤：`kb.py search` 找来源 → 读原页 → `kb.py cite` 登记 → 代码常量旁写 `# kb:cit-NNNN`，报告脚注写条目 id + locator。
- 闸门：L5/L6 不能作 benchmark；locator 为空拒绝。

### 3. `cfd-gci`（建议：cp-design 私有技能，挂在 `cfd-loop` 之后）

- 触发：任何要发表的 Fluent 结果（TIM 面温度、压降、热阻）。
- 步骤：至少三套网格，r > 1.3 → `tools/gci.py --phi φ1 φ2 φ3 --N N1 N2 N3` → 报告 p、φ_ext、GCI_fine、渐近比；振荡收敛单独说明。
- 理由：UC-01b 现在只有一套收敛网格（m425，426 万 HEXA）和一套在算的 12 层网格，无法给出离散不确定度；ASME V&V 20 与 Celik 2008 都要求报告。

### 4. 平台层共享候选 `literature-triage`（建议：`platform/shared/skills/_staging/`）

- 内容：可信度 L1–L6 判定表、合法来源白名单与黑名单、`verified_from` 规则。
- 理由：其他领域智能体（thermal-management、ev-research）的文献工作也需要同一套分级；可作为 `librarian` 的入库前质量检查。

## 候选 memories（semantic 草案）

### A. `memory/semantic/kb-library.md`

```markdown
---
confidence: 0.8
valid_until: 2027-03-31
last_verified: 2026-10-02
expired: false
---

# 冷板知识库 v0.1

外部来源统一登记在 `knowledge/library/registry/entries.json`，可信度 L1–L6，内部报告是 L5。
设计数值引用外部来源时用 `tools/kb.py cite` 登记，locator 至少到页码。
检索：`tools/kb.py search`（FTS5 trigram + BM25，中英文都可）。原件与派生物默认不入 git。
```

### B. `memory/semantic/jet-correlation-applicability.md`

```markdown
---
confidence: 0.7
valid_until: 2027-03-31
last_verified: 2026-10-02
expired: false
---

# 射流关联式适用性

本项目 GPU 区：D 0.40/0.50 mm，216 孔，Sx×Sy 3.0×2.4 mm，H 2.0 mm，PG25 Re 约 420–570（水基线 478），Pr 约 10（按内部物性，待 PG25 物性报告确认）。
Martin 1977 阵列式要求 Re ≥ 2000，不适用（与 v2.0/v2.1 结论一致，有外部来源支持）。
最接近的是 Wei et al. 2021 IJHMT 182:121865 Eq.(19)：交替进排液微射流，32 ≤ Re ≤ 2048，0.01 ≤ d_i/L ≤ 0.4，0.01 ≤ H/L ≤ 0.4，Pr 固定 7.56，±30%。
本项目 d_i/L ≈ 0.15–0.19 在内，H/L ≈ 0.75 在外（原文称 0.3–1 之间 H/L 影响很小），Pr 在外，出口拓扑不同（短槽就近抽走 vs 排液孔）。
因此它只能作量级交叉核对，不能替代 CFD + TTV 实测。
```

### C. `memory/semantic/velocity-limit-source.md`

```markdown
---
confidence: 0.75
valid_until: 2027-03-31
last_verified: 2026-10-02
expired: false
---

# 铜件流速上限的外部来源

项目限值：孔速 ≤ 2.0 m/s，HBM 近壁 ≤ 0.80 m/s。公开权威参照只有 CDA Copper Tube Handbook p.15：
冷水 ≤ 8 ft/s（2.44 m/s），60 °C 以下热水 ≤ 5 ft/s（1.52 m/s），长期 > 60 °C 为 2–3 ft/s，小管还应更低。
它针对建筑管道，不是短孔射流，只作量级参照。40 °C PG25 属热水档，0.40 mm 孔在 2.6 L/min 时 1.596 m/s 超过 1.52 m/s。
```

### D. episodic 草案 `memory/episodic/2026-10-02-kb-v0-1.json`

```json
{"date": "2026-10-02", "task": "知识库 v0.1 建设", "confidence": 0.8, "valid_until": "2027-03-31",
 "last_verified": "2026-10-02", "expired": false,
 "done": ["架构文档与 schema", "kb.py / fetch.py / gci.py 与测试", "5 主题并行检索登记", "试点知识卡片", "验证基准清单", "内部数值对照"],
 "open": ["付费标准与手册待用户获取", "向量检索依赖待审批", "kb.* MCP 接口未接入 server.py", "UC-01b 三套网格 GCI"]}
```

`memory/index.json` 不改；若采纳 A–C，再把路径加入其 `semantic` 列表。

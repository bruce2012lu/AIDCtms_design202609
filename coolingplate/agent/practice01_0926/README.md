# cp-design 怎么接着用

设计台和 MCP 都在这个目录。几何规则仍然是 `cad/coldplate`，这里只是把它变成可调用的智能体。

## 打开界面

在冷板根目录执行：

```powershell
.\agent\practice01_0926\启动冷板设计台.ps1
```

浏览器打开 http://127.0.0.1:8765/ 。CAD 页可以改孔径、节距和流量，先校验规则，确认后再导出。导出在 `agent/practice01_0926/runs/`，冻结参数集不会被改写。

## 接到 Cursor

仓库根 `.mcp.json` 已登记 `cp-design`。工具：`kb_catalog`、`memory_list`、`cad_tracks`、`cad_inspect`、`cad_build`。

对话里做冷板几何时，先读 `agent/practice01_0926/agent.md` 和 `agent/practice01_0926/skills/cad-loop/SKILL.md`。

## 目录

| 路径 | 内容 |
|---|---|
| `agent.md` | 角色与边界 |
| `memory/` | 画像、语义记忆、情景记忆 |
| `knowledge/` | 知识库目录、四条 CAD 轨道、内核缺口 |
| `skills/` | 设计循环、CAD 循环、CFD 循环 |
| `mcp/server.py` | MCP stdio 与设计台 HTTP |
| `ui/` | HTML 设计台 |
| `软件界面方案.md` | 独立软件下一步 |
| `cycle-20260926/` | 这一轮一维、CAD、单孔分析和结构装配报告 |

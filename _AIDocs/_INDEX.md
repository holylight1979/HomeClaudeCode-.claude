# MyClaudeCode (.claude) — AI 分析文件索引

> 本資料夾記錄 `~/.claude` 自訂擴充系統的架構與演進。
> 最近更新：2026-03-02

---

## 文件清單

| # | 文件名稱 | 說明 |
|---|---------|------|
| 1 | Architecture.md | 系統架構總覽：原子記憶 + Workflow Guardian + hooks |
| 2 | _CHANGELOG.md | 變更記錄 |

---

## 架構一句話摘要

基於 Claude Code hooks 事件驅動的工作流監督系統，搭配兩層原子記憶管理跨 session 知識，透過 MCP server 提供 Dashboard 監控與工具介面。

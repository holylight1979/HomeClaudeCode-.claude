# MyClaudeCode (.claude) — AI 分析文件索引

> 本資料夾記錄 `~/.claude` 自訂擴充系統的架構與演進。
> 最近更新：2026-03-04

---

## 文件清單

| # | 文件名稱 | 說明 |
|---|---------|------|
| 1 | Architecture.md | 系統架構總覽：原子記憶 + Workflow Guardian + hooks |
| 2 | AtomicMemory-v2.1-Plan.md | v2.1 缺陷研究與修補計畫（7 大缺陷 + 比較矩陣 + schema + 路線圖） |
| 3 | _CHANGELOG.md | 變更記錄 |
| 4 | ../README.md | 完整運作知識庫 + 7 階段流程圖（GitHub 入口） |

---

## 架構一句話摘要

基於 Claude Code hooks 事件驅動的工作流監督系統，搭配兩層原子記憶管理跨 session 知識，透過 MCP server 提供 Dashboard 監控與工具介面。

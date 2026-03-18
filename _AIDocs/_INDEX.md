# MyClaudeCode (.claude) — AI 分析文件索引

> 本資料夾記錄 `~/.claude` 自訂擴充系統的架構與演進。
> 最近更新：2026-03-13

---

## 文件清單

| # | 文件名稱 | 說明 |
|---|---------|------|
| 1 | Architecture.md | 系統架構總覽：原子記憶 V2.12 + Workflow Guardian + Wisdom Engine + hooks |
| 2 | Project_File_Tree.md | 完整目錄結構 |
| 3 | _CHANGELOG.md | 變更記錄（最近 ~8 筆） |
| 4 | _CHANGELOG_ARCHIVE.md | 變更記錄封存 |
| 5 | ../README.md | 完整運作知識庫 + 7 階段流程圖（GitHub 入口） |
| 6 | DocIndex-System.md | 全 76 檔系統索引（啟動鏈 + Hook + Skill + Tool + Memory） |

---

## 架構一句話摘要

基於 Claude Code hooks 事件驅動的工作流監督系統，搭配雙 LLM（Claude + Ollama qwen3/qwen3.5）原子記憶管理跨 session 知識。V2.12：Dual-Backend（rdchat+local）、Wisdom Engine、衝突偵測、rules/ 模組化、Fix Escalation Protocol、76 檔系統。

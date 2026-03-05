# Claude Code 全域設定 — AI 分析文件索引

> 本資料夾包含由 AI 輔助產出的 Claude Code 全域設定分析文件。
> 適用範圍：`C:\Users\holyl\.claude\`（家用電腦）
> GitHub: `holylight1979/MyClaudeCode-Home-.claude`
> 最近更新：2026-03-05

---

## 文件清單

| # | 文件名稱 | 說明 |
|---|---------|------|
| 1 | Project_File_Tree.md | 目錄結構摘要 |
| 2 | Architecture.md | 核心架構：hooks、skills、memory 系統 |

---

## 架構一句話摘要

Claude Code 全域設定，包含工作流引擎指令（CLAUDE.md）、7 個 hook events（SessionStart/UserPromptSubmit/PreToolUse/PostToolUse/PreCompact/Stop/SessionEnd）、三個自訂 skills、原子記憶 V2.4（Hybrid RECALL + 回應捕獲 + 跨 Session 鞏固）、以及多個專案的原子記憶。

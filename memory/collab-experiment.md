# AI 自主開發實驗協作模式

- Scope: global
- Confidence: [觀]
- Trigger: AI自主開發, AI自主, Sprint自主, 協作實驗, harness agent, subagent協作, PM角色, AI當開發, 啟動協作實驗, 協作模式
- Last-used: 2026-04-02
- Confirmations: 1

## 知識

- [觀] 完整教程文件位置：`~/.claude/collab/AI-Human-Collaboration-Guide.md`
- [觀] 角色分工：Wells = PM（需求/方向/驗收）；Claude = 開發者（目標搜尋/subagent 調度/實作/測試）
- [觀] 標準啟動語：「Sprint X 開始，目標：{目標說明}，你自主搜尋目標後回報我再開始」
- [觀] 溝通頻道：Discord，Wells 設定的 PM 頻道（本次 Sprint 2：1485277764205547630）
- [觀] 核心規則：每個目標開工前先回報計畫（幾個 agent、分別做什麼） → 5+ agent（設計/安全/開發/品管/測試） → 完成後出 MD 報告
- [觀] 安全邊際：綠區自主執行，黃區告知後執行，紅區（外部 API 異動/刪除重要檔案）必須等人類確認
- [觀] 測試頻道：1484061896217858178（可在此頻道叫另一個 bot 做實機測試）
- [觀] 協作知識庫路徑：`~/.claude/collab/`（版控於 HomeClaudeCode-.claude）

## Sprint 3 候選目標（backlog）

- [觀] `session:end` 從未 emit → `extractFullScan` / `evaluatePromotions` 從未執行，全量掃描死路
- [觀] `consolidate()` 未定時呼叫 → atoms 永遠停在 [臨]，無法晉升 [觀]
- [觀] Ollama 萃取耗時 ~60s（qwen3:14b）→ 高流量下排隊積累風險

## 行動

- 收到「啟動 Sprint X 自主開發」類請求 → 讀 `~/.claude/collab/AI-Human-Collaboration-Guide.md` 確認完整流程
- 開工前必須先向 Wells 回報目標清單 + agent 分工計畫，不可直接動手
- Sprint 3 開始時，優先從上方 backlog 選目標

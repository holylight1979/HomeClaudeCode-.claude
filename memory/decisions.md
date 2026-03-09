# 全域決策

- Scope: global
- Confidence: [固]
- Trigger: 全域決策, 工具, 工作流, workflow, guardian, hooks, MCP, 記憶系統
- Last-used: 2026-03-09
- Confirmations: 52
- Type: decision

## 知識

### 核心架構
- [固] 原子記憶 V2.5：Hybrid RECALL + Ranked Search + Keyword Boost + Self-healing Cache + 回應捕獲 + 跨 Session 鞏固 + Workflow Guardian
- [固] 雙 LLM：Claude Code（雲端決策）+ Ollama qwen3（本地語意處理）
- [固] 7 hook 事件全由 workflow-guardian.py 統一處理（SessionStart/UserPromptSubmit/PostToolUse/PreCompact/Stop/SessionEnd + PreToolUse 由 inbox-check.js）

### 記憶檢索管線（V2.5）
- [固] UserPromptSubmit: Intent 分類（qwen3:1.7b）→ Trigger 匹配 → Vector Search → Keyword Boost → Ranked Merge → additionalContext
- [固] V2.5 Hybrid Search: 向量結果疊加 keyword matching boost（大寫詞、引號短語、中文專有名詞），雙命中 +0.1，keyword 救回 +0.05
- [固] V2.5 Self-healing Cache: ChromaDB collection reference 快取 + 失效自動 invalidate + retry；連續失敗計數器超閾值升級警告
- [固] 降級順序：Ollama 不可用 → 純 keyword | Vector Service 掛 → graceful fallback
- [固] 索引 4 層：global → project → extra:openclaw → episodic（向量發現）

### 回應捕獲（V2.4）
- [固] 逐輪萃取：UserPromptSubmit 非同步讀取上一輪 assistant 回應，qwen3:1.7b 萃取知識（≤3000 chars, 2 items）
- [固] SessionEnd 補漏：同步掃描全 transcript（≤20000 chars, 5 items）
- [固] 萃取結果一律 [臨]，經跨 Session 鞏固後自動晉升

### 跨 Session 鞏固（V2.4 Phase 3）
- [固] SessionEnd 時對 knowledge_queue 做向量搜尋（min_score 0.75）
- [固] 2+ sessions 命中 → 自動晉升 [臨]→[觀]；4+ sessions → 建議晉升 [觀]→[固]
- [固] 結果寫入 episodic atom「跨 Session 觀察」段落

### Episodic atom
- [固] SessionEnd 自動生成，TTL 24d，存放於 memory/episodic/（不進 git）
- [固] 門檻：modified_files ≥ 1 且 session 時長 ≥ 2 分鐘
- [固] 不列入 MEMORY.md index，靠 vector search 發現

### 基礎設施
- [固] Vector Service @ localhost:3849 | Dashboard @ localhost:3848
- [固] Ollama models: qwen3-embedding:0.6b（embedding）+ qwen3:1.7b（萃取/分類）
- [固] Vector DB: ChromaDB（i7-3770 不支援 AVX2，LanceDB 不適用）
- [固] MCP 傳輸格式：JSONL，protocolVersion 2025-11-25

### 主動續航（Session Continuity）
- [固] **段落完成即存**：完成一個段落的動作（不論驗證是否通過）前，立即將進度寫入原子記憶
- [固] **Token 上限預警存檔**：判斷 session 快碰觸 token 上限時，優先將當前工作狀態寫入 atom（任務名稱、進度、下一步、阻塞點）
- [固] **重試追蹤**：反覆修正/重試的場景，記錄重試次數、每次調整的重點、成功/失敗原因
- [固] **執行中項目清單**：以 atom 記錄「目前執行中的項目」，新 session 首次發話時主動檢查是否有未完成項目
- [固] **跨 Session 接續**：不論跨越多少 session，透過原子記憶確保接續上下文完整。項目完成或確定中斷時，標記為已完成/已中斷
- [固] **向量庫同步**：寫入/更新 atom 時，同步更新向量記憶庫（確保新 session 的語意搜尋能找到）

### 歷史決策
- [固] 記憶檢索統一用 Python，已移除 Node.js memory-v2（2026-03-05 退役）
- [固] Stop hook 只保留 Guardian 閘門，移除 Discord 通知
- [固] OpenClaw workspace atoms 透過 additional_atom_dirs 整合（extra:openclaw 層，5 atoms）

## 行動

- 記憶寫入走 write-gate 品質閘門
- 向量搜尋 fallback 順序：Ollama → sentence-transformers → keyword
- Guardian 閘門最多阻止 2 次，第 3 次強制放行

## 演化日誌

- 2026-03-05: 建立 README.md（哲學/Token比較/流程圖/大型專案使用法）+ Install-forAI.md 安裝指南
- 2026-03-05: V2.3 合併安裝，從公司版遷移核心工具鏈到家用電腦
- 2026-03-05: LanceDB → ChromaDB（i7-3770 不支援 AVX2，LanceDB search crash）
- 2026-03-05: embedding model 指定 qwen3-embedding:0.6b（避免 latest 4.7GB 版 timeout）
- 2026-03-05: search_min_score 從 0.65 降至 0.45（0.6b 小模型 score 普遍較低）
- 2026-03-05: OpenClaw atoms 整合（additional_atom_dirs），Node.js memory-v2 退役
- 2026-03-05: V2.3 全面升級 OpenClaw Phase 1+2 完成 — MEMORY.md 3欄格式修正、root CLAUDE.md、4個大師級 atom
- 2026-03-05: V2.4 Phase 1+2（回應捕獲）+ Phase 3（跨 Session 鞏固）上線
- 2026-03-05: SessionEnd timeout 5→30s，修復 episodic atom 不生成 bug
- 2026-03-05: episodic 移入 memory/episodic/（不進 git），hardware.md 從 git 移除
- 2026-03-05: .gitignore 整理 — 只保留 OpenClaw project memory，排除 session-env/、.claude/
- 2026-03-05: fix: workflow-guardian stdout/stderr 強制 UTF-8（Windows cp950 導致中文亂碼）
- 2026-03-06: V2.5 Hybrid Search Keyword Boost（專有名詞召回率提升）+ Self-healing Collection Cache（ChromaDB 失效自動恢復）
- 2026-03-09: [固] 主動續航（Session Continuity）— 段落完成即存、Token 上限預警存檔、重試追蹤、執行中項目清單、跨 Session 接續

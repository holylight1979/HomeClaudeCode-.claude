# Claude Code Custom Extensions

> Claude Code hooks + MCP + Atomic Memory V2.2 = 自動化工作流監督 & 跨 session 知識管理（含向量語意搜尋、Session Awareness、自動晉升）

---

## Overview

這是一套 Claude Code 的自訂擴充系統，核心解決兩個問題：

1. **工作流監督** — Claude 容易忘記同步（git commit、更新文件），這套系統自動追蹤修改、提醒同步、阻止未完成就結束
2. **跨 session 記憶** — Claude 每次新對話都是白紙一張，原子記憶 V2.2 讓知識在 sessions 之間延續

**技術架構**：
- **Hooks**（Python）— 6 個生命週期事件的統一處理器
- **MCP Server**（Node.js）— JSON-RPC stdio + HTTP Dashboard（5 tabs）
- **Atomic Memory V2.2** — Hybrid RECALL + Ranked Search + Write Gate + Session Awareness + Proactive Classification + Auto-promotion

---

## 7-Phase Workflow Lifecycle

每個 Claude Code session 的完整生命週期：

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  Phase 1: BOOT（啟動初始化）                                          │
│  Trigger: SessionStart hook                                          │
│  ├─ 新 session → 建立 state, 解析全域+專案 MEMORY.md atom index       │
│  ├─ resume/compact → 恢復 state, 清空 injected_atoms, 注入摘要       │
│  └─ 自動啟動 Memory Vector Service daemon（若未運行）                  │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 2: RECALL（記憶召回）★ V2.2 Hybrid                            │
│  Trigger: UserPromptSubmit hook（每輪）                               │
│  ├─ [1] Keyword match: prompt vs atom Trigger 關鍵詞（~10ms）        │
│  ├─ [2] Intent classification: rule-based 分類（~1ms）               │
│  │       → debug / build / design / recall / general                 │
│  ├─ [3] Ranked search: HTTP → Vector Service /search/ranked          │
│  │       → 5 因子加權：Semantic·Recency·IntentBoost·Confidence·Confirm│
│  ├─ [4] Merge: keyword + semantic results（去重）                     │
│  ├─ [5] 在 token budget 內載入 atom 全文或摘要                        │
│  ├─ [6] Session context injection（首輪 only）                        │
│  │       → /search/episodic → 注入過往 session 摘要（~400ms）         │
│  ├─ [7] Proactive classification: 跨 session 模式偵測 + 建議          │
│  └─ [8] Auto-promotion: [臨] Confirmations≥2 → 自動晉升 [觀]         │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 3: TRACK（修改追蹤）                                           │
│  Trigger: PostToolUse hook（Edit|Write）                              │
│  ├─ 靜默記錄 file_path + tool + timestamp                            │
│  ├─ 設定 sync_pending = true                                         │
│  └─ ★ 若修改的是 atom 檔 → 觸發增量向量索引                          │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 4: REMIND（同步提醒）                                          │
│  Trigger: UserPromptSubmit hook（週期性）                              │
│  ├─ 每 N 輪提醒一次未同步修改（max_reminders 上限）                    │
│  └─ 偵測 sync 關鍵詞時顯示完整 sync context                          │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 5: COMPACT（壓縮保護）                                         │
│  Trigger: PreCompact hook                                             │
│  ├─ 快照 state（timestamp）                                          │
│  └─ Resume 時由 Phase 1 恢復 context + 重新注入 atoms                 │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 6: GATE（結束閘門）                                            │
│  Trigger: Stop hook                                                   │
│  ├─ 修改 ≥ min_files_to_block → BLOCK（最多 N 次）                   │
│  ├─ phase=done/muted → ALLOW                                         │
│  └─ 阻止 N 次後強制放行（anti-loop）                                  │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 7: SYNC（同步執行）                                            │
│  Trigger: 手動（Claude + 使用者確認）                                 │
│  ├─ Write Gate 品質檢查 + 去重（auto_threshold=0.5）                  │
│  ├─ 更新 _AIDocs/_CHANGELOG.md                                       │
│  ├─ 更新 atom 檔（知識段落 + Last-used + Confirmations++）            │
│  ├─ Episodic atom 自動生成（修改≥1 檔 + session≥2min）               │
│  │   → episodic-{YYYYMMDD}-{slug}.md, TTL=24d, 不列 MEMORY.md 索引  │
│  ├─ workflow_signal("sync_completed") → 清空 queue + phase=done       │
│  └─ git commit + push                                                │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Features

### Workflow Guardian
- **自動追蹤修改** — Edit/Write 操作靜默記錄，不干擾工作
- **Stop 閘門** — 有未同步修改時阻止 Claude 結束，防止遺忘
- **Anti-loop 保護** — 最多阻止 N 次後強制放行，不會卡死
- **Mute 靜音** — 不想被打擾時可以靜音提醒
- **Dashboard** — `http://127.0.0.1:3848` 即時監控所有 sessions（5 tabs）
- **多實例 Heartbeat** — 多個 VS Code 視窗時自動接管 Dashboard port
- **Session ID Prefix Match** — 用截短 ID（前 8 碼）即可操作

### Atomic Memory V2
- **兩層架構** — 全域 atoms（跨專案）+ 專案 atoms（專案綁定）
- **Hybrid RECALL** — Keyword Trigger + Vector Semantic Search 並行
- **Vector Service** — LanceDB + Ollama qwen3-embedding，常駐 HTTP daemon @ port 3849
- **Embedding 雙軌** — Ollama qwen3-embedding（主力）/ sentence-transformers bge-m3（fallback）
- **本地 LLM** — qwen3:1.7b via Ollama：查詢改寫、Re-ranking、知識萃取
- **段落級索引** — atom 中每個知識點獨立向量化，搜尋精度高於整檔比對
- **增量索引** — atom 修改時自動觸發，只重建變動的檔案（hash 比對）
- **Graceful fallback** — daemon/Ollama 未啟動時自動退化為純 keyword 模式
- **Token Budget** — 根據 prompt 複雜度自動調整載入量（1.5~5K tokens）
- **三級分類** — `[固]` 確認長期有效、`[觀]` 可能演化、`[臨]` 單次決策
- **Last-used 自動刷新** — Atom 被載入時自動更新使用日期
- **Compact 恢復** — Context 壓縮後自動重新注入 atoms

### v2.1 — Quality & Governance
- **Write Gate** — 寫入前品質評分 + 向量去重（auto_threshold=0.5, dedup_score=0.80）
- **Conflict Detection** — LLM 語意比對 AGREE/CONTRADICT/EXTEND/UNRELATED（離線路徑）
- **Intent Classification** — Rule-based 零 LLM 開銷（debug/build/design/recall/general）
- **Ranked Search** — `/search/ranked` 五因子加權：0.45 Semantic + 0.15 Recency + 0.20 IntentBoost + 0.10 Confidence + 0.10 Confirmation
- **Delete Propagation** — `--delete`/`--purge` 全鏈清除（LanceDB + Related 引用 + MEMORY.md + re-index）
- **Type Decay Multipliers** — semantic=1.0, episodic=0.8, procedural=1.5
- **Audit Trail** — JSONL audit.log 追蹤 add/skip/decay/delete/purge/conflict_scan
- **E2E Testing** — 9 tests + 50-query benchmark（R@5=0.96, Hit@5=0.90, MRR=0.80）

### v2.2 — Session Awareness
- **Topic Tracker** — 累積 intent_distribution + keyword_signals，跨 session 辨識主題
- **Enhanced Episodic Atoms** — Session 結束自動生成 `episodic-{YYYYMMDD}-{slug}.md`，含 `## 摘要` + `## 關聯`。Type=episodic, [臨], TTL=24d，不寫入 MEMORY.md 索引（向量搜尋發現）
- **Session Start Context Injection** — 首輪 prompt 觸發 `/search/episodic`，注入 `[Session:Context]` 過往 session 摘要（~400ms）
- **Proactive Classification** — 跨 session 模式偵測 + episodic 遷移建議 + atom 建立提示
- **[臨]→[觀] Auto-promotion** — Confirmations ≥ 2 自動晉升（寫入檔案 + 通知）。[觀]→[固] 需人工確認（顯示 ⚡ hint）

---

## Quick Start

詳細安裝指南見 [Install-forAI.md](Install-forAI.md)（為 AI 設計的安裝手冊）。

### 核心元件

```
~/.claude/
├── CLAUDE.md                      # 工作流引擎指令（Claude 自動載入）
├── hooks/
│   └── workflow-guardian.py        # 6 事件 hook 處理器（V2.2 semantic search + session awareness）
├── tools/
│   ├── workflow-guardian-mcp/
│   │   └── server.js              # MCP server + HTTP Dashboard（5 tabs）
│   ├── memory-vector-service/     # V2 向量搜尋服務
│   │   ├── service.py             # HTTP daemon (port 3849)
│   │   ├── indexer.py             # 段落級 chunking + embedding + LanceDB
│   │   ├── searcher.py            # 語意搜尋 + ranked search + episodic search
│   │   ├── reranker.py            # LLM 查詢改寫 / re-ranking / 知識萃取
│   │   ├── config.py              # 設定管理
│   │   └── requirements.txt       # Python 依賴
│   ├── rag-engine.py              # V2 CLI 入口
│   ├── memory-audit.py            # 健檢 + decay + delete/purge
│   ├── memory-write-gate.py       # ★ v2.1 寫入品質閘門
│   ├── memory-conflict-detector.py # ★ v2.1 LLM 衝突偵測
│   ├── test-memory-v21.py         # ★ v2.1 E2E 測試（9 tests）
│   ├── eval-ranked-search.py      # ★ v2.1 搜尋品質評估（50 queries）
│   └── read-excel.py              # Excel 讀取工具
├── workflow/
│   ├── config.json                # Guardian + Vector Search + Write Gate + Decay 設定
│   └── state-*.json               # Session state（自動產生，不 commit）
├── memory/
│   ├── MEMORY.md                  # 全域 Atom Index
│   ├── preferences.md             # 使用者偏好 atom
│   ├── decisions.md               # 全域決策 atom
│   ├── rag-vector-plan.md         # RAG 架構設計 atom
│   ├── episodic-*.md              # ★ v2.2 自動生成 session 摘要（不在索引，向量搜尋發現）
│   ├── _vectordb/                 # LanceDB 向量資料庫 + audit.log（runtime data）
│   └── SPEC_Atomic_Memory_System.md  # 原子記憶 V2.1 規格書
├── commands/
│   └── init-project.md            # /init-project 自訂指令
├── _AIDocs/
│   ├── _INDEX.md                  # 文件索引
│   ├── Architecture.md            # 系統架構詳述
│   └── _CHANGELOG.md              # 變更記錄
└── settings.json                  # hooks 註冊 + 權限
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `workflow_status` | 查詢 session 狀態（省略 session_id → 列出全部） |
| `workflow_signal` | 發送信號：sync_started / sync_completed / reset / mute |
| `memory_queue_add` | 新增知識到 pending queue（classification: [固]/[觀]/[臨]） |
| `memory_queue_flush` | 標記 queue 已寫入 atom |

### Standalone Tools

| Tool | CLI | Description |
|------|-----|-------------|
| `memory-audit.py` | `python ~/.claude/tools/memory-audit.py` | 健檢（格式驗證、過期分析、晉升建議、重複偵測） |
| | `--enforce` | 自動淘汰過期 [臨] atoms，標記 [觀] pending-review |
| | `--delete <name>` | 刪除 atom（全鏈：LanceDB + Related + MEMORY.md） |
| | `--purge <name>` | 永久刪除（不移入 _distant/） |
| | `--compact-logs` | 壓縮 evolution logs（>10 筆合併） |
| `memory-write-gate.py` | `--content "..." [--classification "[觀]"]` | 寫入前品質 + 去重檢查 |
| `memory-conflict-detector.py` | `[--atom X] [--dry-run]` | LLM 衝突掃描（AGREE/CONTRADICT/EXTEND/UNRELATED） |
| `test-memory-v21.py` | `[-v] [--test NAME] [--json]` | E2E 測試（9 tests） |
| `eval-ranked-search.py` | `[--top-k 5] [--min-score 0.50]` | 50-query 搜尋品質評估 |
| `read-excel.py` | `<file> [--sheet N]` | Excel 讀取 |

### RAG Engine CLI

```bash
# 全量建索引
python ~/.claude/tools/rag-engine.py index

# 語意搜尋
python ~/.claude/tools/rag-engine.py search "查詢關鍵字"

# 增強搜尋（LLM 查詢改寫）
python ~/.claude/tools/rag-engine.py search "查詢" --enhanced

# 服務管理
python ~/.claude/tools/rag-engine.py status
python ~/.claude/tools/rag-engine.py health
python ~/.claude/tools/rag-engine.py start
python ~/.claude/tools/rag-engine.py stop
```

### Vector Service API（port 3849）

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/search?q=...&top_k=5&min_score=0.65` | 基本語意搜尋 |
| GET | `/search/ranked?q=...&intent=general` | ★ v2.1 Intent-aware 加權排序搜尋 |
| GET | `/search/episodic?q=...&top_k=3&min_score=0.35` | ★ v2.2 Episodic memory 搜尋 |
| GET | `/health` | 健康檢查 |
| GET | `/status` | 索引狀態（chunks 數、atom 數、最後索引時間） |
| POST | `/index` | 全量重建索引 |
| POST | `/index/incremental` | 增量索引（只重建有變動的 atom） |
| POST | `/search/enhanced` | LLM 查詢改寫 + 搜尋 |
| POST | `/rerank` | LLM re-ranking |
| POST | `/extract` | 知識萃取（文本 → 結構化 [固/觀/臨] 事實） |
| POST | `/reload` | 重新載入 config |
| POST | `/shutdown` | 停止 daemon |

---

## MCP Transport Format

Claude Code v2.x 使用 **JSONL** 傳輸格式（非 LSP Content-Length header）：

```
{"jsonrpc":"2.0","method":"initialize","params":{...}}\n
{"jsonrpc":"2.0","id":1,"result":{...}}\n
```

- protocolVersion: `2025-11-25`
- 自寫 MCP server 務必遵循此格式，否則 30 秒超時 failed

---

## Configuration

`~/.claude/workflow/config.json`:

```json
{
  "enabled": true,
  "dashboard_port": 3848,
  "stop_gate_max_blocks": 2,
  "min_files_to_block": 2,
  "remind_after_turns": 3,
  "max_reminders": 3,
  "sync_keywords": ["同步", "sync", "commit", "提交", "結束", "收工"],
  "vector_search": {
    "enabled": true,
    "service_port": 3849,
    "embedding_backend": "ollama",
    "embedding_model": "qwen3-embedding",
    "fallback_backend": "sentence-transformers",
    "fallback_model": "BAAI/bge-m3",
    "ollama_llm_model": "qwen3:1.7b",
    "search_top_k": 5,
    "search_min_score": 0.65,
    "search_timeout_ms": 2000,
    "auto_start_service": true,
    "auto_index_on_change": true
  },
  "write_gate": {
    "enabled": true,
    "auto_threshold": 0.5,
    "ask_threshold": 0.3,
    "dedup_score": 0.80,
    "skip_on_explicit_user": true
  },
  "episodic": {
    "auto_generate": true,
    "min_files": 1,
    "min_duration_seconds": 120
  },
  "session_awareness": {
    "enabled": true,
    "max_keyword_signals": 20,
    "max_triggers": 12
  },
  "cleanup": {
    "ended_ttl_ms": 60000,
    "orphan_done_ttl_ms": 1800000,
    "orphan_working_ttl_ms": 86400000
  },
  "decay": {
    "staleness_thresholds": {"[固]": 90, "[觀]": 60, "[臨]": 30},
    "auto_archive_临": true,
    "never_auto_archive_固": true
  }
}
```

### Dashboard（port 3848）

`http://127.0.0.1:3848` — 自動重新整理（5s interval）

| Tab | 內容 |
|-----|------|
| Sessions | 活躍 session 卡片（phase badge、修改檔案列表、knowledge queue） |
| Episodic | 自動生成的 episodic atoms 列表（TTL 倒數、摘要預覽） |
| Health | memory-audit 健檢報告（格式問題、晉升建議、decay 警告） |
| Tests | E2E 測試執行器（即時進度、pass/fail 明細） |
| Vector | Vector Service 狀態代理（索引統計、最後更新時間） |

---

## Hardware Requirements

### Minimum（純 keyword 模式，不需 GPU）
- Python 3.8+
- Node.js 18+

### Recommended（V2 Hybrid RECALL）
- Python 3.10+（3.14 已驗證）
- NVIDIA GPU with CUDA（embedding 加速）
- Ollama 已安裝 + `qwen3-embedding` 模型
- `pip install lancedb sentence-transformers`

### Tested On
- Windows 11 Pro, GTX 1050 Ti 4GB, Python 3.14.2
- Ollama: qwen3-embedding（embedding）+ qwen3:1.7b（LLM）
- 全量索引 18+ atoms → 380+ chunks in ~300s
- Warm search: ~386ms | Ranked search: ~400ms
- Session context injection: ~400ms（首輪 only）
- Hook 總延遲（首輪）: ~880ms（3s timeout 內）

### Quality Metrics（50-query benchmark）

| Metric | Value |
|--------|-------|
| Recall@5 | 0.96 |
| Hit@5 | 0.90 |
| MRR | 0.80 |
| Semantic-only delta | +0.80（0.05 → 0.85） |
| Intent classifier accuracy | 72% |

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| v2.0 | 2026-03-03 | Hybrid RECALL（keyword + vector semantic search）, Dashboard, 7-Phase Lifecycle |
| v2.1 | 2026-03-04 | Write Gate, Ranked Search, Conflict Detection, Delete Propagation, Audit Trail, E2E Tests |
| v2.2 | 2026-03-04 | Session Awareness, Episodic Auto-generation, Context Injection, Proactive Classification, Auto-promotion |

---

## Known Limitations & Design Trade-offs

誠實評估：

**已知不足**：
- **Token 估算粗糙** — `len(content) // 4` 只是近似值，中英文混合時偏差大
- **無回饋迴路** — 系統不知道注入的 context 是否真的被 Claude 用到了
- **First-match-wins** — 預算內先到先得，不是「最有價值的先注入」
- **Intent 分類器 72% 準確率** — rule-based，不會學習
- **冷啟動問題** — episodic atoms 需要累積，前幾個 session 的跨 session 模式偵測基本無效

**跟「真正智慧」的差距**：

真正智慧的系統會：
- 追蹤「注入了但沒被引用」的 atom → 降低其未來優先級
- 根據對話進展動態載入（不只首 prompt 決定一次）
- 用 LLM 判斷「這段 context 對當前問題有多相關」而非靠向量分數

但這些都需要更多 token 或更長延遲。v2.2 的設計哲學是**用零 token 的本地運算做到 80% 的精準度**，trade-off 是放棄了最後 20% 需要 LLM 判斷才能達到的精確度。

以 GTX 1050 Ti + 3 秒 hook timeout 的限制來說，這個 trade-off 是合理的。

---

## License

Personal use. Not published as a package.

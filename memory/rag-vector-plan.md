# Hybrid RAG 架構設計

- Scope: global
- Confidence: [固]
- Trigger: RAG, vector, 向量, embedding, 語意, semantic, LanceDB, Ollama, 本地LLM, local LLM, sentence-transformers, qwen3-embedding, bge-m3
- Last-used: 2026-03-04
- Confirmations: 2

## 知識

### 決策（已實作）

- [固] 採用 Hybrid 架構：keyword trigger（現有）優先 + vector semantic search 補充
- [固] 現有 atom trigger 系統保留不動，RAG 作為 RECALL 階段的第二層
- [固] 後端雙軌：Ollama `qwen3-embedding`（主力，MTEB 多語言 #1）+ sentence-transformers `BAAI/bge-m3`（fallback）
- [固] 向量 DB：**LanceDB**（ChromaDB 與 Python 3.14 不相容，已棄用）
- [固] 本地 LLM：`qwen3:1.7b`（qwen3:4b 在 GTX 1050 Ti 上過慢，部分 CPU offload）
- [固] Index endpoints 非同步：HTTP 立即回應，背景執行建索引

### 環境資訊

- GPU: NVIDIA GTX 1050 Ti (4GB VRAM, ~2577 MiB 可用, CUDA 6.1)
- Python: 3.14.2
- Ollama: 已安裝，qwen3-embedding + qwen3:1.7b 已拉取
- Hook timeout: UserPromptSubmit = 3 秒（vector search 必須在 ~2s 內完成）

### 架構設計

```
UserPromptSubmit (3s timeout)
├─ [1] Keyword matching (existing, ~10ms)
├─ [2] HTTP → Vector Service @ localhost:3849 (~200-400ms warm)
│       GET /search?q=<prompt>&top_k=5
│       → 返回 ranked atom names + similarity scores
├─ [3] Merge: keyword + semantic results (deduplicate)
├─ [4] Load atoms within token budget (existing)
└─ Output context
```

### Memory Vector Service（已實作）

- 位置：`~/.claude/tools/memory-vector-service/`
- 檔案：service.py, indexer.py, searcher.py, reranker.py, config.py
- 類型：Python HTTP daemon（非 MCP），port 3849
- 啟動時載入 embedding model（一次載入，warm search ~386ms）
- LanceDB 持久化存儲：`~/.claude/memory/_vectordb/`
- API: GET /search, /health, /status; POST /index, /index/incremental, /reload, /shutdown, /search/enhanced, /rerank, /extract
- 自動啟動：由 SessionStart hook 檢查並啟動
- CLI：`python tools/rag-engine.py {index|search|status|health|start|stop|extract}`

### 實測效能

| 指標 | 數值 |
|------|------|
| 全量索引（18 atoms → 377 chunks） | ~315s（首次） |
| Daemon warm search | ~386ms |
| Enhanced search（LLM query rewrite） | ~7-10s |
| Hook 內語意搜尋 | < 500ms（2s timeout） |

### 本地 LLM 功能（Phase 3，已實作）

1. **Query Rewriting** — LLM 改寫查詢擴展同義詞（`/search/enhanced`）
2. **Re-ranking** — 向量 top-10 → LLM 逐一評分 → 加權重排（`/rerank`）
3. **知識萃取** — 從文本自動萃取結構化 [固/觀/臨] 事實（`/extract`）

### 技術陷阱（已解決）

- [固] ChromaDB 依賴 pydantic v1，與 Python 3.14 不相容 → 改用 LanceDB
- [固] qwen3:4b 在 4GB VRAM GTX 1050 Ti 上 ~71% GPU / 29% CPU，推理超慢 → 改用 qwen3:1.7b
- [固] indexer.py 的 `to_pandas()` 需要 pandas → 改用 LanceDB `to_list()` / `count_rows()`
- [固] enhanced search min_score 0.65 太高（改寫查詢分數 ~0.4-0.54）→ 自動降為 min(config, 0.4)
- [固] pip 在 Git Bash 不直接可用 → 使用 `python -m pip install`

### v2.1 改進方向（已研究，待實作）

- [觀] 7 大缺陷已盤點：碎片化/TTL/衝突/噪音/intent/分層/隱私
- [觀] 新 schema 欄位：Type, TTL, Expires-at, Related, Supersedes, Privacy, Tags, Quality
- [觀] Write Gate：quality score + dedup 檢查（走 session-end 非即時路徑）
- [觀] Conflict Detection：LLM 語意比對 AGREE/CONTRADICT/EXTEND/UNRELATED
- [觀] Retrieval Ranking：0.45 semantic + 0.15 recency + 0.20 intent + 0.10 confidence + 0.10 confirmations
- [觀] Decay --enforce：[臨]>30d 自動淘汰，[觀]>60d 提醒
- [觀] Confirmations 自動遞增（guardian hook 更新 Last-used 時同步 ++）
- 完整計畫：`_AIDocs/AtomicMemory-v2.1-Plan.md`

## 行動

- 系統已實作完畢，日常使用時自動運作
- 修改 atom 後會自動觸發增量索引（PostToolUse hook）
- 手動全量重建：`python ~/.claude/tools/rag-engine.py index`
- 手動搜尋：`python ~/.claude/tools/rag-engine.py search "查詢"`
- 增強搜尋：`python ~/.claude/tools/rag-engine.py search "查詢" --enhanced`
- **v2.1 實作**：讀 `_AIDocs/AtomicMemory-v2.1-Plan.md` 按 Sprint 1→2→3 順序

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-03-04 | v2.1 缺陷研究完成：7 缺陷 + 6 系統比較 + schema + 路線圖，標為 [觀] 待實作 | session 研究 |
| 2026-03-03 | 研究完成，建立為 [觀] | session 研究分析 |
| 2026-03-03 | 全系統實作完成，晉升 [固]；ChromaDB→LanceDB、qwen3:4b→1.7b | session 實作測試 |

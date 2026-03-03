# Atom: Claude Code 記憶 V2 (CC Memory V2)

- Scope: global
- Confidence: [固]
- Source: 2026-03-04 實作完成
- Last-used: 2026-03-04
- Trigger: Claude Code 記憶 V2, memory-v2, UserPromptSubmit hook, CC atom 自動檢索, 向量搜尋 CC, 開發者分類, memory-v2 bug, hook 設定
- Privacy: public

## 知識

### 系統概述

Claude Code Memory V2 是 UserPromptSubmit hook 驅動的自動記憶檢索系統。每次使用者送出訊息時，自動搜尋相關 atom 並注入 AI context。

### 架構：三階段管線

```
stdin (prompt JSON) → index.js
  ├─ Stage 1: Gate (intent-classifier.js)
  │   確定性快篩(跳過問候) + LLM 分類(5大開發者類別)
  ├─ Stage 2: 雙通道搜尋
  │   A4: trigger-matcher.js (keyword) — 永遠執行
  │   A16: vector-indexer.js (LanceDB) — 需 Ollama
  └─ Stage 3: fusion-ranker.js
      加權合併 + 類別對齊 + 信心度調整 → top-3
→ stdout (hookSpecificOutput.additionalContext)
```

### 檔案結構

```
.claude/scripts/memory-v2/
  index.js              ← Hook 進入點 (~230 行)
  config.json           ← 配置（來源、權重、模型）
  lib/
    atom-parser.js      ← 解析 atom .md 檔（from OpenClaw, +\r\n fix）
    trigger-matcher.js  ← A4 關鍵詞匹配（from OpenClaw, 0 改動）
    vector-indexer.js   ← LanceDB 向量搜尋（from OpenClaw, +多來源+路徑）
    fusion-ranker.js    ← 融合排序（from OpenClaw, 0 改動）
    intent-classifier.js← Gate 分類器（NEW, 開發者 5 分類 prompt）
    taxonomy.js         ← 分類系統（from OpenClaw, +路徑改動）
  taxonomy/
    categories.json     ← 開發者五分類定義
    unclassified.jsonl  ← 低信心查詢日誌（自動產生）
  vector-store/
    cc-atoms.lance/     ← LanceDB 向量資料（自動產生）
  scripts/
    build-index.js      ← 手動全量/增量建索引
    test-e2e.js         ← 端對端測試（8 cases）
  README.md
  INSTALL-FOR-OTHER-AI.md
```

### 記憶來源（config.json atomSources）

| ID | 路徑 | 跳過 |
|----|------|------|
| cc-memory | `C:/Users/holyl/.claude/projects/e--OpenClawWorkSpace/memory/` | MEMORY.md |
| openclaw-atoms | `E:/OpenClawWorkSpace/.openclaw/workspace/atoms/` | _identity-map, _pairing, _registry, _active |

### 開發者五分類（非人事時地物）

| 類別 | code | 子分類 |
|------|------|--------|
| 技術 | tech | debug, api, pattern |
| 架構 | arch | structure, design, integration |
| 運維 | ops | config, deploy, infra |
| 工作流 | flow | preference, process, tool |
| 領域 | domain | openclaw, desktop, consciousness |

### 降級鏈

1. **完整 V2**: Ollama + LanceDB → Gate + A4 + Vector + Fusion
2. **無 Ollama**: 跳過 Gate + Vector → 純 A4 keyword 匹配
3. **無索引**: Gate + A4（首次自動背景建索引）
4. **全掛**: exit 0 → MEMORY.md always-loaded 照常

### Hook 設定

在 `C:\Users\holyl\.claude\settings.json` 全域設定：
```json
"UserPromptSubmit": [{
  "hooks": [{
    "type": "command",
    "command": "node E:/OpenClawWorkSpace/.claude/scripts/memory-v2/index.js",
    "timeout": 15
  }]
}]
```

### 關鍵修復（2026-03-04 實作過程中）

| 代號 | 問題 | 修復 |
|------|------|------|
| \r\n | Windows 行尾導致 metadata 解析全失敗 | `split(/\r?\n/)` |
| C2 | readStdin 競態（readableEnded 過早） | `fs.readFileSync(0, 'utf8')` |
| I8 | isOllamaAvailable 重複呼叫 2 次 | 快取結果，只查一次 |
| I2 | tokenBudget 1200 太小（3 atoms 裝不下） | 改 3600 + per-atom budget |
| M11 | 背景建索引無限重啟 | sentinel 檔 + 5 分鐘冷卻 |
| blocking | 首次建索引 28s > 15s timeout | 改為 detached background spawn |

### 共用基礎設施

- Ollama: `http://127.0.0.1:11434`（qwen3-embedding:0.6b + qwen3:1.7b）
- LanceDB: `require("E:/OpenClawWorkSpace/.openclaw/workspace/node_modules/@lancedb/lancedb")`
- 嵌入維度: 1024（qwen3-embedding:0.6b）

## 行動

- 修改 memory-v2 任何檔案後：執行 `node .claude/scripts/memory-v2/scripts/test-e2e.js` 驗證
- 新增/修改 atom 檔後：執行 `node .claude/scripts/memory-v2/scripts/build-index.js --incremental` 更新索引
- 分類器不準時：檢查 `taxonomy/unclassified.jsonl`，據此擴充 `categories.json`
- Hook 無反應時：檢查 `C:\Users\holyl\.claude\settings.json` 的 UserPromptSubmit 設定
- Ollama 掛了：系統自動降級到 A4-only，不需人工介入
- 向量索引損壞：刪除 `vector-store/cc-atoms.lance/` + `vector-store/.building`，重建索引

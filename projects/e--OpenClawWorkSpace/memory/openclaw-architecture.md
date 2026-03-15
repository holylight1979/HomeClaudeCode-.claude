# Atom: OpenClaw 完整架構

- Scope: global
- Confidence: [固]
- Source: 2026-03-05 V2.3 升級全面掃描
- Last-used: 2026-03-15
- Confirmations: 5
- Trigger: OpenClaw 架構, 運作流程, Gateway 管線, preprocessor 管線, 演算法, 降級, Token 流向, 服務拓撲, 系統概覽
- Privacy: public

## 知識

### 服務拓撲

```
使用者 ─→ Discord WebSocket / LINE ngrok webhook
         ↓
   Gateway (port 18789, Node.js)
     ├─ controlUi: /ui (basePath="/ui")
     ├─ Browser control: port 18791 (CDP: 18792)
     ├─ Health: /health → {"ok":true}
     └─ Plugins: discord, line
         ↓
   Preprocessor (message:before hook)
     ├─ A15 Gate → need_memory?
     │   ├─ no → skip (省 token)
     │   └─ yes → A4 trigger ∥ A16 vector → A17 fusion
     └─ A20 behavioral observer (靜默)
         ↓
   LLM: OpenAI Codex OAuth (gpt-5.3-codex)
         ↓
   回應 → Discord/LINE
```

### 18 演算法模組（preprocessor/lib/）

| ID | 模組 | 類型 | 用途 |
|----|------|------|------|
| A1 | identity-resolver | 確定性 | _identity-map.md 解析，平台ID→人員映射 |
| A4 | trigger-matcher | 確定性 | 關鍵詞匹配，score=matched/total，minScore=0.3 |
| A6 | decay-checker | 確定性 | 過期檢測：[臨]30d歸檔、[觀]確認、[固]列審 |
| A7 | staging-evaluator | 確定性 | staging 晉升：occ≥3→promote，>90d+<3→delete |
| A8 | candidate-matcher | 確定性 | 跨平台人員匹配：name×0.20+hours×0.20+topics×0.25 |
| A9 | candidate-evaluator | 確定性 | 候選人評估：interactions≥3+span≥2d→promote |
| A13 | changelog-rotator | 確定性 | CHANGELOG 滾動：>8筆→移至 ARCHIVE |
| A14 | index.js | 編排 | heartbeat 編排，呼叫所有模組+產報表 |
| A15 | intent-classifier | 混合 | Gate 分類：確定性快篩+qwen3:1.7b 五大分類 |
| A16 | vector-indexer | 混合 | LanceDB 向量搜尋：qwen3-embedding:0.6b, 1024維, hybrid keyword boost (+0.1), self-healing cache |
| A17 | fusion-ranker | 確定性 | 融合：0.5×A4+0.5×vector+confidence+category |
| A18 | taxonomy.js | 確定性 | 分類載入+noMemory快篩+categoryAlignment |
| A20 | behavioral-observer | 確定性 | 每訊息特徵提取：字數/句長/問句比/指令比/emoji |
| A21 | session-profiler | 混合 | 每10則合成trait標籤：qwen3:0.6b+信心度計算 |
| A22 | behavior-matcher | 確定性 | 跨session snapshot比對，閾值≥85%→pending |
| — | direct-response-checker | 確定性 | 高信心+短問→直接回應指令（score≥0.7+[固]+≤100字） |
| — | atom-parser | 確定性 | .md metadata 解析（title/confidence/trigger/features） |
| — | report-writer | 確定性 | 彙整報表：decay/staging/candidate/system-health |

### 三 Hook 記憶管線

| Hook | 事件 | 方向 | 策略 | 頻率 |
|------|------|------|------|------|
| atom-context-injector | agent:bootstrap | Read | WHO（身份驅動） | 每 session 一次 |
| memory-retriever | message:before | Read | WHAT（內容驅動） | 每訊息 |
| memory-writer | message:sent | Write | 回應萃取（確定性） | 每回覆 |

memory-writer 為安全網：偵測記憶信號但 agent 未自行 fs_write 時，自動建 staging entry。
agent 也可透過 fs_write 直接寫入 atoms/（由 SKILL.md Memory Write Protocol 指導）。

### 降級鏈（永不中斷服務）

1. **完整模式**: Gate(A15) + A4 + A16(vector) + A17(fusion) + A20(observer)
2. **無 Ollama**: 跳過 Gate + Vector → 純 A4 keyword 匹配（V1 行為）
3. **無 LanceDB**: A4 only
4. **全掛**: exit 0 → MEMORY.md always-loaded 照常

### 本地 LLM（共用 Ollama）

| 模型 | 用途 | VRAM |
|------|------|------|
| qwen3:1.7b | A15 intent 分類（需 /no_think tag） | ~1.0GB |
| qwen3-embedding:0.6b | A16 向量嵌入（1024維） | ~0.4GB |
| qwen3:0.6b | A21 trait 合成 + reranker | ~0.4GB |

### V2.1 Fusion 公式

```
fusionScore = 0.5×a4 + 0.5×vector
  + confidenceBoost ([固]+0.05 / [臨]-0.03)
  + categoryAlignment (+0.15)
  + crossChannelBonus (+0.05, 雙通道同時命中)
```

maxAtoms=3, tokenBudget=800

## 行動

- 理解 OpenClaw 架構時：參照本 atom 的服務拓撲和演算法表
- 修改 preprocessor 前：確認是哪個 A# 模組，閱讀原始碼
- 降級問題排查：依降級鏈由下往上確認（Ollama→LanceDB→Gate→Full）
- VRAM 不足時：可停用 reranker（省0.4GB），或降級到 A4-only

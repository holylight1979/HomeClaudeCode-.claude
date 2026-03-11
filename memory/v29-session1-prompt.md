# V2.9 Session 1 續接 Prompt

複製以下內容到新 Session：

---

## 任務：V2.9 記憶檢索強化 — Session 1/3

請先進入 Plan Mode，然後執行以下工作。

### 背景
上一個 session 完成了 V2.9 設計規格，存於 `~/.claude/memory/v3-design-spec.md`。
跨領域研究洞見存於 `~/.claude/memory/v3-research-insights.md`。

### Session 1 目標（3 項）

**1. 刪除冗餘記憶**
- 刪除 `~/.claude/projects/c--Projects-sgi-server/memory/` 目錄
- 保留 `c--Projects-sgi-server/` 的 session logs（.jsonl）
- 原因：c--Projects 已是完全超集，sgi-server 的 atom 都是舊版子集

**2. Project-Aliases 實作**
- 在 `c--Projects/memory/MEMORY.md` 加 `> Project-Aliases: sgi, sgi_server, sgi-server, sgi_client, 遊戲後端`
- 修改 `~/.claude/hooks/workflow-guardian.py` 的 `parse_memory_index()` 解析 aliases
- 修改跨專案掃描邏輯：alias 命中 → 注入該專案 MEMORY.md 全文
- 關鍵程式碼位置：workflow-guardian.py L805-L828（Cross-project atom discovery）

**3. Blind-Spot Reporter**
- 當 keyword + vector + alias 全部找不到 atom 時
- 注入 `[Guardian:BlindSpot] 未找到與 "..." 相關的記憶 atom。`

### 驗證
- 從非 sgi CWD 問 "sgi 的架構" → 確認 atoms 被找到
- 問完全無 atom 的主題 → 確認 blind-spot 報告出現
- 正常流程不受影響

### 參考
- 設計規格：`~/.claude/memory/v3-design-spec.md`
- 現行 hook：`~/.claude/hooks/workflow-guardian.py`
- 現行 SPEC：`~/.claude/memory/SPEC_Atomic_Memory_System.md`
